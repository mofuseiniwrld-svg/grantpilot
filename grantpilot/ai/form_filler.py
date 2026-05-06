"""
AI-powered form field mapper.

When a portal's field names don't match the adapter's selectors,
the AI mapper scans the live DOM and maps profile fields to real inputs.

This is the "smart fill" path — the adapters are the "fast path".
"""
import json
from ..profile import Profile


SYSTEM_PROMPT = """You are a form-filling assistant. Given:
1. A JSON user profile
2. A list of form fields (label, name, type, placeholder)

Return a JSON mapping of { "field_name_or_id": "value_from_profile" }.
Only include fields you can confidently fill. Do not invent data."""


async def ai_map_fields(page, profile: Profile, llm_fn) -> dict:
    """
    Scan the page for form fields, ask LLM to map them to profile values.
    llm_fn: async callable(prompt: str) -> str
    """
    # Extract all visible form fields from the DOM
    fields = await page.evaluate("""() => {
        return [...document.querySelectorAll(
            "input:not([type=hidden]):not([type=submit]):not([type=button]), textarea, select"
        )].map(el => ({
            tag: el.tagName,
            type: el.type || "",
            name: el.name || "",
            id: el.id || "",
            placeholder: el.placeholder || "",
            label: (() => {
                const lbl = document.querySelector(`label[for="${el.id}"]`);
                return lbl ? lbl.textContent.trim() : "";
            })(),
            options: el.tagName === "SELECT"
                ? [...el.options].map(o => o.text).slice(0, 20)
                : [],
        }));
    }""")

    prompt = f"""Profile:
{json.dumps(profile.model_dump(), indent=2)}

Form fields:
{json.dumps(fields, indent=2)}

Return JSON mapping {{field_name: value}}."""

    response = await llm_fn(prompt)

    try:
        start = response.index("{")
        end = response.rindex("}") + 1
        return json.loads(response[start:end])
    except Exception:
        return {}


async def apply_ai_mapping(page, mapping: dict) -> None:
    """Apply the LLM-generated field mapping to the page."""
    for field_id_or_name, value in mapping.items():
        if not value:
            continue
        selectors = [
            f'[name="{field_id_or_name}"]',
            f'[id="{field_id_or_name}"]',
        ]
        for sel in selectors:
            try:
                loc = page.locator(sel).first
                if await loc.count() > 0:
                    tag = await loc.evaluate("el => el.tagName.toLowerCase()")
                    if tag == "select":
                        await loc.select_option(label=str(value))
                    elif tag == "textarea":
                        await loc.fill(str(value))
                    else:
                        await loc.fill(str(value))
                    break
            except Exception:
                continue
