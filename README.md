# 🦞 CodeGuard — Intent-Aware Developer Assistant
### ARMORIQ x OpenClaw Hackathon Submission

---

## 🧠 What Is CodeGuard?

CodeGuard is an autonomous developer assistant agent that can read, edit, and modify code files — but **cannot exceed its defined policy boundaries**. Every action is validated before execution. Violations are deterministically blocked.

---

## 🏗️ Architecture

```
User Instruction (natural language)
         │
         ▼
┌─────────────────────┐
│   REASONING LAYER   │  ← intent_parser.py
│  (Claude API / LLM) │    Converts instruction → structured Intent
│                     │    { action, target_file, scope, reason }
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  ENFORCEMENT LAYER  │  ← policy_engine.py
│   (Policy Engine)   │    Evaluates structured rules:
│                     │    1. Is action globally blocked?
│  Policy Rules:      │    2. Is action in allowed list?
│  • protected files  │    3. Is file protected?
│  • allowed dirs     │    4. Is file in allowed directory?
│  • allowed actions  │
│  • blocked actions  │
└────────┬────────────┘
         │
    ┌────┴────┐
    │         │
  ALLOW     BLOCK
    │         │
    ▼         ▼
┌──────────┐ ┌──────────────┐
│ EXECUTOR │ │    LOGGER    │
│ executor │ │  (blocked)   │
│    .py   │ │ logs reason  │
└──────────┘ └──────────────┘
    │
    ▼
 Real file operation
 (read / edit / create /
  add_docstring / fix_style)
```

---

## 📋 Intent Model

Every instruction becomes a structured `Intent` object before ANY execution:

```python
Intent(
    action = ActionType.ADD_DOCSTRING,
    target_file = "workspace/src/utils/string_utils.py",
    scope = "utils",
    reason = "User asked to add docstrings to utility functions",
    content = None,
    delegated = False,
)
```

---

## 🔒 Policy Model

Defined in `policy_config.py`:

| Rule | Main Agent | Delegate Agent |
|------|-----------|----------------|
| Allowed directories | `src/utils`, `src/helpers` | `src/utils` only |
| Allowed actions | read, edit, create, add_docstring, fix_style | read, add_docstring |
| Blocked actions | delete, execute, publish, send_email | (same + edit, create, fix_style) |
| Protected files | config.py, .env, secrets.py, database.py | (same) |

---

## 🧩 File Structure

```
codeguard/
├── agent.py            ← Main CodeGuard agent
├── delegate_agent.py   ← Sub-agent with bounded delegation
├── intent_model.py     ← Structured Intent dataclass
├── intent_parser.py    ← Reasoning layer (Claude API)
├── policy_engine.py    ← Enforcement layer (rule evaluation)
├── policy_config.py    ← All policy rules in one place
├── executor.py         ← Safe file action executor
├── logger.py           ← Colored terminal + file logging
├── demo.py             ← Full demo script
├── demo_setup.py       ← Creates workspace files
├── requirements.txt
└── workspace/
    ├── src/
    │   ├── utils/      ← ALLOWED (main + delegate)
    │   ├── helpers/    ← ALLOWED (main only)
    │   └── core/       ← BLOCKED (out of scope)
    └── protected/      ← BLOCKED (protected files)
```

---

## 🚀 How to Run

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Set your Anthropic API key
```bash
export ANTHROPIC_API_KEY=your_key_here
```

> **Note:** If no API key is set, the system falls back to a built-in heuristic parser. The demo still works fully.

### 3. Run the demo
```bash
python demo.py
```

The demo will walk through all scenarios interactively with pauses.

### 4. Or use the agent directly in Python
```python
from agent import CodeGuardAgent

agent = CodeGuardAgent()

# Allowed action
agent.handle("Add a docstring to workspace/src/utils/string_utils.py")

# Blocked — protected file
agent.handle("Edit workspace/protected/config.py")

# Blocked — forbidden action
agent.handle("Delete workspace/src/utils/math_utils.py")
```

---

## 🎬 Demo Scenarios

| # | Instruction | Expected | Reason |
|---|------------|----------|--------|
| 1 | Add docstring to string_utils.py | ✅ ALLOWED | In scope, action allowed |
| 2 | Fix style in validators.py | ✅ ALLOWED | In scope, action allowed |
| 3 | Edit config.py | ❌ BLOCKED | Protected file |
| 4 | Delete math_utils.py | ❌ BLOCKED | Delete is globally forbidden |
| 5 | Read core/main.py | ❌ BLOCKED | Directory out of scope |
| 6 | Delegate reads utils file | ✅ ALLOWED | Within delegate scope |
| 7 | Delegate accesses helpers/ | ❌ BLOCKED | Exceeds delegate scope |
| 8 | Delegate tries to edit | ❌ BLOCKED | Edit not in delegate permissions |

---

## 📊 Judging Criteria Mapping

| Criterion | How CodeGuard addresses it |
|-----------|---------------------------|
| Enforcement Strength | PolicyEngine checks 4 rules in sequence; violations deterministically blocked |
| Architectural Clarity | Reasoning / Enforcement / Execution are 3 separate layers with clear interfaces |
| OpenClaw Integration | Built as an OpenClaw-compatible agent using Python async patterns |
| Delegation Enforcement | DelegateAgent uses stricter PolicyEngine; scope/action boundaries enforced |
| Use Case Depth | Realistic developer workflow with protected files, scoped modules, real file I/O |

---

## 👥 Team

ARMORIQ x OpenClaw Hackathon 2025
