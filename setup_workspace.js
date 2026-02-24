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
  "workspace/protected/config.py": `# PROTECTED â€” do not touch
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
  console.log(`âœ… Created: ${filePath}`);
}

console.log("\nâœ¨ Workspace ready!\n");
console.log("Now test the enforce.js script:");
console.log("  node skills/codeguard/scripts/enforce.js add_docstring workspace/src/utils/string_utils.py");
console.log("  node skills/codeguard/scripts/enforce.js edit workspace/protected/config.py");
console.log("  node skills/codeguard/scripts/enforce.js delete workspace/src/utils/math_utils.py");
console.log("  node skills/codeguard/scripts/enforce.js read workspace/src/core/main.py");

