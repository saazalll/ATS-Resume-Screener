import requests
import re
import functools
from typing import Dict, Optional, List, Tuple

def extract_github_username(text: str) -> Optional[str]:
    """
    Extract a GitHub username from raw text using regex.
    Matches formats like github.com/username or https://github.com/username
    """
    # Look for github.com/ followed by alphanumeric characters and hyphens
    match = re.search(r'github\.com/([a-zA-Z0-9-]+)', text, re.IGNORECASE)
    if match:
        return match.group(1)
    return None

@functools.lru_cache(maxsize=128)
def fetch_github_languages(username: str, token: Optional[str] = None) -> Tuple[str]:
    """
    Fetch public repositories for the given username and return a list
    of unique primary languages used across those repositories.
    Caches the results to avoid hitting rate limits on Bulk Analysis.
    Excludes forked repositories as per requirements.
    """
    headers = {'Accept': 'application/vnd.github.v3+json'}
    if token:
        headers['Authorization'] = f'token {token}'
        
    try:
        response = requests.get(
            f'https://api.github.com/users/{username}/repos?sort=updated&per_page=15',
            headers=headers,
            timeout=5
        )
        
        if response.status_code != 200:
            return tuple()
            
        repos = response.json()
        languages = set()
        
        for repo in repos:
            if repo.get('fork', False):
                continue
            lang = repo.get('language')
            if lang:
                languages.add(lang.lower())
                
        return tuple(languages)
    except Exception as e:
        print(f"Error fetching GitHub profile for {username}: {e}")
        return tuple()
