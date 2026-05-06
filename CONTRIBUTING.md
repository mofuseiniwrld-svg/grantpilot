# Contributing to GrantPilot

## Adding a new portal adapter

1. Create `grantpilot/adapters/<portal_name>.py`
2. Subclass `BaseAdapter`
3. Set `name` and `login_url`
4. Implement `fill(page, profile)` — map profile fields to form selectors
5. Always end with `await self.stop_before_submit(page)`
6. Register it in `grantpilot/adapters/__init__.py`
7. Open a PR with a test profile showing it works

## Portal research tips

- Use browser DevTools → Elements to find selector names
- Most portals use `name` or `id` attributes on inputs
- Check for multi-step wizards (click Next between sections)
- Rich text editors (Quill, ProseMirror) need special handling — see `submittable.py`

## Bounties (once Pro launches)

- New stable adapter: **$50 credit** on GrantPilot Pro
- Bug fix with test: **$25 credit**
