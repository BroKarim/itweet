"""
Command-line interface for iTweet.

Initial CLI skeleton with a GitHub Trending command placeholder.
"""
import sys
from typing import Optional

import click

from .core.ai_service import AIService, AIServiceError
from .core.fetch_service import FetchService, FetchServiceError
from .core.readme_service import ReadmeService, ReadmeServiceError
from .core.prompt_service import PromptService, TweetRequest
from .core.output_writer import OutputWriter, OutputWriterError
from .core.selector_service import SelectorService, SelectorServiceError


def _normalize_tweet_language(raw: str) -> str:
    normalized = (raw or "").strip()
    if not normalized:
        return "English"
    key = normalized.lower()
    aliases = {
        "en": "English",
        "english": "English",
        "id": "Indonesian",
        "indo": "Indonesian",
        "indonesia": "Indonesian",
        "indonesian": "Indonesian",
        "bahasa indonesia": "Indonesian",
        "ms": "Malay",
        "malay": "Malay",
        "melayu": "Malay",
        "malaysia": "Malay",
        "malasyia": "Malay",
        "es": "Spanish",
        "spanish": "Spanish",
        "fr": "French",
        "french": "French",
        "de": "German",
        "german": "German",
        "ja": "Japanese",
        "japanese": "Japanese",
        "jp": "Japanese",
        "ko": "Korean",
        "korean": "Korean",
        "zh": "Chinese",
        "chinese": "Chinese",
        "pt": "Portuguese",
        "portuguese": "Portuguese",
    }
    return aliases.get(key, normalized)


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def main():
    """iTweet CLI entrypoint."""
    pass


