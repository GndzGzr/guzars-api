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
            # Process Removed Files
            for filepath in commit.get("removed", []):
                if filepath.endswith(".md") and is_path_allowed(filepath):
                    slug = filepath.split("/")[-1].replace(".md", "")
                    Note.objects.filter(slug=slug).delete()

            # Process Added/Modified Files
            upsert_files = commit.get("added", []) + commit.get("modified", [])
            for filepath in upsert_files:
                if filepath.endswith(".md") and is_path_allowed(filepath):
                    self._fetch_and_ingest(repo_full_name, branch, filepath, ingestor)

        return JsonResponse({"status": "success"})

    def _fetch_and_ingest(self, repo_full_name, branch, filepath, ingestor):
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
            note, created = ingestor.ingest_note(filename, raw_content)
        else:
            logger.error(f"Failed to fetch {filepath}. Status: {resp.status_code}")
