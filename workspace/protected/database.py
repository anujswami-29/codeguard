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
