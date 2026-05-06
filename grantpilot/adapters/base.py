"""Base adapter — inherit to add support for a new grant portal."""
from abc import ABC, abstractmethod
from pathlib import Path
from playwright.async_api import Page
from ..profile import Profile


class BaseAdapter(ABC):
    name: str = "base"
    login_url: str = ""

    async def login(self, page: Page, email: str, password: str) -> None:
        """Default login flow — override if portal is non-standard."""
        await page.goto(self.login_url)
        await page.wait_for_load_state("networkidle")
        await page.fill('input[type="email"], input[name="email"]', email)
        await page.fill('input[type="password"]', password)
        await page.click('button[type="submit"], input[type="submit"]')
        await page.wait_for_load_state("networkidle")

    @abstractmethod
    async def fill(self, page: Page, profile: Profile) -> None:
        """Fill all form fields. Must call stop_before_submit() at the end."""
        ...

    async def upload_file(self, page: Page, selector: str, file_path: str) -> None:
        """Upload a file to an input[type=file] element."""
        if not file_path or not Path(file_path).exists():
            print(f"  [skip] File not found: {file_path}")
            return
        async with page.expect_file_chooser() as fc_info:
            await page.click(selector)
        file_chooser = await fc_info.value
        await file_chooser.set_files(file_path)

    async def stop_before_submit(self, page: Page) -> None:
        """
        Pause for human review. NEVER auto-submit.
        Highlights the submit button so the user can find it easily.
        """
        print()
        print("=" * 60)
        print("  GrantPilot: Form filled. Review and submit manually.")
        print("  Browser will stay open until you close it.")
        print("=" * 60)
        # Highlight submit button
        await page.evaluate("""
            const btns = [...document.querySelectorAll(
                'button[type="submit"], input[type="submit"], button'
            )].filter(b => /submit|apply|send/i.test(b.textContent));
            btns.forEach(b => {
                b.style.outline = "4px solid #00ff88";
                b.style.boxShadow = "0 0 20px #00ff88";
            });
        """)
        await page.pause()  # Opens Playwright Inspector for manual control
