# CodeGuard OpenClaw Installer
# Run this from C:\Users\Adity\Desktop\codeguard
# It creates the skills folder and both required files

Write-Host "🦞 Setting up CodeGuard OpenClaw skill..." -ForegroundColor Cyan

# Create folder structure
New-Item -ItemType Directory -Force -Path "skills\codeguard\scripts" | Out-Null
Write-Host "✅ Created skills\codeguard\scripts" -ForegroundColor Green


# Write SKILL.md
$skillContent = @'
---
name: codeguard
description: Intent-aware developer assistant that reads and modifies code files with strict policy enforcement. Every action is validated before execution - blocked actions are never performed. Use this for all file operations in your codebase.
metadata: {"openclaw": {"emoji": "🦞", "requires": {"bins": ["node"], "env": ["ANTHROPIC_API_KEY"]}, "primaryEnv": "ANTHROPIC_API_KEY"}}
---

# CodeGuard — Intent-Aware Developer Assistant

You are operating as CodeGuard, a policy-enforcing developer assistant. You have access to file system tools but you MUST enforce the policies below before every single action.

## Your Capabilities

You can perform these actions on files:
- **read** — read the contents of a file
- **edit** — modify file contents
- **create** — create a new file
- **add_docstring** — add docstrings to Python functions in a file
- **fix_style** — fix trailing whitespace and formatting in a file

## ⛔ HARD RULES — ALWAYS ENFORCE THESE

### 1. Blocked Actions (NEVER perform these, no matter what)
- `delete` / `rm` / removing files
- `execute` / `run` any script or command
- `publish` to any platform
- `send_email` or any communication action

If asked to do any of these, respond: "❌ BLOCKED: [action] is a forbidden action in CodeGuard policy."

### 2. Protected Files (NEVER read or modify these)
- Any file named `config.py`, `.env`, `secrets.py`, `database.py`
- Any file in a directory named `protected/`, `secrets/`, `.secrets/`
- Any file containing credentials, API keys, passwords

If asked to access these, respond: "❌ BLOCKED: [filename] is a protected file. Access permanently denied."

