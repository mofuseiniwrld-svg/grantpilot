"""Browser automation core — Playwright wrapper with anti-detection defaults."""
import asyncio
import json
from pathlib import Path
from typing import Optional
from playwright.async_api import async_playwright, Browser, BrowserContext, Page


STEALTH_SCRIPTS = """
Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3,4,5]});
Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
window.chrome = {runtime: {}};
"""


class GrantPilotAgent:
    """
    Manages a local Playwright browser session.

    Key design: runs on the user's machine (residential IP, real fingerprint).
    This is why it bypasses DataDome / Cloudflare where cloud agents fail.
    """

    def __init__(
        self,
        cookies_path: Optional[str] = None,
        headless: bool = False,
        slow_mo: int = 50,
    ):
        self.cookies_path = cookies_path
        self.headless = headless
        self.slow_mo = slow_mo
        self._playwright = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None

    async def __aenter__(self):
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(
            headless=self.headless,
            slow_mo=self.slow_mo,
            args=["--disable-blink-features=AutomationControlled"],
        )
        context_options = {
            "viewport": {"width": 1280, "height": 800},
            "user_agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
        }
        if self.cookies_path and Path(self.cookies_path).exists():
            cookies = json.loads(Path(self.cookies_path).read_text())
            context_options["storage_state"] = {"cookies": cookies, "origins": []}

        self._context = await self._browser.new_context(**context_options)
        await self._context.add_init_script(STEALTH_SCRIPTS)
        return self

    async def __aexit__(self, *_):
        if self._context:
            await self._context.close()
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()

    async def new_page(self) -> Page:
        return await self._context.new_page()

    async def inject_cookies(self, cookies: list[dict]) -> None:
        """Inject cookies at runtime (e.g. exported from Chrome)."""
        await self._context.add_cookies(cookies)

    async def save_session(self, path: str) -> None:
        """Persist current session for reuse."""
        state = await self._context.storage_state()
        Path(path).write_text(json.dumps(state, indent=2))
        print(f"Session saved to {path}")
