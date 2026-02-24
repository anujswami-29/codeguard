# ============================================================
# CODEGUARD — Intent Parser (Reasoning Layer)
# Converts natural language instructions into structured Intents.
# This is the REASONING layer — separated from execution.
# Uses the Anthropic API (Claude) to understand instructions.
# ============================================================

import json
import os
import re
from intent_model import Intent, ActionType
from logger import get_logger

logger = get_logger("IntentParser")


SYSTEM_PROMPT = """You are the reasoning layer of CodeGuard, a safe developer assistant.

Your job is to parse a user instruction into a structured JSON intent object.
You must output ONLY valid JSON — no explanation, no markdown, no code blocks.

The JSON must have these fields:
{
  "action": one of: read, edit, create, delete, add_docstring, fix_style, execute, publish, send_email
  "target_file": the file path to act on (e.g. "workspace/src/utils/helpers.py")
  "scope": which module this touches (e.g. "utils", "helpers", "core", "protected")
  "reason": brief reason why this action is needed
  "content": (optional) new file content if action is edit or create
}

Rules for inferring the file path:
- If user says "utils" or "helper" → use workspace/src/utils/ or workspace/src/helpers/
- If user says "config", "env", "secrets", "database" → use workspace/protected/
- Always use realistic .py file paths

Be accurate. Extract exactly what the user asked for.
"""


def parse_intent(instruction: str, delegated: bool = False, delegate_id: str = None) -> Intent:
    """
    Uses Claude to convert a natural language instruction into a structured Intent.
    Falls back to a heuristic parser if the API is unavailable.
    """
    logger.info(f"Parsing instruction: '{instruction}'")

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=500,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": instruction}]
        )

        raw = response.content[0].text.strip()
        # Strip markdown code fences if present
        raw = re.sub(r"```json|```", "", raw).strip()
        data = json.loads(raw)

    except Exception as e:
        logger.warning(f"API parse failed ({e}), using heuristic parser")
        data = _heuristic_parse(instruction)

    # Convert to Intent object
    try:
        action = ActionType(data.get("action", "read"))
    except ValueError:
        action = ActionType.READ

    intent = Intent(
        action=action,
        target_file=data.get("target_file", "workspace/src/utils/unknown.py"),
        scope=data.get("scope", "unknown"),
        reason=data.get("reason", instruction),
        content=data.get("content"),
        delegated=delegated,
        delegate_id=delegate_id,
    )

    logger.info(f"Parsed intent: {intent}")
    return intent


def _heuristic_parse(instruction: str) -> dict:
    """Fallback rule-based parser if the API is unavailable."""
    instruction_lower = instruction.lower()

    # Determine action
    action = "read"
    if any(w in instruction_lower for w in ["add docstring", "docstring"]):
        action = "add_docstring"
    elif any(w in instruction_lower for w in ["edit", "modify", "update", "change", "fix style", "clean"]):
        action = "edit"
    elif any(w in instruction_lower for w in ["create", "make", "new"]):
        action = "create"
    elif any(w in instruction_lower for w in ["delete", "remove", "rm"]):
        action = "delete"
    elif any(w in instruction_lower for w in ["fix style", "style", "format"]):
        action = "fix_style"
    elif any(w in instruction_lower for w in ["execute", "run"]):
        action = "execute"
    elif "publish" in instruction_lower:
        action = "publish"

    # Determine file path
    if any(w in instruction_lower for w in ["config", "configuration"]):
        target = "workspace/protected/config.py"
        scope = "protected"
    elif any(w in instruction_lower for w in ["secret", ".env", "env"]):
        target = "workspace/protected/.env"
        scope = "protected"
    elif any(w in instruction_lower for w in ["database", "db"]):
        target = "workspace/protected/database.py"
        scope = "protected"
    elif "helper" in instruction_lower:
        target = "workspace/src/helpers/helpers.py"
        scope = "helpers"
    elif "util" in instruction_lower:
        target = "workspace/src/utils/utils.py"
        scope = "utils"
    elif "core" in instruction_lower:
        target = "workspace/src/core/main.py"
        scope = "core"
    else:
        target = "workspace/src/utils/utils.py"
        scope = "utils"

    return {
        "action": action,
        "target_file": target,
        "scope": scope,
        "reason": instruction,
    }
