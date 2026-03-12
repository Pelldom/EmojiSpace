"""
Centralized input handling. All input passes through get_choice().
Reject invalid input cleanly; never crash on bad input.
"""

from __future__ import annotations


def get_choice(max_option: int, prompt: str = "Select: ") -> int | None:
    """
    Read a numeric choice from the user. Valid range: 0 to max_option (inclusive).
    Returns the integer choice, or None if input was invalid or empty after strip.
    Does not crash on bad input; returns None so caller can retry or interpret 0 as Back.
    """
    if max_option < 0:
        return None
    try:
        raw = input(prompt).strip()
        if raw == "":
            return None
        value = int(raw)
        if 0 <= value <= max_option:
            return value
        return None
    except ValueError:
        return None
    except EOFError:
        return None


def get_choice_required(max_option: int, prompt: str = "Select: ") -> int:
    """
    Same as get_choice but only returns when a valid choice is made.
    Loops until 0..max_option is entered. Use when you must have a selection.
    """
    while True:
        c = get_choice(max_option, prompt)
        if c is not None:
            return c
        print("Invalid choice. Please enter a number from 0 to {}.".format(max_option))
