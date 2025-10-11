"""Run the command line interface to manage a movie database."""
from movies import (
    show_menu,
    get_user_choice,
    say_bye,
    execute_user_choice,
    wait_for_enter_key
)
from cli_style import clear_screen

while True:
    clear_screen()
    show_menu()
    user_choice = get_user_choice()
    # Rebuild the menu with highlighted menu entry.
    # This only works for numbers.
    if user_choice.isdigit():
        clear_screen()
        show_menu(user_choice)
    # Option to exit the program.
    if user_choice == "0":
        say_bye()
        break
    # Execute the selected action.
    if execute_user_choice(user_choice):
        pass
    # Intentionally pause after every action,
    # to allow for reading of information or error messages.
    wait_for_enter_key()
