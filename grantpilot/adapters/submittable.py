"""Adapter for submittable.com — Mozilla, Shuttleworth, and 500+ foundations."""
from playwright.async_api import Page
from .base import BaseAdapter


class SubmittableAdapter(BaseAdapter):
    name = "submittable"
    login_url = "https://submittable.com/login"

    async def fill(self, page: Page) -> None:
        p = self.profile
        personal = p.get("personal", {})
        research = p.get("research", {})
        essays = p.get("essays", {})
        full_name = personal.get("full_name", "")
        first, *rest = full_name.split() if full_name else ("", [])
        last = " ".join(rest)

        await page.wait_for_load_state("networkidle")

        # Submittable uses aria-label / label[for] patterns
        for label, value in [
            ("First Name", first),
            ("Last Name", last),
            ("Email", personal.get("email", "")),
            ("Country", personal.get("country", "")),
            ("Organization", personal.get("institution", "")),
            ("Affiliation", personal.get("institution", "")),
            ("Project Title", research.get("title", "")),
            ("Title", research.get("title", "")),
            ("Abstract", research.get("abstract", "")),
            ("Summary", research.get("abstract", "")),
            ("Motivation", essays.get("motivation", "")),
            ("Impact", essays.get("impact", "")),
        ]:
            await self._fill_by_label(page, label, value)

        # Document uploads
        docs = p.get("documents", {})
        if docs.get("cv"):
            await self.upload_file(page, 'input[type="file"]', docs["cv"])

        await self.stop_before_submit(page)
