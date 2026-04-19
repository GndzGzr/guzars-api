from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
import hmac
import hashlib
import requests
import logging
from django.conf import settings
from django.http import HttpResponseForbidden, JsonResponse
from notes.services import NoteIngestor
import datetime
from django.utils import timezone
from notes.models import Note
from notes.utils import is_path_allowed

logger = logging.getLogger(__name__)

class HelloView(APIView):
    """
    A simple protected endpoint to verify token auth is working.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            'message': f'Hello, {request.user.username}! Your DRF API is working.',
        })

class GitHubWebhookView(APIView):
    """
    Endpoint that accepts GitHub Webhook 'push' events.
    Authenticates requests via HMAC SHA256 signature rather than standard DRF tokens.
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        # 1. Verify Signature
        signature_header = request.headers.get("X-Hub-Signature-256")
        if not signature_header:
            return HttpResponseForbidden("Missing signature")
            
        secret = getattr(settings, 'GITHUB_WEBHOOK_SECRET', '').encode('utf-8')
        expected_signature = "sha256=" + hmac.new(
            secret, request.body, hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(expected_signature, signature_header):
            return HttpResponseForbidden("Invalid signature")

        payload = request.data
        
        # Determine event type
        event_name = request.headers.get("X-GitHub-Event", "push")
        if event_name != "push":
            return JsonResponse({"status": "ignored", "reason": f"Ignoring event: {event_name}"})

        commits = payload.get("commits", [])
        if not commits:
            return JsonResponse({"status": "ignored", "reason": "No commits found in push payload"})

        repo_full_name = payload.get("repository", {}).get("full_name", "")
        branch = payload.get("ref", "").split("/")[-1]
        
        ingestor = NoteIngestor()

        # 2. Iterate incoming commits
        for commit in commits:
            commit_timestamp_str = commit.get("timestamp", "")
            commit_timestamp = timezone.now()
            if commit_timestamp_str:
                try:
                    commit_timestamp = datetime.datetime.fromisoformat(commit_timestamp_str.replace('Z', '+00:00'))
                except ValueError:
                    pass
            
            # Process Removed Files
            for filepath in commit.get("removed", []):
                if filepath.endswith(".md") and is_path_allowed(filepath):
                    slug = filepath.split("/")[-1].replace(".md", "")
                    Note.objects.filter(slug=slug).delete()

            # Process Added/Modified Files
            upsert_files = commit.get("added", []) + commit.get("modified", [])
            for filepath in upsert_files:
                if filepath.endswith(".md") and is_path_allowed(filepath):
                    self._fetch_and_ingest(repo_full_name, branch, filepath, ingestor, commit_timestamp)

        return JsonResponse({"status": "success"})

    def _fetch_and_ingest(self, repo_full_name, branch, filepath, ingestor, timestamp):
        github_token = getattr(settings, 'GITHUB_PERSONAL_ACCESS_TOKEN', '')
        
        # When fetching private repos, passing the Accept header and Authorization Token 
        # fetches the file securely natively.
        raw_url = f"https://api.github.com/repos/{repo_full_name}/contents/{filepath}?ref={branch}"
        headers = {'Accept': "application/vnd.github.v3.raw"}
        
        if github_token:
            headers['Authorization'] = f"token {github_token}"
            
        resp = requests.get(raw_url, headers=headers)
        if resp.status_code == 200:
            filename = filepath.split("/")[-1]
            raw_content = resp.text
            note, created = ingestor.ingest_note(filename, raw_content, updated_at=timestamp)
            if created and note:
                note.created_at = timestamp
                note.save(update_fields=['created_at'])
        else:
            logger.error(f"Failed to fetch {filepath}. Status: {resp.status_code}")

class AssetProxyView(APIView):
    """
    Accepts a target generic or explicit relative file string, e.g., ?file=image.png
    And either dynamically proxies it by making a raw GitHub API request,
    or redirects the client straight to it.
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        filename = request.query_params.get('file')
        if not filename:
            return JsonResponse({'error': 'No file parameter provided.'}, status=400)
            
        import urllib.parse
        decoded_filename = urllib.parse.unquote(filename).lstrip('/')

        # For a truly Headless CMS relying on GitHub, we can leverage 
        # GitHub's raw content CDN without parsing giant tree hashes on the fly.
        # Alternatively, the React frontend can map to its own public asset folder.
        # This proxy view currently just constructs the standard raw redirect.
        
        # We need the repo info from settings
        # In a generic setup, one could hit the GitHub Search API (`filename:XYZ repo:X`)
        # Wait, the best strategy if you don't know the folder path is to return
        # a redirect to your github raw assuming everything is in an 'assets' folder,
        # or have the system track asset paths in the DB.
        
        return JsonResponse({
            'file': decoded_filename,
            'message': 'Asset mapping endpoint configured successfully.',
            'redirect_target_example': f'https://raw.githubusercontent.com/user/repo/main/{decoded_filename}'
        }, status=200)

from .models import VaultConfiguration
from .serializers import VaultConfigurationSerializer
from drf_spectacular.utils import extend_schema

class VaultConfigurationView(APIView):
    """
    CMS Endpoint to retrieve or update the vault synchronization rules.
    Used by the Admin frontend to change included/excluded paths dynamically.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=VaultConfigurationSerializer)
    def get(self, request):
        config = VaultConfiguration.load()
        serializer = VaultConfigurationSerializer(config)
        return Response(serializer.data)

    @extend_schema(request=VaultConfigurationSerializer, responses=VaultConfigurationSerializer)
    def put(self, request):
        config = VaultConfiguration.load()
        serializer = VaultConfigurationSerializer(config, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

import os
from django.http import HttpResponse

class APIIndexView(APIView):
    """
    Renders the dynamic 'How-To' Markdown documentation natively on the base API route.
    By default reads from the main project docs.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        doc_param = request.query_params.get('doc', 'project-guide')
        valid_docs = ['project-guide', 'frontend-guide', 'obsidian-frontmatter-guide', 'roadmap']
        
        if doc_param not in valid_docs:
            doc_param = 'project-guide'

        file_path = os.path.join(settings.BASE_DIR, "docs", f"{doc_param}.md")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except FileNotFoundError:
            content = "# Documentation not found\n\nThe requested documentation file could not be found."

        # simple HTML wrapping
        from notes.parsers import render_markdown_to_html
        try:
             html_content = render_markdown_to_html(content)
        except Exception:
             html_content = f"<pre>{content}</pre>"

        html_page = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>API Documentation - {doc_param}</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: -apple-system, system-ui, sans-serif; max-width: 900px; margin: 40px auto; line-height: 1.6; padding: 0 20px; }}
                nav {{ margin-bottom: 20px; padding: 10px; background: #f0f0f0; border-radius: 5px; }}
                nav a {{ margin-right: 15px; color: #0366d6; text-decoration: none; font-weight: 500; }}
                nav a:hover {{ text-decoration: underline; }}
                pre {{ background: #f6f8fa; padding: 16px; border-radius: 6px; overflow-x: auto; }}
                code {{ font-family: ui-monospace, SFMono-Regular, monospace; background: #f0f0f0; padding: 2px 4px; border-radius: 3px; font-size: 85%; }}
                img {{ max-width: 100%; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; }}
            </style>
        </head>
        <body>
            <nav>
                <span>Docs:</span>
                <a href="?doc=project-guide">API Overview</a>
                <a href="?doc=frontend-guide">Frontend Integration</a>
                <a href="?doc=obsidian-frontmatter-guide">Frontmatter Guide</a>
                <a href="?doc=roadmap">Roadmap</a>
            </nav>
            {html_content}
        </body>
        </html>
        """
        return HttpResponse(html_page, content_type="text/html")

from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from .serializers import UserSignupSerializer

class SignUpView(APIView):
    """
    Endpoint for new user registration.
    Returns the user's auth token upon successful creation.
    """
    permission_classes = [AllowAny]

    @extend_schema(request=UserSignupSerializer)
    def post(self, request):
        serializer = UserSignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                "message": "User created successfully.",
                "token": token.key,
                "username": user.username
            }, status=201)
        return Response(serializer.errors, status=400)
