"""Base adapter class — inherit this to add a new grant portal."""
import abc
from typing import Any
from playwright.async_api import Page


class BaseAdapter(abc.ABC):
    """Inherit and implement fill() to support a new portal."""

    name: str = ""
    login_url: str = ""

    def __init__(self, profile: dict[str, Any]) -> None:
        self.profile = profile

    @abc.abstractmethod
    async def fill(self, page: Page) -> None:
        """Fill all form fields with profile data."""
        ...

    # ------------------------------------------------------------------ helpers

    async def upload_file(self, page: Page, selector: str, file_path: str) -> None:
        """Upload a local file to a <input type=file> element."""
        if file_path:
            try:
                await page.set_input_files(selector, file_path)
            except Exception:
                pass

    async def stop_before_submit(self, page: Page) -> None:
        """Highlight the submit button and wait for the user to click it.

        GrantPilot NEVER auto-submits — the human always makes the final call.
        """
        await page.evaluate("""
            () => {
                const btns = document.querySelectorAll(
                    'button[type=submit], input[type=submit], [data-testid*="submit"]'
                );
                btns.forEach(btn => {
                    btn.style.outline = '3px solid #ff3b30';
                    btn.style.boxShadow = '0 0 12px #ff3b30';
                    btn.title = 'GrantPilot: review & click when ready';
                });
            }
        """)
        print("\n✅  Form filled. Review the browser then click Submit.")
        print("    Press ENTER here to close without submitting.\n")
        input()

    async def _fill_if_exists(self, page: Page, selector: str, value: str) -> None:
        """Fill the first matching element; silently skip if absent or empty."""
        if not value:
            return
        try:
            loc = page.locator(selector).first
            if await loc.count() > 0:
                await loc.fill(value)
        except Exception:
            pass

    async def _fill_by_label(self, page: Page, label_text: str, value: str) -> None:
        """Fill an input associated with a label containing label_text."""
        if not value:
            return
        try:
            await page.get_by_label(label_text, exact=False).fill(value)
        except Exception:
            pass
