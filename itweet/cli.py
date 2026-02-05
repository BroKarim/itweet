"""
Command-line interface for iTweet.

Initial CLI skeleton with a GitHub Trending command placeholder.
"""
import sys
import click


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
    """Fetch GitHub Trending (placeholder)."""
    click.echo("iTweet: GitHub Trending")
    click.echo(f"- since: {since}")
    click.echo(f"- lang: {language or 'all'}")
    click.echo("\nNext: implement scraper + AI tweet draft generation.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
