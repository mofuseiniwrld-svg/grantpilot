# GrantPilot 🚀

**Local-first AI agent for grant & fellowship applications.**

Cloud-hosted AI automation fails on grant portals because DataDome, Cloudflare, and similar systems block datacenter IPs. GrantPilot runs on **your machine** — real IP, real browser fingerprint, zero bot detection.

```bash
pip install grantpilot
grantpilot apply --portal awardsplatform --profile profiles/me.json
```

---

## Why GrantPilot exists

Every grant application is 2–4 hours of copy-pasting the same information into a different form. The information doesn't change. The portals do. GrantPilot learns your profile once and fills any portal — automatically.

The hard part isn't the AI. It's getting past bot detection. GrantPilot solves this by running locally using your real browser session.

---

## How it works

```
profiles/me.json          ← your info, stored once
       │
       ▼
grantpilot CLI / Python API
       │
       ▼
Portal Adapter (awardsplatform / submittable / fluxx / ...)
       │
       ▼
Local Playwright browser (your IP, your fingerprint)
       │
       ▼
AI form-filler (maps profile fields → form fields via LLM)
       │
       ▼
Review draft → you click Submit
```

**GrantPilot never submits without your confirmation.**

---

## Supported portals

| Portal | Status | Used by |
|--------|--------|---------|
| awardsplatform.com | ✅ Stable | Mila, IDRC, many foundations |
| submittable.com | ✅ Stable | Mozilla, Shuttleworth, 500+ foundations |
| fluxx.io | 🔧 Beta | Gates Foundation, Wellcome Trust |
| SurveyMonkey Apply | 🔧 Beta | Many academic fellowships |
| OpenGrants | 🗓 Planned | — |
| Custom (bring your own) | ✅ Stable | Write a 50-line adapter |

---

## Quickstart

### 1. Install
```bash
pip install grantpilot
playwright install chromium
```

### 2. Create your profile
```bash
cp profiles/example_profile.json profiles/me.json
# Edit me.json with your info
```

### 3. Run
```bash
# Fill a form (stops before submit — you review first)
grantpilot apply --portal awardsplatform --profile profiles/me.json --url https://mila.awardsplatform.com/...

# Use an existing browser session (bypasses login entirely)
grantpilot apply --portal awardsplatform --profile profiles/me.json --cookies cookies.json

# Dry run (shows what it would fill, no browser)
grantpilot apply --portal awardsplatform --profile profiles/me.json --dry-run
```

### 4. Export cookies from Chrome (optional, best for anti-bot portals)
```bash
# Install: pip install browser-cookie3
grantpilot export-cookies --browser chrome --domain awardsplatform.com -o cookies.json
```

---

## Profile format

```json
{
  "personal": {
    "full_name": "Fuseini Mohammed",
    "email": "you@example.com",
    "country": "Ghana",
    "institution": "KNUST",
    "degree": "MSc Computer Science (AI)",
    "role": "Founder, SankofaAI"
  },
  "research": {
    "area": "AI Governance, Policy, West Africa",
    "title": "Governing AI in the Absence of Governance: Regulatory Capacity for West Africa",
    "abstract": "..."
  },
  "essays": {
    "motivation": "...",
    "impact": "...",
    "methodology": "..."
  },
  "references": [
    {
      "name": "Dr. Kwame Asante",
      "email": "kwame.asante@knust.edu.gh",
      "institution": "KNUST",
      "relationship": "Academic Supervisor"
    }
  ],
  "documents": {
    "cv": "docs/cv.pdf",
    "writing_sample": "docs/writing_sample.pdf"
  }
}
```

---

## Architecture

```
grantpilot/
├── cli.py              # CLI entry point (Click)
├── profile.py          # Profile load/validate/merge
├── agent.py            # Playwright browser controller
├── adapters/           # One file per grant portal
│   ├── base.py         # BaseAdapter (inherit to add a portal)
│   ├── awardsplatform.py
│   ├── submittable.py
│   └── fluxx.py
├── ai/
│   └── form_filler.py  # LLM maps profile → form fields
└── utils/
    └── session.py      # Cookie import/export helpers
```

---

## Writing a custom adapter

```python
from grantpilot.adapters.base import BaseAdapter

class MyPortalAdapter(BaseAdapter):
    name = "myportal"
    login_url = "https://myportal.com/login"

    async def fill(self, page, profile):
        await page.fill('[name="first_name"]', profile["personal"]["full_name"].split()[0])
        await page.fill('[name="project_title"]', profile["research"]["title"])
        # ... map every field
        await self.upload_file(page, '[type="file"]', profile["documents"]["cv"])
        await self.stop_before_submit(page)  # Always call this last
```

---

## Monetization / Roadmap

GrantPilot is **open core**.

| Tier | Price | What you get |
|------|-------|--------------|
| **OSS** | Free | Local runner, 3 portal adapters, basic profile |
| **Pro** | $29/mo | Cloud dashboard, 50+ adapters, AI essay assistant, deadline alerts |
| **Agency** | $199/mo | Multi-client profiles, white-label, API, bulk runs |

→ [Join the waitlist for Pro](https://grantpilot.dev) *(coming soon)*

---

## Contributing

PRs welcome, especially new portal adapters. See `CONTRIBUTING.md`.

---

## License

MIT — use it, fork it, build on it.
