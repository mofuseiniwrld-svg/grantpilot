"""
Adapter for submittable.com — used by Mozilla, Shuttleworth, 500+ foundations.
"""
import asyncio
from playwright.async_api import Page
from .base import BaseAdapter
from ..profile import Profile


class SubmittableAdapter(BaseAdapter):
    name = "submittable"
    login_url = "https://submittable.com/login"

    async def fill(self, page: Page, profile: Profile) -> None:
        print("[submittable] Starting form fill...")
        await page.wait_for_load_state("networkidle")

        # Submittable uses a step-by-step wizard
        # Each section is a separate "page" in the form

        # Personal info
        await self._try_fill(page, '[data-qa="first-name-input"]', profile.get("personal.full_name", "").split()[0])
        await self._try_fill(page, '[data-qa="last-name-input"]', " ".join(profile.get("personal.full_name", "").split()[1:]))
        await self._try_fill(page, '[data-qa="email-input"]', profile.get("personal.email"))

        # Text fields — Submittable uses rich text editors
        await self._fill_rich_text(page, profile.get("research.abstract"))
        await self._fill_rich_text(page, profile.get("essays.motivation"))

        print("  [✓] Personal info and essays")
        await self.stop_before_submit(page)

    async def _try_fill(self, page: Page, selector: str, value: str) -> None:
        try:
            loc = page.locator(selector).first
            if await loc.count() > 0:
                await loc.fill(value)
        except Exception:
            pass

    async def _fill_rich_text(self, page: Page, text: str) -> None:
        """Handle ProseMirror / Quill editors used by Submittable."""
        if not text:
            return
        try:
            editor = page.locator('.ProseMirror, .ql-editor').first
            if await editor.count() > 0:
                await editor.click()
                await editor.fill(text)
        except Exception:
            pass
