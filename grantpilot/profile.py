"""Profile management — load, validate, and merge user profiles."""
import json
from pathlib import Path
from typing import Any
from pydantic import BaseModel, EmailStr, field_validator


class Reference(BaseModel):
    name: str
    email: str
    institution: str
    relationship: str = ""


class Documents(BaseModel):
    cv: str = ""
    writing_sample: str = ""
    research_proposal: str = ""
    transcript: str = ""


class Profile(BaseModel):
    personal: dict[str, Any]
    research: dict[str, Any] = {}
    essays: dict[str, str] = {}
    references: list[Reference] = []
    documents: Documents = Documents()
    extras: dict[str, Any] = {}

    @classmethod
    def load(cls, path: str | Path) -> "Profile":
        data = json.loads(Path(path).read_text())
        return cls(**data)

    def get(self, key: str, default: Any = "") -> Any:
        """Dot-path accessor: profile.get('personal.full_name')"""
        parts = key.split(".")
        obj: Any = self
        for part in parts:
            if isinstance(obj, dict):
                obj = obj.get(part, default)
            elif isinstance(obj, BaseModel):
                obj = getattr(obj, part, default)
            else:
                return default
        return obj or default

    def merge(self, overrides: dict) -> "Profile":
        """Return new profile with overrides applied (non-destructive)."""
        data = self.model_dump()
        _deep_merge(data, overrides)
        return Profile(**data)


def _deep_merge(base: dict, updates: dict) -> None:
    for k, v in updates.items():
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            _deep_merge(base[k], v)
        else:
            base[k] = v
