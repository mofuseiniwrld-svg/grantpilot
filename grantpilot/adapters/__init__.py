from .awardsplatform import AwardsPlatformAdapter
from .submittable import SubmittableAdapter
from .fluxx import FluxxAdapter

ADAPTERS: dict = {
    "awardsplatform": AwardsPlatformAdapter,
    "submittable": SubmittableAdapter,
    "fluxx": FluxxAdapter,
}

__all__ = ["ADAPTERS", "AwardsPlatformAdapter", "SubmittableAdapter", "FluxxAdapter"]
