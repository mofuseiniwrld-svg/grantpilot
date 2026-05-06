"""Portal adapters registry."""
from .awardsplatform import AwardsPlatformAdapter
from .submittable import SubmittableAdapter

ADAPTERS = {
    "awardsplatform": AwardsPlatformAdapter,
    "submittable": SubmittableAdapter,
}

def get_adapter(name: str):
    adapter_cls = ADAPTERS.get(name)
    if not adapter_cls:
        raise ValueError(
            f"Unknown portal: {name!r}\n"
            f"Available: {list(ADAPTERS.keys())}\n"
            f"To add a new portal: subclass BaseAdapter in grantpilot/adapters/"
        )
    return adapter_cls()
