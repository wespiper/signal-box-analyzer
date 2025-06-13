"""
GitHub integration service for fetching repository content
Time estimate: 3 hours
"""

import httpx
import base64
import re
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse
import asyncio
import logging

logger = logging.getLogger(__name__)


class GitHubService:
    """Service for interacting with GitHub repositories"""
    
    def __init__(self, github_token: Optional[str] = None):
        """
        Initialize GitHub service
        
        Args:
            github_token: GitHub personal access token (optional, increases rate limits)
        """
        self.github_token = github_token
        self.base_url = "https://api.github.com"
        
        # File extensions we're interested in
        self.relevant_extensions = {
            '.py',   # Python files
            '.js',   # JavaScript files  
            '.ts',   # TypeScript files
            '.jsx',  # React JSX files
            '.tsx',  # React TSX files
            '.md',   # Markdown files (for documentation)
            '.yml',  # YAML config files
            '.yaml', # YAML config files
            '.json', # JSON config files
            '.env',  # Environment files
            '.txt',  # Text files
        }
        
        # Directories to skip
        self.skip_directories = {
            '.git', '__pycache__', 'node_modules', '.venv', 'venv',
            '.pytest_cache', '.mypy_cache', 'dist', 'build',
            '.next', '.nuxt', 'coverage', '.coverage'
        }
        
        # Files to always include (even if not in relevant_extensions)
        self.important_files = {
            'requirements.txt', 'package.json', 'pyproject.toml', 
            'setup.py', 'Dockerfile', 'docker-compose.yml',
            'config.yaml', 'config.yml', 'OAI_CONFIG_LIST'
        }
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for GitHub API requests"""
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'Signal-Box-Analyzer/1.0'
        }
        
        if self.github_token:
            headers['Authorization'] = f'token {self.github_token}'
        
        return headers
    
    def _parse_github_url(self, url: str) -> tuple[str, str]:
        """
        Parse GitHub URL to extract owner and repository name
        
        Args:
            url: GitHub repository URL
            
        Returns:
            Tuple of (owner, repo_name)
        """
        # Remove .git suffix if present
        url = url.rstrip('.git')
        
        # Parse URL
        parsed = urlparse(url)
        
        if parsed.netloc != 'github.com':
            raise ValueError("URL must be a GitHub repository")
        
        # Extract path components
        path_parts = parsed.path.strip('/').split('/')
        
        if len(path_parts) < 2:
            raise ValueError("Invalid GitHub repository URL")
        
        owner = path_parts[0]
        repo = path_parts[1]
        
        return owner, repo
    
    def _should_include_file(self, file_path: str) -> bool:
        """
        Determine if a file should be included in analysis
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if file should be included
        """
        # Get file name and extension
        file_name = file_path.split('/')[-1]
        file_ext = '.' + file_name.split('.')[-1] if '.' in file_name else ''
        
        # Always include important files
        if file_name in self.important_files:
            return True
        
        # Check if in relevant extensions
        if file_ext in self.relevant_extensions:
            return True
        
        # Skip large files that are likely not code
        if file_ext in {'.jpg', '.jpeg', '.png', '.gif', '.svg', '.ico', 
                       '.pdf', '.zip', '.tar', '.gz', '.bz2', '.xz'}:
            return False
        
        return False
    
    def _should_skip_directory(self, dir_path: str) -> bool:
        """
        Determine if a directory should be skipped
        
        Args:
            dir_path: Path to the directory
            
        Returns:
            True if directory should be skipped
        """
        dir_name = dir_path.split('/')[-1]
        return dir_name in self.skip_directories
    
    async def _fetch_with_retry(self, url: str, max_retries: int = 3) -> Dict[str, Any]:
        """
        Fetch URL with retry logic for rate limiting
        
        Args:
            url: URL to fetch
            max_retries: Maximum number of retries
            
        Returns:
            JSON response
        """
        headers = self._get_headers()
        
        for attempt in range(max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.get(url, headers=headers)
                    
                    if response.status_code == 200:
                        return response.json()
                    
                    elif response.status_code == 403:
                        # Rate limit exceeded
                        if attempt < max_retries:
                            wait_time = 60 * (attempt + 1)  # Exponential backoff
                            logger.warning(f"Rate limited, waiting {wait_time}s before retry {attempt + 1}")
                            await asyncio.sleep(wait_time)
                            continue
                        else:
                            raise Exception("GitHub API rate limit exceeded. Try again later or provide a GitHub token.")
                    
                    elif response.status_code == 404:
                        raise Exception("Repository not found or not accessible")
                    
                    else:
                        response.raise_for_status()
                        
            except httpx.TimeoutException:
                if attempt < max_retries:
                    logger.warning(f"Request timeout, retrying... (attempt {attempt + 1})")
                    await asyncio.sleep(5)
                    continue
                else:
                    raise Exception("Request timeout after multiple retries")
            
            except httpx.RequestError as e:
                if attempt < max_retries:
                    logger.warning(f"Request error: {e}, retrying... (attempt {attempt + 1})")
                    await asyncio.sleep(5)
                    continue
                else:
                    raise Exception(f"Failed to connect to GitHub: {e}")
        
        raise Exception("Maximum retries exceeded")
    
    async def fetch_repository_tree(self, owner: str, repo: str, branch: str = "main") -> List[Dict[str, Any]]:
        """
        Fetch the repository file tree
        
        Args:
            owner: Repository owner
            repo: Repository name  
            branch: Branch name (defaults to main)
            
        Returns:
            List of file/directory information
        """
        # Try main branch first, then master
        for branch_name in [branch, "master", "main"]:
            try:
                url = f"{self.base_url}/repos/{owner}/{repo}/git/trees/{branch_name}?recursive=1"
                tree_data = await self._fetch_with_retry(url)
                return tree_data.get('tree', [])
            
            except Exception as e:
                if "not found" in str(e).lower():
                    continue
                else:
                    raise
        
        raise Exception(f"Could not find any of the following branches: {branch}, main, master")
    
    async def fetch_file_content(self, owner: str, repo: str, file_path: str, branch: str = "main") -> str:
        """
        Fetch content of a specific file
        
        Args:
            owner: Repository owner
            repo: Repository name
            file_path: Path to the file
            branch: Branch name
            
        Returns:
            File content as string
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/contents/{file_path}?ref={branch}"
        
        try:
            content_data = await self._fetch_with_retry(url)
            
            # GitHub API returns base64 encoded content
            if content_data.get('encoding') == 'base64':
                content_bytes = base64.b64decode(content_data['content'])
                
                # Try to decode as UTF-8, fallback to latin-1 if needed
                try:
                    return content_bytes.decode('utf-8')
                except UnicodeDecodeError:
                    try:
                        return content_bytes.decode('latin-1')
                    except UnicodeDecodeError:
                        # Skip files that can't be decoded
                        logger.warning(f"Could not decode file: {file_path}")
                        return ""
            
            else:
                # Direct content (for small files)
                return content_data.get('content', '')
                
        except Exception as e:
            logger.warning(f"Failed to fetch file {file_path}: {e}")
            return ""
    
    async def fetch_repository(self, github_url: str, max_files: int = 100) -> Dict[str, Any]:
        """
        Fetch repository content for analysis
        
        Args:
            github_url: GitHub repository URL
            max_files: Maximum number of files to fetch
            
        Returns:
            Dictionary with repository information and file contents
        """
        # Parse URL
        owner, repo = self._parse_github_url(github_url)
        
        logger.info(f"Fetching repository: {owner}/{repo}")
        
        # Get repository info
        repo_url = f"{self.base_url}/repos/{owner}/{repo}"
        repo_info = await self._fetch_with_retry(repo_url)
        
        # Get file tree
        tree = await self.fetch_repository_tree(owner, repo)
        
        # Filter files we want to analyze
        relevant_files = []
        
        for item in tree:
            if item['type'] == 'blob':  # It's a file
                file_path = item['path']
                
                # Skip files in excluded directories
                if any(self._should_skip_directory(part) for part in file_path.split('/')):
                    continue
                
                # Include relevant files
                if self._should_include_file(file_path):
                    relevant_files.append({
                        'path': file_path,
                        'size': item.get('size', 0),
                        'url': item.get('url', '')
                    })
        
        # Sort by relevance (Python files first, then by size)
        relevant_files.sort(key=lambda x: (
            0 if x['path'].endswith('.py') else 1,  # Python files first
            -x['size']  # Larger files first
        ))
        
        # Limit number of files
        if len(relevant_files) > max_files:
            logger.warning(f"Repository has {len(relevant_files)} relevant files, limiting to {max_files}")
            relevant_files = relevant_files[:max_files]
        
        # Fetch file contents
        files = {}
        branch = repo_info.get('default_branch', 'main')
        
        # Use semaphore to limit concurrent requests
        semaphore = asyncio.Semaphore(5)  # Max 5 concurrent requests
        
        async def fetch_single_file(file_info):
            async with semaphore:
                content = await self.fetch_file_content(owner, repo, file_info['path'], branch)
                if content:  # Only include non-empty files
                    files[file_info['path']] = content
        
        # Fetch all files concurrently
        tasks = [fetch_single_file(file_info) for file_info in relevant_files]
        await asyncio.gather(*tasks, return_exceptions=True)
        
        logger.info(f"Successfully fetched {len(files)} files from {owner}/{repo}")
        
        return {
            'repository': {
                'owner': owner,
                'name': repo,
                'full_name': repo_info.get('full_name'),
                'description': repo_info.get('description'),
                'language': repo_info.get('language'),
                'size': repo_info.get('size'),
                'stars': repo_info.get('stargazers_count'),
                'forks': repo_info.get('forks_count'),
                'default_branch': repo_info.get('default_branch'),
                'url': repo_info.get('html_url')
            },
            'files': files,
            'total_files_analyzed': len(files),
            'total_files_found': len(relevant_files)
        }
    
    async def validate_repository_access(self, github_url: str) -> bool:
        """
        Validate that we can access the repository
        
        Args:
            github_url: GitHub repository URL
            
        Returns:
            True if repository is accessible
        """
        try:
            owner, repo = self._parse_github_url(github_url)
            repo_url = f"{self.base_url}/repos/{owner}/{repo}"
            
            await self._fetch_with_retry(repo_url)
            return True
            
        except Exception:
            return False