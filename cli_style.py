"""Make the CLI more appealing with colored text output

Main features:
- colored text
- clear screen
- print dividers (to be implemented)

Tag based use for inline text (no extra print statement):
- in an f string use as follows
- print(f"{ERROR}test{OFF}") or print(f"{module.ERROR}test{module.OFF}")
- the Following tags are available: INFO, ERROR, PROMPT, DEFAULT, OFF

Alternative (old) way to use:
- color_on(color_name)
- color_off()
- create a new line with optional argument inline=False

Recommended use:
- dedicated functions for each style tag
- cprint_info, cprint_error etc.
- cprompt for user input

Any of the above methods can be combined as needed,
depending on the use case.
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


# ---------------------------------------------------------------------
# CUSTOM FUNCTIONS FOR COLORED TEXT OUTPUT
# ---------------------------------------------------------------------
DEFAULT = color_on("green")
INFO = color_on("cyan")
ERROR = color_on("red")
OUTPUT = color_on("blue")
ACTIVE = color_on("purple")
PROMPT = color_on("yellow")
OFF = color_off()


# ---------------------------------------------------------------------
# CUSTOM FUNCTIONS FOR COLORED TEXT OUTPUT
# ---------------------------------------------------------------------
def cprint_default(text, **kwargs):
    """Print the given text with style 'DEFAULT'."""
    print(f"{DEFAULT}{text}{OFF}", **kwargs)


def cprint_info(text, **kwargs):
    """Print the given text with style 'INFO'."""
    print(f"{INFO}{text}{OFF}", **kwargs)


def cprint_error(text, **kwargs):
    """Print the given text with style 'ERROR'."""
    print(f"{ERROR}{text}{OFF}", **kwargs)


def cprint_output(text, **kwargs):
    """Print the given text with style 'OUTPUT'."""
    print(f"{OUTPUT}{text}{OFF}", **kwargs)


def cprint_active(text, **kwargs):
    """Print the given text with style 'ACTIVE'."""
    print(f"{ACTIVE}{text}{OFF}", **kwargs)


def cprompt(text, strip=True):
    """Prompt the given text with style 'PROMPT'.

    Set argument 'strip' to False,
    if you want to deactivate white space stripping.
    """
    prompt = input(f"{PROMPT}{text}{OFF}")
    if strip:
        return prompt.strip()
    else:
        return prompt


def main():
    """Main function for testing when running the script under main."""
    pass


if __name__ == "__main__":
    main()
