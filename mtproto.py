#!/usr/bin/env python3
import subprocess
import os
import secrets
import tempfile
from pathlib import Path

def get_public_ip():
    return subprocess.run(['curl', '-s', 'https://checkip.amazonaws.com'], 
                         capture_output=True, text=True).stdout.strip()

def main():
    port = os.getenv('PROXY_PORT', '8443')
    public_ip = get_public_ip()
    secret = secrets.token_hex(16)
    
    creds = f"Server IP: {public_ip}\nPort: {port}\nSecret: {secret}\n"
    print(creds)
    
    gh_token = os.getenv('GH_TOKEN')
    repo_url = os.getenv('GITHUB_REPO')
    
    if not gh_token or not repo_url:
        print("Missing GH_TOKEN or GITHUB_REPO")
        exit(1)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = Path(tmpdir) / "repo"
        repo.mkdir()
        
        env = os.environ.copy()
        clone_url = repo_url.replace('https://', f'https://x-access-token:{gh_token}@')
        
        subprocess.run(['git', 'clone', clone_url, str(repo)], env=env, capture_output=True, check=True)
        
        (repo / "mtproto_credentials.txt").write_text(creds)
        
        subprocess.run(['git', 'config', 'user.email', 'bot@render'], cwd=repo, check=True)
        subprocess.run(['git', 'config', 'user.name', 'Bot'], cwd=repo, check=True)
        subprocess.run(['git', 'add', 'mtproto_credentials.txt'], cwd=repo, check=True)
        subprocess.run(['git', 'commit', '-m', 'MTProto creds'], cwd=repo, check=True, capture_output=True)
        subprocess.run(['git', 'push'], cwd=repo, env=env, check=True, capture_output=True)
        
        print("✓ Pushed to GitHub")

if __name__ == '__main__':
    main()