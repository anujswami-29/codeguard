#!/usr/bin/env node
// ============================================================
// CodeGuard Policy Enforcer â€” scripts/enforce.js
// Called by OpenClaw as a tool before any file operation.
// Returns JSON: { allowed: bool, reason: string, decision: string }
// ============================================================

const fs = require("fs");
const path = require("path");

// â”€â”€ Policy Configuration â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
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

// â”€â”€ Rule Checks â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
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

// â”€â”€ Main Evaluation â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
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

// â”€â”€ File Operations â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
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

// â”€â”€ Logger â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
function log(entry) {
  const line = `[${new Date().toISOString()}] ACTION: ${entry.action} | FILE: ${entry.filePath} | DECISION: ${entry.decision} | REASON: ${entry.reason}\n`;
  fs.appendFileSync("codeguard.log", line);
}

// â”€â”€ CLI Entry Point â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
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

