"""Adapter for awardsplatform.com — used by Mila, IDRC, and many foundations."""
from playwright.async_api import Page
from .base import BaseAdapter


class AwardsPlatformAdapter(BaseAdapter):
    name = "awardsplatform"
    login_url = "https://awardsplatform.com/login"

    async def fill(self, page: Page) -> None:  # noqa: C901
        p = self.profile
        personal = p.get("personal", {})
        research = p.get("research", {})
        essays = p.get("essays", {})
        refs = p.get("references", [])
        full_name = personal.get("full_name", "")
        first, *rest = full_name.split() if full_name else ("", [])
        last = " ".join(rest)

        await page.wait_for_load_state("networkidle")

        # ---------- personal info
        await self._fill_if_exists(page, '[name="first_name"],[placeholder*="First name"]', first)
        await self._fill_if_exists(page, '[name="last_name"],[placeholder*="Last name"]', last)
        await self._fill_if_exists(page, '[name="full_name"],[placeholder*="Full name"]', full_name)
        await self._fill_if_exists(page, '[type="email"],[name="email"]', personal.get("email", ""))
        await self._fill_if_exists(
            page,
            '[name="country"],[placeholder*="Country"]',
            personal.get("country", ""),
        )
        await self._fill_if_exists(
            page,
            '[name="institution"],[name="organization"],[placeholder*="Institution"],[placeholder*="Organization"]',
            personal.get("institution", ""),
        )
        await self._fill_if_exists(
            page,
            '[name="degree"],[placeholder*="Degree"],[placeholder*="Highest degree"]',
            personal.get("degree", ""),
        )
        await self._fill_if_exists(
            page,
            '[name="role"],[name="position"],[name="job_title"],[placeholder*="Role"],[placeholder*="Position"]',
            personal.get("role", ""),
        )

        # ---------- research / project
        await self._fill_if_exists(
            page,
            '[name="title"],[name="project_title"],[placeholder*="Project title"],[placeholder*="Title"]',
            research.get("title", ""),
        )
        await self._fill_if_exists(
            page,
            '[name="abstract"],[name="summary"],[placeholder*="Abstract"],[placeholder*="Summary"]',
            research.get("abstract", ""),
        )
        await self._fill_if_exists(
            page,
            '[name="research_area"],[name="thematic_area"],[placeholder*="Thematic"],[placeholder*="Research area"]',
            research.get("area", ""),
        )

        # ---------- essays
        await self._fill_if_exists(
            page,
            '[name="motivation"],[placeholder*="motivation"],[placeholder*="Motivation"]',
            essays.get("motivation", ""),
        )
        await self._fill_if_exists(
            page,
            '[name="impact"],[placeholder*="impact"],[placeholder*="Impact"]',
            essays.get("impact", ""),
        )
        await self._fill_if_exists(
            page,
            '[name="methodology"],[placeholder*="methodology"],[placeholder*="Methodology"]',
            essays.get("methodology", ""),
        )

        # ---------- first reference
        if refs:
            ref = refs[0]
            await self._fill_if_exists(
                page, '[name="reference_name"],[placeholder*="Referee name"],[placeholder*="Reference name"]',
                ref.get("name", ""),
            )
            await self._fill_if_exists(
                page, '[name="reference_email"],[placeholder*="Referee email"],[placeholder*="Reference email"]',
                ref.get("email", ""),
            )
            await self._fill_if_exists(
                page, '[name="reference_institution"],[placeholder*="Referee institution"]',
                ref.get("institution", ""),
            )
            await self._fill_if_exists(
                page, '[name="reference_relationship"],[placeholder*="Relationship"]',
                ref.get("relationship", ""),
            )

        # ---------- documents
        docs = p.get("documents", {})
        if docs.get("cv"):
            await self.upload_file(page, '[type="file"][name*="cv"],[type="file"][name*="resume"]', docs["cv"])

        await self.stop_before_submit(page)
