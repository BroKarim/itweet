"""AI-driven selector for trending repositories."""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Iterable, List

from .fetch_service import TrendingRepo


class SelectorServiceError(RuntimeError):
    pass


@dataclass
class SelectedRepo:
    name: str
    url: str
    reason: str


class SelectorService:
    def __init__(self, ai_client) -> None:
        """
        ai_client must expose: generate_text(prompt: str) -> str
        This keeps selector decoupled from the specific AI provider.
        """
        self.ai_client = ai_client

    def select_top_repos(self, repos: Iterable[TrendingRepo], limit: int = 4) -> List[SelectedRepo]:
        repo_list = list(repos)
        if not repo_list:
            return []

        prompt = self._build_prompt(repo_list, limit=limit)
        raw = self.ai_client.generate_text(prompt)
        return self._parse_response(raw, repo_list, limit=limit)

    @staticmethod
    def _build_prompt(repos: List[TrendingRepo], limit: int) -> str:
        rows = []
        for idx, repo in enumerate(repos, start=1):
            rows.append(
                {
                    "id": idx,
                    "name": repo.name,
                    "url": repo.url,
                    "description": repo.description,
                    "language": repo.language,
                    "stars": repo.stars,
                    "stars_today": repo.stars_today,
                }
            )

        payload = json.dumps(rows, ensure_ascii=False)
        return (
            "You are selecting GitHub repositories for tweeting.\n"
            f"Pick the top {limit} that are most interesting or newsworthy.\n"
            "Return ONLY valid JSON array with objects: {id, reason}.\n"
            "No extra text.\n\n"
            f"Repos JSON:\n{payload}\n"
        )

    @staticmethod
    def _parse_response(raw: str, repos: List[TrendingRepo], limit: int) -> List[SelectedRepo]:
        raw = raw.strip()
        data = None
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            # Common failure mode: model wraps JSON with prose or code fences.
            start = raw.find("[")
            end = raw.rfind("]")
            if start != -1 and end != -1 and end > start:
                try:
                    data = json.loads(raw[start : end + 1])
                except json.JSONDecodeError as exc:
                    raise SelectorServiceError("AI response was not valid JSON.") from exc
            else:
                raise SelectorServiceError("AI response was not valid JSON.")

        if not isinstance(data, list):
            raise SelectorServiceError("AI response JSON must be a list.")

        selected: List[SelectedRepo] = []
        for item in data[:limit]:
            if not isinstance(item, dict):
                continue
            repo_id = item.get("id")
            reason = item.get("reason", "").strip()
            if not isinstance(repo_id, int):
                continue
            if repo_id < 1 or repo_id > len(repos):
                continue
            repo = repos[repo_id - 1]
            selected.append(SelectedRepo(name=repo.name, url=repo.url, reason=reason or "-"))

        return selected
