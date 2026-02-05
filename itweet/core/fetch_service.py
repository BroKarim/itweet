"""Fetch services for external sources."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://github.com/trending"


class FetchServiceError(RuntimeError):
    pass


@dataclass
class TrendingRepo:
    name: str
    url: str
    description: str
    language: str
    stars: int
    stars_today: int


class FetchService:
    def __init__(self, timeout_seconds: int = 20) -> None:
        self.timeout_seconds = timeout_seconds

    def fetch_github_trending(
        self,
        since: str = "daily",
        language: Optional[str] = None,
    ) -> List[TrendingRepo]:
        url = self._build_github_url(since=since, language=language)
        headers = {"User-Agent": "Mozilla/5.0"}

        response = requests.get(url, headers=headers, timeout=self.timeout_seconds)
        if response.status_code != 200:
            raise FetchServiceError(f"Failed to fetch GitHub Trending: {response.status_code}")

        soup = BeautifulSoup(response.text, "html.parser")
        repo_list = soup.find_all("article", class_="Box-row")
        if not repo_list:
            raise FetchServiceError("No repositories found. GitHub layout may have changed.")

        trending_repos: List[TrendingRepo] = []
        for repo in repo_list:
            title_tag = repo.h2.a if repo.h2 else None
            if not title_tag or "href" not in title_tag.attrs:
                continue

            href = title_tag["href"].strip()
            repo_name = self._clean_repo_name(title_tag.get_text(strip=True))
            repo_url = f"https://github.com{href}"

            description_tag = repo.find("p", class_=self._desc_class_match)
            description = description_tag.get_text(strip=True) if description_tag else ""

            language_tag = repo.find("span", itemprop="programmingLanguage")
            language_text = language_tag.get_text(strip=True) if language_tag else ""

            stars_tag = repo.find("a", href=lambda x: x and x.endswith("/stargazers"))
            stars_text = stars_tag.get_text(strip=True) if stars_tag else ""

            stars_today_tag = repo.find("span", class_=self._stars_today_match)
            stars_today_text = stars_today_tag.get_text(strip=True) if stars_today_tag else ""

            trending_repos.append(
                TrendingRepo(
                    name=repo_name,
                    url=repo_url,
                    description=description,
                    language=language_text or "N/A",
                    stars=self._parse_count(stars_text),
                    stars_today=self._parse_count(stars_today_text),
                )
            )

        return trending_repos

    @staticmethod
    def _build_github_url(since: str, language: Optional[str]) -> str:
        since = since.lower()
        if language:
            return f"{BASE_URL}/{quote(language)}?since={since}"
        return f"{BASE_URL}?since={since}"

    @staticmethod
    def _clean_repo_name(text: str) -> str:
        return text.replace("\n", "").replace(" ", "").strip()

    @staticmethod
    def _desc_class_match(value) -> bool:
        if not value:
            return False
        if isinstance(value, str):
            return "col-9" in value and "color-fg-muted" in value
        return "col-9" in value and "color-fg-muted" in value

    @staticmethod
    def _stars_today_match(value) -> bool:
        if not value:
            return False
        if isinstance(value, str):
            return "float-sm-right" in value
        return "float-sm-right" in value

    @staticmethod
    def _parse_count(value: str) -> int:
        if not value:
            return 0
        text = value.strip().lower().replace(",", "")
        parts = text.split()
        number = parts[0] if parts else text

        try:
            if number.endswith("k"):
                return int(float(number[:-1]) * 1000)
            if number.endswith("m"):
                return int(float(number[:-1]) * 1_000_000)
            return int(float(number))
        except ValueError:
            return 0
