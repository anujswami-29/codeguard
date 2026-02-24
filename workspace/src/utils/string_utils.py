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
