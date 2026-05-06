"""Cookie import/export — the cleanest way to bypass login on anti-bot portals."""
import json
from pathlib import Path
from typing import Any
from playwright.async_api import BrowserContext


async def import_cookies(context: BrowserContext, cookie_file: str) -> int:
    """Load cookies from a JSON file into a Playwright browser context.

    Accepts both the Playwright cookie format and the Netscape/browser-cookie3
    format (with expirationDate instead of expires).

    Returns the number of cookies loaded.
    """
    path = Path(cookie_file)
    if not path.exists():
        raise FileNotFoundError(f"Cookie file not found: {cookie_file}")

    with open(path) as f:
        raw: list[dict[str, Any]] = json.load(f)

    normalized = []
    for c in raw:
        normalized.append({
            "name":     c["name"],
            "value":    c["value"],
            "domain":   c.get("domain", ""),
            "path":     c.get("path", "/"),
            "expires":  float(c.get("expirationDate", c.get("expires", -1))),
            "httpOnly": bool(c.get("httpOnly", False)),
            "secure":   bool(c.get("secure", False)),
            "sameSite": c.get("sameSite", "Lax"),
        })

    await context.add_cookies(normalized)
    return len(normalized)


async def export_cookies(context: BrowserContext, output_file: str) -> int:
    """Export all cookies from a Playwright context to a JSON file."""
    cookies = await context.cookies()
    with open(output_file, "w") as f:
        json.dump(cookies, f, indent=2)
    return len(cookies)


def export_from_browser(browser: str, domain: str, output_file: str) -> int:
    """Export cookies directly from an installed browser (chrome, firefox, etc.).

    Requires: pip install browser-cookie3
    """
    try:
        import browser_cookie3  # type: ignore
    except ImportError as exc:
        raise ImportError("pip install browser-cookie3") from exc

    getter = getattr(browser_cookie3, browser.lower(), None)
    if getter is None:
        raise ValueError(f"Unsupported browser: {browser}. Try chrome, firefox, edge.")

    jar = getter(domain_name=domain)
    cookies = [
        {
            "name":     c.name,
            "value":    c.value,
            "domain":   c.domain,
            "path":     c.path,
            "expires":  c.expires or -1,
            "secure":   bool(c.secure),
            "httpOnly": bool(getattr(c, "_rest", {}).get("HttpOnly", False)),
            "sameSite": "Lax",
        }
        for c in jar
    ]
    with open(output_file, "w") as f:
        json.dump(cookies, f, indent=2)
    return len(cookies)
