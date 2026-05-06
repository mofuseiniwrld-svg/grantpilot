"""Cookie and session helpers — export from Chrome, inject into Playwright."""
import json
from pathlib import Path


def export_chrome_cookies(domain: str, output_path: str) -> list[dict]:
    """
    Export cookies for a domain from Chrome's local storage.
    Requires: pip install browser-cookie3
    """
    try:
        import browser_cookie3
        cookies = browser_cookie3.chrome(domain_name=domain)
        result = [
            {
                "name": c.name,
                "value": c.value,
                "domain": c.domain,
                "path": c.path,
                "secure": c.secure,
                "httpOnly": False,
                "sameSite": "Lax",
            }
            for c in cookies
        ]
        Path(output_path).write_text(json.dumps(result, indent=2))
        print(f"Exported {len(result)} cookies → {output_path}")
        return result
    except ImportError:
        raise ImportError("Run: pip install browser-cookie3")


def load_cookies(path: str) -> list[dict]:
    return json.loads(Path(path).read_text())
