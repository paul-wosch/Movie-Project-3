"""Make the cli output more appealing

Main features:
- colored text
- clear screen
- print dividers

Tag based use for inline text (no extra print statement):
- in an f string use as follows
- print(f"{ERROR}test{OFF}") or print(f"{module.ERROR}test{module.OFF}")
- the Following tags are available: INFO, ERROR, PROMPT, DEFAULT, OFF

Alternative (old) way to use:
- color_on(color_name)
- color_off()
- create a new line with optional argument inline=False
"""
import os


def clear_screen():
    """Clear the terminal screen from previous output."""
    os.system('cls' if os.name == 'nt' else 'clear')


def match_color(text_color):
    """Translate color names to their corresponding ANSI escape codes."""
    colors = {"black": "0;90",
              "red": "0;91",
              "green": "0;92",
              "yellow": "0;93",
              "blue": "0;94",
              "purple": "0;95",
              "cyan": "0;96",
              "white": "0;97",
              "grey": "0;37m",
              }
    return colors.get(text_color, None)


def color_on(text_color=None, inline=True):
    """Set color for the succeeding text."""
    if match_color(text_color):
        if not inline:
            return print(f"\033[{match_color(text_color)}m", end="")
    return f"\033[{match_color(text_color)}m"


def color_off(inline=True):
    """Turn off colored text."""
    if not inline:
        return print("\n\033[0m", end="")
    return "\033[0m"


INFO = color_on("cyan")
ERROR = color_on("red")
PROMPT = color_on("yellow")
DEFAULT = color_on("green")
OUTPUT = color_on("cyan")
ACTIVE = color_on("purple")
OFF = color_off()
