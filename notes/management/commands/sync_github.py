import requests
import logging
import datetime
from django.utils import timezone
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from notes.services import NoteIngestor
import base64
from notes.utils import is_path_allowed

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Bulk synchronizes all Markdown files from a target GitHub repository into the local database.'

    def add_arguments(self, parser):
        parser.add_argument('repo_full_name', type=str, help='The full name of the repository (e.g. username/repo)')
        parser.add_argument('--branch', type=str, default='main', help='The branch to read from (default: main)')

    def handle(self, *args, **kwargs):
        repo_full_name = kwargs['repo_full_name']
        branch = kwargs['branch']
        
        # Clean up URL if the user provides a full link instead of owner/repo
        repo_full_name = repo_full_name.replace('https://github.com/', '').replace('http://github.com/', '').strip('/')
        if repo_full_name.endswith('.git'):
            repo_full_name = repo_full_name[:-4]
            
        github_token = getattr(settings, 'GITHUB_PERSONAL_ACCESS_TOKEN', '')

        self.stdout.write(self.style.SUCCESS(f"Starting bulk sync for {repo_full_name} on branch '{branch}'..."))

        headers = {}
        if github_token:
            headers['Authorization'] = f"token {github_token}"

        # 1. Fetch the recursive file tree for the repository branch
        # This is massively more efficient than making a request for every single directory
        tree_url = f"https://api.github.com/repos/{repo_full_name}/git/trees/{branch}?recursive=1"
        resp = requests.get(tree_url, headers=headers)
        
        if resp.status_code != 200:
            self.stdout.write(self.style.ERROR(f"Failed to fetch repository tree. Status: {resp.status_code}"))
            return

        tree_data = resp.json().get('tree', [])
        
        from api.models import VaultConfiguration
        from notes.utils import load_local_config
        try:
            config = load_local_config()
            if not config:
                config = VaultConfiguration.load()
        except:
            config = None

        # 2. Filter out exclusively for markdown files and allowed paths
        md_files = [
            item for item in tree_data 
            if item.get('type') == 'blob' 
            and item.get('path', '').endswith('.md')
            and is_path_allowed(item.get('path', ''), config=config)
        ]
        
        self.stdout.write(self.style.SUCCESS(f"Found {len(md_files)} markdown files. Beginning ingestion..."))

        ingestor = NoteIngestor()
        success_count = 0
        error_count = 0

        # 3. Pull raw content and process each
        for file_item in md_files:
            filepath = file_item['path']
            filename = filepath.split('/')[-1]
            
            # Using the raw Accept header to bypass rate limits on binary download
            raw_url = f"https://api.github.com/repos/{repo_full_name}/contents/{filepath}?ref={branch}"
            file_headers = {'Accept': "application/vnd.github.v3.raw"}
            if github_token:
                file_headers['Authorization'] = f"token {github_token}"
                
            file_resp = requests.get(raw_url, headers=file_headers)
            
            if file_resp.status_code == 200:
                raw_content = file_resp.text
                
                # Fetch latest commit timestamp for this specific file
                commit_url = f"https://api.github.com/repos/{repo_full_name}/commits?path={filepath}&sha={branch}&per_page=1"
                commit_resp = requests.get(commit_url, headers=headers)
                
                timestamp = timezone.now()
                if commit_resp.status_code == 200:
                    commits_data = commit_resp.json()
                    if commits_data:
                        timestamp_str = commits_data[0].get("commit", {}).get("committer", {}).get("date", "")
                        if timestamp_str:
                            try:
                                timestamp = datetime.datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                            except ValueError:
                                pass

                try:
                    note, created = ingestor.ingest_note(filename, raw_content, updated_at=timestamp)
                    if created and note:
                        note.created_at = timestamp
                        note.save(update_fields=['created_at'])
                        
                    status_str = "Created" if created else "Updated"
                    self.stdout.write(f"[{status_str}] {filename}")
                    success_count += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Failed to ingest {filename}: {e}"))
                    error_count += 1
            else:
                self.stdout.write(self.style.ERROR(f"Failed to download {filepath} (Status: {file_resp.status_code})"))
                error_count += 1

        self.stdout.write(self.style.SUCCESS(f"\nSync complete! Successfully processed: {success_count}, Errors: {error_count}"))
