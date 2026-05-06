"""LLM-powered form filler — fallback for portals without a dedicated adapter.

Scans the live DOM, extracts all form fields, uses an LLM to map profile values
to each field, then fills them. Never submits automatically.
"""
import json
from typing import Any
from playwright.async_api import Page


class AIFormFiller:
    """Use when there is no dedicated adapter for the target portal."""

    def __init__(self, profile: dict[str, Any], model: str = "gpt-4o-mini") -> None:
        self.profile = profile
        self.model = model

    async def fill(self, page: Page) -> None:
        """Scan DOM -> map via LLM -> fill -> stop before submit."""
        await page.wait_for_load_state("networkidle")
        fields = await self._extract_fields(page)
        if not fields:
            print("No form fields found on this page.")
            return
        print(f"Found {len(fields)} form fields. Mapping with LLM...")
        mappings = await self._map_fields_via_llm(fields)
        print(f"Filling {len(mappings)} matched fields...")
        await self._apply_mappings(page, mappings)
        await self._stop_before_submit(page)

    # ------------------------------------------------------------------ private

    async def _extract_fields(self, page: Page) -> list[dict]:
        return await page.evaluate("""
            () => {
                const fields = [];
                const inputs = document.querySelectorAll(
                    'input:not([type=hidden]):not([type=submit]):not([type=button]):not([type=reset]),'
                    + 'textarea, select'
                );
                inputs.forEach(el => {
                    const label = el.id
                        ? document.querySelector('label[for="' + el.id + '"]')
                        : null;
                    fields.push({
                        tag:         el.tagName.toLowerCase(),
                        type:        el.type || '',
                        name:        el.name || '',
                        id:          el.id || '',
                        placeholder: el.placeholder || '',
                        label:       label ? label.textContent.trim() : '',
                        required:    el.required,
                    });
                });
                return fields;
            }
        """)

    async def _map_fields_via_llm(self, fields: list[dict]) -> list[dict]:
        try:
            import openai  # optional dependency
            client = openai.AsyncOpenAI()
            prompt = (
                "Map the user profile to HTML form fields.\n\n"
                f"Profile:\n{json.dumps(self.profile, indent=2)}\n\n"
                f"Form fields:\n{json.dumps(fields, indent=2)}\n\n"
                "Output a JSON array: [{\"selector\": \"<CSS selector>\", \"value\": \"<value from profile>\"}]\n"
                "Build selectors from name, id, or placeholder attributes.\n"
                "Only include fields where you can confidently match a value.\n"
                "Return ONLY valid JSON, no explanation."
            )
            resp = await client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
            )
            raw = resp.choices[0].message.content.strip()
            # Strip markdown fences if present
            if raw.startswith("```"):
                raw = raw.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
            result = json.loads(raw)
            return result if isinstance(result, list) else []
        except Exception as exc:
            print(f"LLM mapping failed ({exc}). Fill manually.")
            return []

    async def _apply_mappings(self, page: Page, mappings: list[dict]) -> None:
        for m in mappings:
            sel, val = m.get("selector"), m.get("value")
            if not sel or not val:
                continue
            try:
                await page.fill(sel, str(val))
                print(f"  filled  {sel[:60]} = {str(val)[:50]}")
            except Exception as exc:
                print(f"  skipped {sel[:60]} ({exc})")

    async def _stop_before_submit(self, page: Page) -> None:
        await page.evaluate("""
            () => {
                document.querySelectorAll(
                    'button[type=submit],input[type=submit]'
                ).forEach(b => {
                    b.style.outline = '3px solid #ff3b30';
                    b.style.boxShadow = '0 0 12px #ff3b30';
                });
            }
        """)
        print("\n\u2705  AI fill complete. Review the browser, then click Submit.")
        input("Press ENTER to close without submitting...\n")
