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
    output_language: str = "English"
    tone: str = "informative"
    max_chars: int = 280
    thread: bool = False


class PromptService:
    def build_tweet_prompt(self, req: TweetRequest) -> str:
        """
        Build a prompt that generates a tweet (or short thread) based on repo metadata + README.
        """
        base = (
            f"You are writing tweets in {req.output_language} about open-source repositories.\n"
            "Write in casual, informal language. Sound like a Twitter influencer, but stay informative.\n"
            f"Tone: {req.tone}. Max length per tweet: {req.max_chars} chars.\n"
            "Be accurate. Do not invent facts not supported by README or description.\n"
            "If unsure, keep it high-level.\n"
            "Structure:\n"
            "1) Opening line that is catchy and relevant.\n"
            "   Vary the opening across outputs. Pick ONE style each time:\n"
            "   - Problem hook: start from a clear pain/issue the repo solves.\n"
            "   - Storytelling: a short mini-story or relatable scenario.\n"
            "   - Benefit-first: lead with the most concrete benefit.\n"
            "   Keep it natural, not textbook/theory. Avoid generic phrases.\n"
            "2) GitHub link on its own line.\n"
            "3) Bullet-style points using lines starting with '> ' (2-5 points).\n"
            "Points can be features, usage steps, or key notes—pick what's most helpful.\n"
            "No emojis unless they already appear in the README.\n"
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
