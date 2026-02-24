# ============================================================
# CODEGUARD — Logger
# Every decision (allow/block) is recorded here.
# This provides the traceability required by the rubric.
# ============================================================

import logging
import os
from datetime import datetime

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, f"codeguard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

# Color codes for terminal
COLORS = {
    "GREEN":  "\033[92m",
    "RED":    "\033[91m",
    "YELLOW": "\033[93m",
    "CYAN":   "\033[96m",
    "BOLD":   "\033[1m",
    "RESET":  "\033[0m",
    "DIM":    "\033[2m",
}


class ColorFormatter(logging.Formatter):
    LEVEL_COLORS = {
        logging.DEBUG:    COLORS["DIM"],
        logging.INFO:     COLORS["CYAN"],
        logging.WARNING:  COLORS["RED"],
        logging.ERROR:    COLORS["RED"] + COLORS["BOLD"],
        logging.CRITICAL: COLORS["RED"] + COLORS["BOLD"],
    }

    def format(self, record):
        color = self.LEVEL_COLORS.get(record.levelno, "")
        reset = COLORS["RESET"]
        timestamp = datetime.now().strftime("%H:%M:%S")
        return (f"{COLORS['DIM']}[{timestamp}]{reset} "
                f"{color}[{record.name}]{reset} {record.getMessage()}")


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger  # Already configured

    logger.setLevel(logging.DEBUG)

    # Console handler (colored)
    console = logging.StreamHandler()
    console.setFormatter(ColorFormatter())
    console.setLevel(logging.DEBUG)
    logger.addHandler(console)

    # File handler (plain text, for submission)
    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setFormatter(logging.Formatter(
        "[%(asctime)s] [%(name)s] %(levelname)s: %(message)s"
    ))
    file_handler.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)

    return logger


def print_banner(text: str, color: str = "CYAN"):
    c = COLORS.get(color, "")
    r = COLORS["RESET"]
    b = COLORS["BOLD"]
    width = 60
    print(f"\n{c}{b}{'=' * width}{r}")
    print(f"{c}{b}  {text}{r}")
    print(f"{c}{b}{'=' * width}{r}\n")


def print_decision(allowed: bool, message: str):
    if allowed:
        print(f"  {COLORS['GREEN']}{COLORS['BOLD']}✅ ALLOWED{COLORS['RESET']}  {message}")
    else:
        print(f"  {COLORS['RED']}{COLORS['BOLD']}❌ BLOCKED{COLORS['RESET']}  {message}")
