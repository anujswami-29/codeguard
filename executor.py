# ============================================================
# CODEGUARD — Executor
# Only runs AFTER the policy engine gives the green light.
# Performs real file operations on the workspace.
# ============================================================

import os
from intent_model import Intent, ActionType
from logger import get_logger

logger = get_logger("Executor")


class Executor:
    """
    Safe executor — only called when PolicyEngine returns allowed=True.
    Performs real actions on the file system.
    """

    def run(self, intent: Intent) -> str:
        """Execute an approved intent. Returns result message."""
        logger.info(f"Executing approved intent: {intent.action.value} on {intent.target_file}")

        handlers = {
            ActionType.READ:          self._read,
            ActionType.EDIT:          self._edit,
            ActionType.CREATE:        self._create,
            ActionType.ADD_DOCSTRING: self._add_docstring,
            ActionType.FIX_STYLE:     self._fix_style,
        }

        handler = handlers.get(intent.action)
        if not handler:
            return f"No executor found for action: {intent.action.value}"

        result = handler(intent)
        logger.info(f"  ✔ Execution complete: {result}")
        return result

    def _read(self, intent: Intent) -> str:
        if not os.path.exists(intent.target_file):
            return f"File not found: {intent.target_file}"
        with open(intent.target_file, "r") as f:
            content = f.read()
        return f"Read {intent.target_file} ({len(content)} chars):\n\n{content}"

    def _edit(self, intent: Intent) -> str:
        if not intent.content:
            return "Edit failed: no content provided"
        os.makedirs(os.path.dirname(intent.target_file), exist_ok=True)
        with open(intent.target_file, "w") as f:
            f.write(intent.content)
        return f"Edited {intent.target_file} successfully ({len(intent.content)} chars written)"

    def _create(self, intent: Intent) -> str:
        if os.path.exists(intent.target_file):
            return f"File already exists: {intent.target_file}"
        os.makedirs(os.path.dirname(intent.target_file), exist_ok=True)
        content = intent.content or f"# {os.path.basename(intent.target_file)}\n# Created by CodeGuard\n"
        with open(intent.target_file, "w") as f:
            f.write(content)
        return f"Created {intent.target_file} successfully"

    def _add_docstring(self, intent: Intent) -> str:
        if not os.path.exists(intent.target_file):
            return f"File not found: {intent.target_file}"
        with open(intent.target_file, "r") as f:
            lines = f.readlines()

        # Find first function definition and add docstring after it
        new_lines = []
        i = 0
        modified = False
        while i < len(lines):
            new_lines.append(lines[i])
            if lines[i].strip().startswith("def ") and not modified:
                # Get indentation of next line
                if i + 1 < len(lines):
                    indent = len(lines[i + 1]) - len(lines[i + 1].lstrip())
                else:
                    indent = 4
                spaces = " " * (indent if indent > 0 else 4)
                # Check if docstring already exists
                if i + 1 < len(lines) and '"""' not in lines[i + 1]:
                    new_lines.append(f'{spaces}"""Auto-generated docstring by CodeGuard agent."""\n')
                    modified = True
            i += 1

        with open(intent.target_file, "w") as f:
            f.writelines(new_lines)

        status = "added docstring" if modified else "docstring already present"
        return f"Processed {intent.target_file}: {status}"

    def _fix_style(self, intent: Intent) -> str:
        if not os.path.exists(intent.target_file):
            return f"File not found: {intent.target_file}"
        with open(intent.target_file, "r") as f:
            content = f.read()

        # Simple style fixes: trailing whitespace, ensure newline at end
        lines = content.splitlines()
        fixed = [line.rstrip() for line in lines]
        fixed_content = "\n".join(fixed) + "\n"

        with open(intent.target_file, "w") as f:
            f.write(fixed_content)

        return f"Fixed style in {intent.target_file} (trailing whitespace removed, newline ensured)"
