# ============================================================
# CODEGUARD — Policy Configuration
# All rules live here. Change this file to adjust permissions.
# ============================================================

from dataclasses import dataclass, field
from typing import List

@dataclass
class PolicyConfig:
    # Directories the agent is ALLOWED to read/write
    allowed_directories: List[str] = field(default_factory=lambda: [
        "workspace/src/utils",
        "workspace/src/helpers",
    ])

    # Files that are ALWAYS blocked, no matter what
    protected_files: List[str] = field(default_factory=lambda: [
        "workspace/protected/config.py",
        "workspace/protected/.env",
        "workspace/protected/secrets.py",
        "workspace/protected/database.py",
    ])

    # Actions the main agent can perform
    allowed_actions: List[str] = field(default_factory=lambda: [
        "read", "edit", "create", "add_docstring", "fix_style"
    ])

    # Actions that are always blocked
    blocked_actions: List[str] = field(default_factory=lambda: [
        "delete", "execute", "publish", "send_email"
    ])

    # Sub-agent (delegated) has EVEN more restricted permissions
    delegate_allowed_directories: List[str] = field(default_factory=lambda: [
        "workspace/src/utils",   # only utils, not helpers
    ])

    delegate_allowed_actions: List[str] = field(default_factory=lambda: [
        "read", "add_docstring"  # sub-agent can only read & add docstrings
    ])


# Singleton — import this everywhere
POLICY = PolicyConfig()
