"""Fetch repository README content (used to reduce misinformation in tweets)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple
from urllib.parse import urlparse

import requests


class ReadmeServiceError(RuntimeError):
    pass


@dataclass
class RepoRef:
    owner: str
    repo: str


class ReadmeService:
    def __init__(self, timeout_seconds: int = 20) -> None:
        self.timeout_seconds = timeout_seconds

    def fetch_readme(self, repo_url: str, max_chars: int = 12_000) -> str:
        """
        Fetch README as plain text (best-effort).

        Strategy:
        1) GitHub REST API: GET /repos/{owner}/{repo}/readme -> download_url
        2) Fallback to raw URLs with common branches and filenames
        """
        ref = self._parse_repo_url(repo_url)
        if not ref:
            raise ReadmeServiceError(f"Invalid repo URL: {repo_url}")

        text = self._fetch_via_github_api(ref)
        if text is None:
            text = self._fetch_via_raw_fallback(ref)
        if text is None:
            raise ReadmeServiceError("README not found.")

        text = text.replace("\r\n", "\n")
        if max_chars > 0:
            return text[:max_chars]
        return text

    @staticmethod
    def _parse_repo_url(repo_url: str) -> Optional[RepoRef]:
        try:
            parsed = urlparse(repo_url)
        except Exception:
            return None
        if parsed.netloc.lower() != "github.com":
            return None
        parts = [p for p in parsed.path.split("/") if p]
        if len(parts) < 2:
            return None
        owner, repo = parts[0], parts[1]
        if repo.endswith(".git"):
            repo = repo[:-4]
        return RepoRef(owner=owner, repo=repo)

    def _fetch_via_github_api(self, ref: RepoRef) -> Optional[str]:
        url = f"https://api.github.com/repos/{ref.owner}/{ref.repo}/readme"
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "Mozilla/5.0",
        }
        try:
            r = requests.get(url, headers=headers, timeout=self.timeout_seconds)
        except requests.RequestException:
            return None

        if r.status_code != 200:
            return None

        try:
            data = r.json()
        except ValueError:
            return None

        download_url = data.get("download_url")
        if not download_url:
            return None

        try:
            rr = requests.get(download_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=self.timeout_seconds)
        except requests.RequestException:
            return None
        if rr.status_code != 200:
            return None
        return rr.text

    def _fetch_via_raw_fallback(self, ref: RepoRef) -> Optional[str]:
        branches = ["main", "master"]
        filenames = ["README.md", "README.MD", "README.rst", "README.txt", "README"]

        for branch in branches:
            for filename in filenames:
                raw_url = f"https://raw.githubusercontent.com/{ref.owner}/{ref.repo}/{branch}/{filename}"
                try:
                    r = requests.get(raw_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=self.timeout_seconds)
                except requests.RequestException:
                    continue
                if r.status_code == 200 and r.text.strip():
                    return r.text
        return None

