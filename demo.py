#!/usr/bin/env python3
# ============================================================
# CODEGUARD — Full Demo
# Runs all scenarios for the hackathon presentation.
# Shows: allowed actions, blocked actions, delegation bonus.
# ============================================================

import os
import sys
import time

# Make sure we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from demo_setup import setup
from agent import CodeGuardAgent
from logger import print_banner, COLORS


def pause(msg="Press Enter to continue..."):
    input(f"\n  {COLORS['DIM']}{msg}{COLORS['RESET']}\n")


def run_demo():
    # ── Setup workspace
    setup()
    time.sleep(0.5)

    agent = CodeGuardAgent()

    print_banner("CODEGUARD DEMO — ARMORIQ x OPENCLAW HACKATHON", color="GREEN")
    print("""
  CodeGuard is an intent-aware developer assistant.
  Every action goes through:
    1. 📋 Reasoning Layer  → parse instruction to structured intent
    2. 🔒 Enforcement Layer → evaluate against policy rules
    3. ⚙️  Execution Layer   → only run if all rules pass
  
  Watch for ✅ ALLOWED and ❌ BLOCKED decisions below.
""")

    pause("Ready? Press Enter to start the demo...")

    # ══════════════════════════════════════════════════════════
    # SCENARIO 1: ALLOWED — Add docstring to utils file
    # ══════════════════════════════════════════════════════════
    print_banner("SCENARIO 1 — ALLOWED ACTION", color="GREEN")
    print("  Instruction: Add a docstring to the string_utils.py file\n")

    agent.handle("Add a docstring to workspace/src/utils/string_utils.py")

    pause()

    # ══════════════════════════════════════════════════════════
    # SCENARIO 2: ALLOWED — Fix style in helpers
    # ══════════════════════════════════════════════════════════
    print_banner("SCENARIO 2 — ALLOWED ACTION", color="GREEN")
    print("  Instruction: Fix the style/formatting in validators.py\n")

    agent.handle("Fix style in workspace/src/helpers/validators.py")

    pause()

    # ══════════════════════════════════════════════════════════
    # SCENARIO 3: BLOCKED — Protected file access
    # ══════════════════════════════════════════════════════════
    print_banner("SCENARIO 3 — BLOCKED: PROTECTED FILE", color="RED")
    print("  Instruction: Edit the config.py file\n")

    agent.handle("Edit workspace/protected/config.py")

    pause()

    # ══════════════════════════════════════════════════════════
    # SCENARIO 4: BLOCKED — Forbidden action (delete)
    # ══════════════════════════════════════════════════════════
    print_banner("SCENARIO 4 — BLOCKED: FORBIDDEN ACTION", color="RED")
    print("  Instruction: Delete temp files in utils\n")

    agent.handle("Delete workspace/src/utils/math_utils.py")

    pause()

    # ══════════════════════════════════════════════════════════
    # SCENARIO 5: BLOCKED — Out of scope directory
    # ══════════════════════════════════════════════════════════
    print_banner("SCENARIO 5 — BLOCKED: OUT OF SCOPE DIRECTORY", color="RED")
    print("  Instruction: Read the core module\n")

    agent.handle("Read workspace/src/core/main.py")

    pause()

    # ══════════════════════════════════════════════════════════
    # BONUS: DELEGATION SCENARIOS
    # ══════════════════════════════════════════════════════════
    print_banner("BONUS — BOUNDED DELEGATION", color="CYAN")
    print("""
  Main agent spawns a delegate sub-agent.
  Delegate has FEWER permissions:
    ✅ Can only access: workspace/src/utils (not helpers)
    ✅ Can only: read, add_docstring (not edit, fix_style, create)
  
  Main agent CANNOT grant more than it owns.
""")
    pause("Press Enter to see delegation...")

    # Spawn the delegate
    delegate = agent.spawn_delegate(
        delegate_id="docstring-bot-v1",
        scope="workspace/src/utils"
    )

    # DELEGATION ALLOWED: delegate reads a utils file
    print_banner("DELEGATION SCENARIO 1 — ALLOWED", color="GREEN")
    print("  Delegate instruction: Read math_utils.py\n")
    agent.delegate_instruction("docstring-bot-v1", "Read workspace/src/utils/math_utils.py")

    pause()

    # DELEGATION BLOCKED: delegate tries to access helpers (out of its scope)
    print_banner("DELEGATION SCENARIO 2 — BLOCKED: EXCEEDS GRANTED SCOPE", color="RED")
    print("  Delegate instruction: Add docstring to validators.py (in helpers — NOT allowed for delegate)\n")
    agent.delegate_instruction("docstring-bot-v1", "Add docstring to workspace/src/helpers/validators.py")

    pause()

    # DELEGATION BLOCKED: delegate tries to edit (not in its action list)
    print_banner("DELEGATION SCENARIO 3 — BLOCKED: ACTION EXCEEDS DELEGATION", color="RED")
    print("  Delegate instruction: Edit string_utils.py (edit not allowed for delegate)\n")
    agent.delegate_instruction("docstring-bot-v1", "Edit workspace/src/utils/string_utils.py")

    pause()

    # ══════════════════════════════════════════════════════════
    # SUMMARY
    # ══════════════════════════════════════════════════════════
    print_banner("DEMO COMPLETE — SUMMARY", color="GREEN")
    print(f"""
  ✅ ALLOWED ACTIONS DEMONSTRATED:
     • Added docstring to utils/string_utils.py
     • Fixed style in helpers/validators.py
     • Delegate read utils/math_utils.py

  ❌ BLOCKED ACTIONS DEMONSTRATED:
     • Edit protected/config.py          → PROTECTED FILE
     • Delete utils/math_utils.py        → FORBIDDEN ACTION
     • Read src/core/main.py             → OUT OF SCOPE
     • Delegate access helpers/          → EXCEEDS DELEGATE SCOPE
     • Delegate edit action              → ACTION EXCEEDS DELEGATION

  🏗️  ARCHITECTURE:
     • Reasoning Layer  : Claude API parses natural language → structured Intent
     • Enforcement Layer: PolicyEngine evaluates rules deterministically
     • Execution Layer  : Executor only runs after policy approval
     • Delegation Bonus : Sub-agents with bounded, stricter permissions

  📁 Logs saved to: logs/
""")


if __name__ == "__main__":
    run_demo()
