"""Adapter for fluxx.io — Gates Foundation, Wellcome Trust, and others."""
from playwright.async_api import Page
from .base import BaseAdapter


class FluxxAdapter(BaseAdapter):
    name = "fluxx"
    login_url = ""  # Each org has its own Fluxx subdomain

    async def fill(self, page: Page) -> None:
        p = self.profile
        personal = p.get("personal", {})
        research = p.get("research", {})
        essays = p.get("essays", {})
        full_name = personal.get("full_name", "")
        first, *rest = full_name.split() if full_name else ("", [])
        last = " ".join(rest)

        await page.wait_for_load_state("networkidle")

        # Fluxx uses React forms with data-field-id attributes
        for name_attr, value in [
            ("first_name", first),
            ("last_name", last),
            ("email", personal.get("email", "")),
            ("organization_name", personal.get("institution", "")),
            ("project_title", research.get("title", "")),
            ("project_summary", research.get("abstract", "")),
            ("project_description", essays.get("motivation", "")),
        ]:
            await self._fill_if_exists(
                page,
                f'[data-field-id="{name_attr}"],[name="{name_attr}"]',
                value,
            )

        await self.stop_before_submit(page)
