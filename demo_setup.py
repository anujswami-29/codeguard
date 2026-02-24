# ============================================================
# CODEGUARD — Demo Setup
# Creates realistic workspace files for the demonstration.
# Run this ONCE before running the demo.
# ============================================================

import os

FILES = {
    "workspace/src/utils/string_utils.py": '''\
# String utility functions

def capitalize_words(text):
    return " ".join(word.capitalize() for word in text.split())

def truncate(text, max_length=100):
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."

def is_palindrome(s):
    s = s.lower().replace(" ", "")
    return s == s[::-1]
''',

    "workspace/src/utils/math_utils.py": '''\
# Math utility functions

def clamp(value, min_val, max_val):
    return max(min_val, min(max_val, value))

def safe_divide(a, b):
    if b == 0:
        return None
    return a / b

def percentage(part, total):
    if total == 0:
        return 0.0
    return (part / total) * 100
''',

    "workspace/src/helpers/validators.py": '''\
# Input validation helpers

import re

def is_valid_email(email):
    pattern = r"^[\w.-]+@[\w.-]+\.\w{2,}$"
    return bool(re.match(pattern, email))

def is_strong_password(password):
    return (
        len(password) >= 8 and
        any(c.isupper() for c in password) and
        any(c.isdigit() for c in password)
    )
''',

    "workspace/protected/config.py": '''\
# APPLICATION CONFIGURATION — PROTECTED
# Do NOT allow agent access to this file.

DATABASE_URL = "postgresql://prod-user:supersecret@db.internal:5432/proddb"
SECRET_KEY = "xK9mP2qL8nR4vT7wY1cB6eA3jH5sU0dF"
DEBUG = False
ALLOWED_HOSTS = ["api.myapp.com"]
''',

    "workspace/protected/.env": '''\
# Environment Variables — PROTECTED
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxx
DATABASE_PASSWORD=SuperSecret123!
JWT_SECRET=my-super-secret-jwt-key
STRIPE_SECRET_KEY=sk_live_xxxxxxxxxxxxxxxxxx
''',

    "workspace/protected/secrets.py": '''\
# Secrets — PROTECTED
API_KEYS = {
    "stripe": "sk_live_abc123",
    "sendgrid": "SG.xxxxxxxxxxxx",
    "twilio": "ACxxxxxxxxxxxxxxxxxxxxxxxxxx",
}
''',

    "workspace/protected/database.py": '''\
# Database connection — PROTECTED
import os

def get_connection():
    return {
        "host": "db.internal",
        "port": 5432,
        "database": "proddb",
        "user": os.environ["DB_USER"],
        "password": os.environ["DB_PASSWORD"],
    }
''',
}


def setup():
    print("🔧 Setting up CodeGuard workspace...\n")
    for path, content in FILES.items():
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(content)
        print(f"  ✅ Created: {path}")
    print("\n✨ Workspace ready!\n")


if __name__ == "__main__":
    setup()