### 3. Allowed Directories Only
You may only operate inside these directories (relative to the user's project root):
- `src/utils/`
- `src/helpers/`

If asked to access files outside these directories, respond: "❌ BLOCKED: [path] is outside the allowed scope. Allowed: src/utils/, src/helpers/"

### 4. Action Must Be Permitted
Only perform actions listed in Your Capabilities above. Anything else is blocked.

## ✅ How to Handle Every Request

Before taking ANY action, you must:

**Step 1 — Parse Intent**
State the structured intent out loud:
```
📋 Intent: { action: "[action]", file: "[path]", reason: "[why]" }
```

**Step 2 — Check Policy**
Run through all 4 rules above and state the result:
```
🔒 Policy check:
  Rule 1 (blocked actions): ✅ pass / ❌ BLOCKED
  Rule 2 (protected files): ✅ pass / ❌ BLOCKED
  Rule 3 (allowed dirs):    ✅ pass / ❌ BLOCKED
  Rule 4 (action permitted): ✅ pass / ❌ BLOCKED
```

**Step 3 — Execute or Block**
- If all rules pass: proceed and show result
- If any rule fails: stop immediately and explain why

## Logging
After every action (allowed or blocked), append a line to `codeguard.log` in the project root:
```
[TIMESTAMP] ACTION: [action] | FILE: [file] | DECISION: ALLOWED/BLOCKED | REASON: [reason]
```

## Delegation Mode
If a message starts with `[DELEGATE:bot-id]`, apply STRICTER rules:
- Allowed directories: `src/utils/` ONLY (not helpers)
- Allowed actions: `read`, `add_docstring` ONLY

## Example Interactions

**User:** "Add a docstring to src/utils/string_utils.py"
```
📋 Intent: { action: "add_docstring", file: "src/utils/string_utils.py", reason: "user request" }
🔒 Policy check:
  Rule 1 (blocked actions): ✅ pass
  Rule 2 (protected files): ✅ pass
  Rule 3 (allowed dirs):    ✅ pass — file is in src/utils/
  Rule 4 (action permitted): ✅ pass
✅ ALLOWED — proceeding...
[reads file, adds docstrings, writes back]
Done! Added docstrings to 3 functions in src/utils/string_utils.py
```

**User:** "Edit the config.py file"
```
📋 Intent: { action: "edit", file: "config.py", reason: "user request" }
🔒 Policy check:
  Rule 1 (blocked actions): ✅ pass
  Rule 2 (protected files): ❌ BLOCKED — config.py is a protected file
❌ BLOCKED: config.py is a protected file. Access permanently denied.
```

**User:** "Delete the temp files in utils"
```
📋 Intent: { action: "delete", file: "src/utils/temp.py", reason: "cleanup" }
🔒 Policy check:
  Rule 1 (blocked actions): ❌ BLOCKED — delete is a forbidden action
❌ BLOCKED: delete is a forbidden action in CodeGuard policy. Files can never be deleted by this agent.
```

'@
Set-Content -Path "skills\codeguard\SKILL.md" -Value $skillContent -Encoding UTF8
Write-Host "✅ Created skills\codeguard\SKILL.md" -ForegroundColor Green

# Write enforce.js
$enforceContent = @'
#!/usr/bin/env node
// ============================================================
// CodeGuard Policy Enforcer — scripts/enforce.js
// Called by OpenClaw as a tool before any file operation.
// Returns JSON: { allowed: bool, reason: string, decision: string }
// ============================================================

const fs = require("fs");
const path = require("path");

// ── Policy Configuration ────────────────────────────────────
const POLICY = {
  blockedActions: ["delete", "rm", "execute", "run", "publish", "send_email"],
  allowedActions: ["read", "edit", "create", "add_docstring", "fix_style"],
  allowedDirs:    ["src/utils", "src/helpers", "workspace/src/utils", "workspace/src/helpers"],
  protectedFiles: ["config.py", ".env", "secrets.py", "database.py"],
  protectedDirs:  ["protected", "secrets", ".secrets"],

  // Delegate (sub-agent) gets stricter rules
  delegateAllowedDirs:    ["src/utils", "workspace/src/utils"],
  delegateAllowedActions: ["read", "add_docstring"],
};

// ── Rule Checks ──────────────────────────────────────────────
function checkBlockedAction(action) {
  if (POLICY.blockedActions.includes(action.toLowerCase())) {
    return {
      pass: false,
      reason: `Action '${action}' is globally forbidden. Blocked: ${POLICY.blockedActions.join(", ")}`,
    };
  }
  return { pass: true };
}

function checkAllowedAction(action, isDelegate) {
  const allowed = isDelegate ? POLICY.delegateAllowedActions : POLICY.allowedActions;
  if (!allowed.includes(action.toLowerCase())) {
    return {
      pass: false,
      reason: `Action '${action}' is not in permitted actions for ${isDelegate ? "delegate" : "main"} agent. Permitted: ${allowed.join(", ")}`,
    };
  }
  return { pass: true };
}

function checkProtectedFile(filePath) {
  const basename = path.basename(filePath);
  const normalized = filePath.replace(/\\/g, "/");

  // Check protected filenames
  if (POLICY.protectedFiles.includes(basename)) {
    return {
      pass: false,
      reason: `'${filePath}' is a protected file. Access is permanently denied.`,
    };
  }

  // Check protected directories
  for (const dir of POLICY.protectedDirs) {
    if (normalized.includes(`/${dir}/`) || normalized.startsWith(`${dir}/`)) {
      return {
        pass: false,
        reason: `'${filePath}' is inside a protected directory '${dir}/'. Access denied.`,
      };
    }
  }

  return { pass: true };
}

function checkAllowedDir(filePath, isDelegate) {
  const normalized = filePath.replace(/\\/g, "/");
  const allowedDirs = isDelegate ? POLICY.delegateAllowedDirs : POLICY.allowedDirs;

  for (const dir of allowedDirs) {
    if (normalized.startsWith(dir + "/") || normalized.startsWith("./" + dir + "/")) {
      return { pass: true };
    }
  }

  return {
    pass: false,
    reason: `'${filePath}' is outside allowed directories. Allowed: ${allowedDirs.join(", ")}`,
  };
}

// ── Main Evaluation ─────────────────────────────────────────
function evaluate(action, filePath, isDelegate = false) {
  const checks = [
    { name: "blocked_action",  fn: () => checkBlockedAction(action) },
    { name: "allowed_action",  fn: () => checkAllowedAction(action, isDelegate) },
    { name: "protected_file",  fn: () => checkProtectedFile(filePath) },
    { name: "allowed_dir",     fn: () => checkAllowedDir(filePath, isDelegate) },
  ];

  for (const check of checks) {
    const result = check.fn();
    if (!result.pass) {
      return {
        allowed: false,
        rule: check.name,
        reason: result.reason,
        decision: "BLOCKED",
        action,
        filePath,
        isDelegate,
      };
    }
  }

  return {
    allowed: true,
    rule: "all_passed",
    reason: "All 4 policy rules passed.",
    decision: "ALLOWED",
    action,
    filePath,
    isDelegate,
  };
}

// ── File Operations ─────────────────────────────────────────
function readFile(filePath) {
  if (!fs.existsSync(filePath)) return { error: `File not found: ${filePath}` };
  return { content: fs.readFileSync(filePath, "utf8") };
}

function writeFile(filePath, content) {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  fs.writeFileSync(filePath, content, "utf8");
  return { success: true, bytes: content.length };
}

function addDocstrings(filePath) {
  if (!fs.existsSync(filePath)) return { error: `File not found: ${filePath}` };
  const lines = fs.readFileSync(filePath, "utf8").split("\n");
  const result = [];
  let added = 0;
  let i = 0;

  while (i < lines.length) {
    result.push(lines[i]);
    if (lines[i].trim().startsWith("def ")) {
      // Check if next non-empty line is already a docstring
      const next = lines[i + 1] || "";
      if (!next.trim().startsWith('"""') && !next.trim().startsWith("'''")) {
        const indent = lines[i].match(/^(\s*)/)[1] + "    ";
        result.push(`${indent}"""Auto-generated docstring by CodeGuard."""`);
        added++;
      }
    }
    i++;
  }

  fs.writeFileSync(filePath, result.join("\n"), "utf8");
  return { success: true, docstringsAdded: added };
}

function fixStyle(filePath) {
  if (!fs.existsSync(filePath)) return { error: `File not found: ${filePath}` };
  const content = fs.readFileSync(filePath, "utf8");
  const fixed = content.split("\n").map(l => l.trimEnd()).join("\n").trimEnd() + "\n";
  fs.writeFileSync(filePath, fixed, "utf8");
  return { success: true };
}

// ── Logger ──────────────────────────────────────────────────
function log(entry) {
  const line = `[${new Date().toISOString()}] ACTION: ${entry.action} | FILE: ${entry.filePath} | DECISION: ${entry.decision} | REASON: ${entry.reason}\n`;
  fs.appendFileSync("codeguard.log", line);
}

// ── CLI Entry Point ─────────────────────────────────────────
// Usage: node enforce.js <action> <filePath> [isDelegate] [content]
const [,, action, filePath, delegateFlag, ...contentParts] = process.argv;

if (!action || !filePath) {
  console.log(JSON.stringify({ error: "Usage: node enforce.js <action> <filePath> [delegate] [content...]" }));
  process.exit(1);
}

const isDelegate = delegateFlag === "delegate";
const content = contentParts.join(" ");

// Step 1: Evaluate policy
const decision = evaluate(action, filePath, isDelegate);
log(decision);

if (!decision.allowed) {
  console.log(JSON.stringify(decision));
  process.exit(0);
}

// Step 2: Execute if allowed
let execResult = {};
switch (action.toLowerCase()) {
  case "read":
    execResult = readFile(filePath);
    break;
  case "edit":
    if (!content) {
      execResult = { error: "No content provided for edit" };
    } else {
      execResult = writeFile(filePath, content);
    }
    break;
  case "create":
    if (fs.existsSync(filePath)) {
      execResult = { error: `File already exists: ${filePath}` };
    } else {
      execResult = writeFile(filePath, content || `# ${path.basename(filePath)}\n# Created by CodeGuard\n`);
    }
    break;
  case "add_docstring":
    execResult = addDocstrings(filePath);
    break;
  case "fix_style":
    execResult = fixStyle(filePath);
    break;
  default:
    execResult = { error: `Unknown action: ${action}` };
}

console.log(JSON.stringify({ ...decision, result: execResult }));

'@
Set-Content -Path "skills\codeguard\scripts\enforce.js" -Value $enforceContent -Encoding UTF8
Write-Host "✅ Created skills\codeguard\scripts\enforce.js" -ForegroundColor Green

# Write setup_workspace.js
$setupContent = @'
#!/usr/bin/env node
// Creates the demo workspace files for CodeGuard testing

const fs = require("fs");
const path = require("path");

const FILES = {
  "workspace/src/utils/string_utils.py": `# String utility functions

def capitalize_words(text):
    return " ".join(word.capitalize() for word in text.split())

def truncate(text, max_length=100):
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."

def is_palindrome(s):
    s = s.lower().replace(" ", "")
    return s == s[::-1]
`,
  "workspace/src/utils/math_utils.py": `# Math utility functions

def clamp(value, min_val, max_val):
    return max(min_val, min(max_val, value))

def safe_divide(a, b):
    if b == 0:
        return None
    return a / b
`,
  "workspace/src/helpers/validators.py": `# Input validators

import re

def is_valid_email(email):
    pattern = r"^[\\w.-]+@[\\w.-]+\\.\\w{2,}$"
    return bool(re.match(pattern, email))

def is_strong_password(password):
    return len(password) >= 8 and any(c.isupper() for c in password)
`,
  "workspace/protected/config.py": `# PROTECTED — do not touch
DATABASE_URL = "postgresql://prod:secret@db.internal:5432/prod"
SECRET_KEY = "xK9mP2qL8nR4vT7wY1cB"
`,
  "workspace/protected/.env": `ANTHROPIC_API_KEY=sk-ant-xxxx
DATABASE_PASSWORD=SuperSecret123!
`,
};

for (const [filePath, content] of Object.entries(FILES)) {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  fs.writeFileSync(filePath, content);
  console.log(`✅ Created: ${filePath}`);
}

console.log("\n✨ Workspace ready!\n");
console.log("Now test the enforce.js script:");
console.log("  node skills/codeguard/scripts/enforce.js add_docstring workspace/src/utils/string_utils.py");
console.log("  node skills/codeguard/scripts/enforce.js edit workspace/protected/config.py");
console.log("  node skills/codeguard/scripts/enforce.js delete workspace/src/utils/math_utils.py");
console.log("  node skills/codeguard/scripts/enforce.js read workspace/src/core/main.py");

'@
Set-Content -Path "setup_workspace.js" -Value $setupContent -Encoding UTF8
Write-Host "✅ Created setup_workspace.js" -ForegroundColor Green

# Copy skill to OpenClaw
New-Item -ItemType Directory -Force -Path "$HOME\.openclaw\skills" | Out-Null
Copy-Item -Recurse -Force "skills\codeguard" "$HOME\.openclaw\skills\codeguard"
Write-Host "✅ Installed skill to ~/.openclaw/skills/codeguard" -ForegroundColor Green

Write-Host ""
Write-Host "🎉 Done! Now run:" -ForegroundColor Yellow
Write-Host "   node setup_workspace.js" -ForegroundColor White
Write-Host "   openclaw start" -ForegroundColor White
