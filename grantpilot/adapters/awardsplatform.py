"""
Adapter for awardsplatform.com — used by Mila, IDRC, and many foundations.

Portal structure (discovered via manual inspection):
  /gallery → programme listing
  /entry/new → create new application entry
  /entry/{id}/edit → edit existing entry
"""
import asyncio
from playwright.async_api import Page
from .base import BaseAdapter
from ..profile import Profile


class AwardsPlatformAdapter(BaseAdapter):
    name = "awardsplatform"
    login_url = "https://mila.awardsplatform.com/auth/login"

    async def fill(self, page: Page, profile: Profile) -> None:
        """Fill Mila AI Policy Fellowship application on awardsplatform.com."""
        print("[awardsplatform] Starting form fill...")

        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(1)

        # ── Step 1: Entry name ─────────────────────────────────────────────
        entry_name_sel = 'input[name="name"], input[placeholder*="name" i]'
        if await page.locator(entry_name_sel).count() > 0:
            await page.fill(entry_name_sel, profile.extras.get("entry_name", "Application_1"))
            print("  [✓] Entry name")

        # ── Step 2: Eligibility checkboxes ─────────────────────────────────
        checkboxes = page.locator('input[type="checkbox"]'
        )
        count = await checkboxes.count()
        for i in range(count):
            cb = checkboxes.nth(i)
            if not await cb.is_checked():
                await cb.check()
        print(f"  [✓] Checked {count} eligibility boxes")

        # ── Step 3: Personal information ───────────────────────────────────
        field_map = {
            'input[name*="first_name" i], input[placeholder*="first name" i]': profile.get("personal.full_name", "").split()[0],
            'input[name*="last_name" i], input[placeholder*="last name" i]': " ".join(profile.get("personal.full_name", "").split()[1:]),
            'input[name*="full_name" i], input[placeholder*="full name" i]': profile.get("personal.full_name"),
            'input[name*="email" i], input[type="email"]': profile.get("personal.email"),
            'input[name*="country" i], select[name*="country" i]': profile.get("personal.country"),
            'input[name*="institution" i], input[name*="university" i]': profile.get("personal.institution"),
            'input[name*="degree" i], input[name*="education" i]': profile.get("personal.degree"),
            'input[name*="position" i], input[name*="role" i], input[name*="title" i]': profile.get("personal.role"),
        }
        for selector, value in field_map.items():
            if not value:
                continue
            for sel in selector.split(", "):
                try:
                    loc = page.locator(sel).first
                    if await loc.count() > 0 and await loc.is_visible():
                        tag = await loc.evaluate("el => el.tagName.toLowerCase()")
                        if tag == "select":
                            await loc.select_option(label=value)
                        else:
                            await loc.fill(value)
                        break
                except Exception:
                    continue

        print("  [✓] Personal information")

        # ── Step 4: Reference ──────────────────────────────────────────────
        refs = profile.references
        if refs:
            ref = refs[0]
            ref_fields = {
                'input[name*="referee" i], input[name*="reference_name" i]': ref.name,
                'input[name*="referee_email" i], input[name*="reference_email" i]': ref.email,
                'input[name*="referee_institution" i]': ref.institution,
            }
            for selector, value in ref_fields.items():
                for sel in selector.split(", "):
                    try:
                        loc = page.locator(sel).first
                        if await loc.count() > 0:
                            await loc.fill(value)
                            break
                    except Exception:
                        continue
            print("  [✓] Reference")

        # ── Step 5: Research / project fields ─────────────────────────────
        research_fields = {
            'input[name*="project_title" i], input[name*="research_title" i]': profile.get("research.title"),
            'textarea[name*="abstract" i], textarea[name*="summary" i]': profile.get("research.abstract"),
            'textarea[name*="motivation" i], textarea[name*="why" i]': profile.get("essays.motivation"),
            'textarea[name*="impact" i]': profile.get("essays.impact"),
            'textarea[name*="methodology" i], textarea[name*="approach" i]': profile.get("essays.methodology"),
        }
        for selector, value in research_fields.items():
            if not value:
                continue
            for sel in selector.split(", "):
                try:
                    loc = page.locator(sel).first
                    if await loc.count() > 0 and await loc.is_visible():
                        await loc.fill(value)
                        break
                except Exception:
                    continue
        print("  [✓] Research fields")

        # ── Step 6: File uploads ───────────────────────────────────────────
        if profile.documents.cv:
            upload_btns = page.locator('input[type="file"]')
            if await upload_btns.count() > 0:
                await self.upload_file(page, 'input[type="file"] >> nth=0', profile.documents.cv)
                print("  [✓] CV uploaded")

        if profile.documents.writing_sample:
            upload_btns = page.locator('input[type="file"]')
            if await upload_btns.count() > 1:
                await self.upload_file(page, 'input[type="file"] >> nth=1', profile.documents.writing_sample)
                print("  [✓] Writing sample uploaded")

        # ── Step 7: Save draft ─────────────────────────────────────────────
        save_btn = page.locator('button:has-text("Save"), button:has-text("Save draft")').first
        if await save_btn.count() > 0:
            await save_btn.click()
            await page.wait_for_load_state("networkidle")
            print("  [✓] Draft saved")

        await self.stop_before_submit(page)
