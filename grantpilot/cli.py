"""GrantPilot CLI — powered by Click."""
import asyncio
import click
from rich.console import Console
from rich.panel import Panel

console = Console()


@click.group()
@click.version_option()
def main():
    """GrantPilot — Local-first AI agent for grant & fellowship applications."""


@main.command()
@click.option("--portal", required=True, help="Portal name (awardsplatform, submittable, fluxx)")
@click.option("--profile", required=True, type=click.Path(exists=True), help="Path to profile JSON")
@click.option("--url", default=None, help="Direct URL to the application form")
@click.option("--cookies", default=None, type=click.Path(), help="Path to cookies JSON (skip login)")
@click.option("--email", default=None, help="Login email (if not using cookies)")
@click.option("--password", default=None, help="Login password (if not using cookies)")
@click.option("--headless", is_flag=True, default=False, help="Run browser in headless mode")
@click.option("--dry-run", is_flag=True, default=False, help="Print what would be filled, no browser")
def apply(portal, profile, url, cookies, email, password, headless, dry_run):
    """Fill a grant application form."""
    from .profile import Profile
    from .adapters import get_adapter
    from .agent import GrantPilotAgent

    p = Profile.load(profile)

    if dry_run:
        console.print(Panel(
            f"[bold]Profile loaded:[/bold] {profile}\n"
            f"[bold]Portal:[/bold] {portal}\n"
            f"[bold]Name:[/bold] {p.get('personal.full_name')}\n"
            f"[bold]Email:[/bold] {p.get('personal.email')}\n"
            f"[bold]Research title:[/bold] {p.get('research.title')}",
            title="[green]GrantPilot Dry Run[/green]"
        ))
        return

    console.print(f"[bold green]GrantPilot[/bold green] → [bold]{portal}[/bold]")
    console.print(f"Profile: {p.get('personal.full_name')} / {p.get('personal.email')}")

    async def run():
        adapter = get_adapter(portal)
        async with GrantPilotAgent(cookies_path=cookies, headless=headless) as agent:
            page = await agent.new_page()
            if url:
                await page.goto(url)
            elif email and password:
                await adapter.login(page, email, password)
            else:
                console.print("[yellow]No URL or login provided. Opening portal login page...[/yellow]")
                await page.goto(adapter.login_url)
                console.print("[yellow]Log in manually, then press Enter here to continue.[/yellow]")
                input()

            await adapter.fill(page, p)

    asyncio.run(run())


@main.command("export-cookies")
@click.option("--browser", default="chrome", help="Browser to export from (chrome, firefox)")
@click.option("--domain", required=True, help="Domain to export cookies for")
@click.option("-o", "--output", required=True, help="Output JSON file path")
def export_cookies(browser, domain, output):
    """Export cookies from your local browser to bypass login."""
    from .utils.session import export_chrome_cookies
    export_chrome_cookies(domain, output)
    console.print(f"[green]Cookies exported → {output}[/green]")


@main.command("list-portals")
def list_portals():
    """List all supported grant portals."""
    from .adapters import ADAPTERS
    console.print("[bold]Supported portals:[/bold]")
    for name in ADAPTERS:
        console.print(f"  • {name}")
