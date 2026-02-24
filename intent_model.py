# ============================================================
# CODEGUARD — Intent Model
# Every agent action is converted into this structured format
# BEFORE any execution happens. Nothing runs without an intent.
# ============================================================

from dataclasses import dataclass
from typing import Optional
from enum import Enum


class ActionType(str, Enum):
    READ         = "read"
    EDIT         = "edit"
    CREATE       = "create"
    DELETE       = "delete"
    ADD_DOCSTRING = "add_docstring"
    FIX_STYLE    = "fix_style"
    EXECUTE      = "execute"
    PUBLISH      = "publish"
    SEND_EMAIL   = "send_email"


@dataclass
class Intent:
    """
    Structured representation of ONE agent action.
    Produced by the reasoning layer, validated by the policy engine
    before any real execution happens.
    """
    action: ActionType          # What the agent wants to do
    target_file: str            # Which file to act on
    scope: str                  # Which module/directory (e.g. 'utils')
    reason: str                 # Why the agent wants to do this
    content: Optional[str] = None   # New content (for edit/create)
    delegated: bool = False         # Is this from a sub-agent?
    delegate_id: Optional[str] = None  # Which sub-agent issued this

    def to_dict(self) -> dict:
        return {
            "action": self.action.value,
            "target_file": self.target_file,
            "scope": self.scope,
            "reason": self.reason,
            "delegated": self.delegated,
            "delegate_id": self.delegate_id,
        }

    def __str__(self):
        prefix = f"[DELEGATE:{self.delegate_id}] " if self.delegated else ""
        return (f"{prefix}Intent({self.action.value} → "
                f"{self.target_file} | reason: {self.reason})")
