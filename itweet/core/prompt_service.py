"""Prompt builder for tweet generation."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TweetRequest:
    repo_name: str
    repo_url: str
    description: str
    language: str
    stars: int
    stars_today: int
    readme_text: str
    tone: str = "informative"
    max_chars: int = 280
    thread: bool = False


class PromptService:
    def build_tweet_prompt(self, req: TweetRequest) -> str:
        """
        Build a prompt that generates a tweet (or short thread) based on repo metadata + README.
        """
        base = (
            "You are writing tweets about open-source repositories.\n"
            f"Tone: {req.tone}. Max length per tweet: {req.max_chars} chars.\n"
            "Be accurate. Do not invent facts not supported by README or description.\n"
            "If unsure, keep it high-level.\n"
        )

        if req.thread:
            base += "Output a short thread (2-3 tweets) as a JSON array of strings.\n"
        else:
            base += "Output a single tweet as plain text only.\n"

        repo_block = (
            f"\nRepo:\n"
            f"- Name: {req.repo_name}\n"
            f"- URL: {req.repo_url}\n"
            f"- Description: {req.description}\n"
            f"- Language: {req.language}\n"
            f"- Stars: {req.stars} (today +{req.stars_today})\n"
        )

        readme_block = f"\nREADME (truncated):\n{req.readme_text}\n"

        return base + repo_block + readme_block
