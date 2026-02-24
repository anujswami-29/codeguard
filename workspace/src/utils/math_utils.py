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