@main.command()
@click.option(
    "--since",
    type=click.Choice(["daily", "weekly", "monthly"], case_sensitive=False),
    default="daily",
    show_default=True,
    help="Trending time range",
)
@click.option(
    "--lang",
    "tweet_language",
    type=str,
    default="English",
    show_default=True,
    help="Output language for generated tweets",
)
@click.option(
    "--code-lang",
    "language",
    type=str,
    default=None,
    help="Filter by programming language (optional)",
)
@click.option(
    "--limit",
    type=int,
    default=25,
    show_default=True,
    help="How many trending repos to consider",
)
@click.option(
    "--pick",
    type=int,
    default=4,
    show_default=True,
    help="How many repos the AI should pick",
)
@click.option(
    "--readme-chars",
    type=int,
    default=6000,
    show_default=True,
    help="Max README characters to fetch per repo (0 = unlimited)",
)
@click.option(
    "--list-only",
    is_flag=True,
    default=False,
    help="Only list trending repos (skip AI selection and README fetching)",
)
@click.option(
    "--no-tweets",
    is_flag=True,
    default=False,
    help="Skip tweet generation (only list + AI pick)",
)
@click.option(
    "--thread",
    is_flag=True,
    default=False,
    help="Generate short thread (2-3 tweets) per repo instead of single tweet",
)
@click.option(
    "--tone",
    type=str,
    default="informative",
    show_default=True,
    help="Tone for tweets (e.g., informative, casual, excited)",
)
@click.option(
    "--max-chars",
    type=int,
    default=280,
    show_default=True,
    help="Max characters per tweet",
)
@click.option(
    "--output",
    type=str,
    default=None,
    help="Write tweets to file (txt); if omitted, print to stdout",
)
@click.option(
    "--json",
    "json_output",
    is_flag=True,
    default=False,
    help="Also save tweets as JSON",
)
def github(
    since: str,
    language: Optional[str],
    limit: int,
    pick: int,
    readme_chars: int,
    list_only: bool,
    no_tweets: bool,
    thread: bool,
    tone: str,
    max_chars: int,
    tweet_language: str,
    output: Optional[str],
    json_output: bool,
):
    """Fetch GitHub Trending, then (optionally) let AI pick top repos and fetch their READMEs."""
    tweet_language = _normalize_tweet_language(tweet_language)

    click.echo("iTweet: GitHub Trending")
    click.echo(f"- since: {since}")
    click.echo(f"- code lang: {language or 'all'}")
    click.echo(f"- tweet language: {tweet_language}")

    ai_service = None
    if not list_only:
        ai_service = AIService()
        if not ai_service.validate_api_key():
            click.echo("\n🔑 iTweet requires an OpenRouter API key.")
            click.echo("Get your key at: https://openrouter.ai/keys")
            try:
                user_key = input("\nPlease enter your OpenRouter API key: ").strip()
                if user_key:
                    ai_service = AIService(api_key=user_key)
                    ai_service.config_manager.save_api_key(user_key)
                else:
                    click.echo("❌ Error: No API key provided.")
                    return 1
            except (EOFError, KeyboardInterrupt):
                click.echo("\n⚠️  Action cancelled.")
                return 1

    service = FetchService()
    try:
        repos = service.fetch_github_trending(since=since, language=language)
    except FetchServiceError as exc:
        click.echo(f"\nError: {exc}")
        return 1

    if not repos:
        click.echo("\nNo trending repositories found.")
        return 0

    click.echo("\nTrending repositories:\n")
    repos = repos[: max(1, limit)]
    for idx, repo in enumerate(repos, start=1):
        stars_today = f" (+{repo.stars_today} today)" if repo.stars_today else ""
        desc = repo.description or "-"
        click.echo(f"{idx}. {repo.name} [{repo.language}]")
        click.echo(f"   {repo.url}")
        click.echo(f"   ⭐ {repo.stars}{stars_today}")
        click.echo(f"   {desc}\n")

    if list_only:
        return 0

    pick = max(1, min(pick, len(repos)))
    selector = SelectorService(ai_service)
    try:
        selected = selector.select_top_repos(repos, limit=pick)
    except (SelectorServiceError, AIServiceError) as exc:
        click.echo(f"\nError: failed to select repos via AI: {exc}")
        return 1

    if not selected:
        click.echo("\nAI did not select any repositories.")
        return 1

    click.echo("\nAI selected:\n")
    for idx, repo in enumerate(selected, start=1):
        click.echo(f"{idx}. {repo.name}")
        click.echo(f"   {repo.url}")
        click.echo(f"   reason: {repo.reason}\n")

    readme_service = ReadmeService()
    prompt_service = PromptService()
    output_writer = OutputWriter()

    click.echo("Fetching READMEs (for context / to reduce misinformation):\n")
    readme_map = {}
    for repo in selected:
        click.echo(f"- {repo.name}:")
        try:
            text = readme_service.fetch_readme(repo.url, max_chars=readme_chars)
            readme_map[repo.name] = text
            click.echo(f"  README fetched: {len(text)} chars\n")
        except ReadmeServiceError as exc:
            readme_map[repo.name] = ""
            click.echo(f"  README fetch failed: {exc}\n")

    if no_tweets:
        click.echo("Tip: remove --no-tweets to generate tweet drafts.")
        return 0

    click.echo("Generating tweet drafts:\n")
    drafts = []
    for selected_repo in selected:
        repo = next((r for r in repos if r.name == selected_repo.name), None)
        if not repo:
            continue
        readme_text = readme_map.get(repo.name, "")
        req = TweetRequest(
            repo_name=repo.name,
            repo_url=repo.url,
            description=repo.description,
            language=repo.language,
            stars=repo.stars,
            stars_today=repo.stars_today,
            readme_text=readme_text,
            output_language=tweet_language,
            tone=tone,
            max_chars=max_chars,
            thread=thread,
        )
        prompt = prompt_service.build_tweet_prompt(req)
        try:
            result = ai_service.generate_text(prompt)
        except AIServiceError as exc:
            click.echo(f"❌ Failed to generate tweet for {repo.name}: {exc}")
            continue
        drafts.append(result)

        click.echo(f"- {repo.name}\n{result}\n")

    if output or json_output:
        try:
            if output:
                path = output_writer.write_text(drafts, filename=output)
                click.echo(f"Saved tweets to: {path}")
            if json_output:
                path = output_writer.write_json(drafts)
                click.echo(f"Saved tweets to: {path}")
        except OutputWriterError as exc:
            click.echo(f"⚠️  Failed to write output: {exc}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
