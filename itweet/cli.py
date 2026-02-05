"""
Command-line interface for iTweet.

Initial CLI skeleton with a GitHub Trending command placeholder.
"""
import sys
import click

from .core.ai_service import AIService, AIServiceError
from .core.fetch_service import FetchService, FetchServiceError


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
    "language",
    type=str,
    default=None,
    help="Filter by programming language (optional)",
)
def github(since: str, language: str | None):
    """Fetch GitHub Trending and print a simple list."""
    click.echo("iTweet: GitHub Trending")
    click.echo(f"- since: {since}")
    click.echo(f"- lang: {language or 'all'}")

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
    for idx, repo in enumerate(repos, start=1):
        stars_today = f" (+{repo.stars_today} today)" if repo.stars_today else ""
        desc = repo.description or "-"
        click.echo(f"{idx}. {repo.name} [{repo.language}]")
        click.echo(f"   {repo.url}")
        click.echo(f"   ⭐ {repo.stars}{stars_today}")
        click.echo(f"   {desc}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
