from sqlalchemy.exc import SQLAlchemyError
from requests import exceptions as requests_exceptions
import random
import difflib
import statistics
from datetime import date

import data_processing
from cli_style import (cprint_default,
                       cprint_info,
                       cprint_error,
                       cprint_output,
                       cprint_active,
                       cprint_inactive,
                       cprompt,
                       cprompt_pw,
                       clear_screen)
import api_client as api
import auth
from render_user_page import render_webpage

DEFAULT_USER_ID = 1
current_user_id = DEFAULT_USER_ID

MENU_ENTRIES = [
    " 0. Exit",
    " 1. List my movies",
    " 2. Add movie rating",
    " 3. Delete movie rating",
    " 4. Update movie rating",
    " 5. Stats",
    " 6. Random movie",
    " 7. Search movie",
    " 8. Sort movies by rating",
    " 9. Sort movies by year",
    "10. Filter movies",
    "11. Generate website",
    "12. Log in / Switch user"
]

MENU_INDICES_ON_NO_DATA = {0, 2, 12}
MENU_INDICES_ON_NO_USER = {0, 12}
ALL_MENU_INDICES = set(range(len(MENU_ENTRIES)))
DEACTIVATED_MENU_INDICES_ON_NO_DATA = ALL_MENU_INDICES - MENU_INDICES_ON_NO_DATA
DEACTIVATED_MENU_INDICES_ON_NO_USER = ALL_MENU_INDICES - MENU_INDICES_ON_NO_USER

# ---------------------------------------------------------------------
# CUSTOM EXCEPTIONS
# ---------------------------------------------------------------------
class InvalidInputError(BaseException):
    """Raised when user input isn't valid"""


class InvalidYearError(BaseException):
    """Raised when year isn't valid"""


class RatingOutOfRangeError(BaseException):
    """Raised when rating is not between 0-10."""


class CancelDialog(BaseException):
    """Raised when user enters a predefined string in a prompt."""


class MovieRatingNotFoundError(BaseException):
    """Raised when a movie's rating could not be found."""


class NoRecordsFoundError(BaseException):
    """Raised when no database records are found (for the current user)."""


# ---------------------------------------------------------------------
# CLI MENU
# ---------------------------------------------------------------------
def show_menu(active="0"):
    """Display the main menu with different options
    and ask for user's choice."""
    current_username = data_processing.get_user(current_user_id, True)["user_name"]
    # Display the heading always with the menu.
    cprint_default("********** My Movies Database **********")
    cprint_default("Currently logged in: ", end="")
    cprint_output(f"{current_username}\n")
    cprint_default("Menu:")
    # Build the menu entries from a list of menu items.
    for i, entry in enumerate(MENU_ENTRIES):
        # Turn off menu entry if default user is logged in or
        if (is_default_user(current_user_id)
                and i in DEACTIVATED_MENU_INDICES_ON_NO_USER):
            cprint_inactive(entry)
        # ...no movie ratings found for user
        elif (not user_has_movie_ratings(current_user_id)
                and i in DEACTIVATED_MENU_INDICES_ON_NO_DATA):
            cprint_inactive(entry)
        # Check if menu item is active and change color accordingly.
        elif int(active) == i and int(active) != 0:
            cprint_active(entry)
        else:
            cprint_default(entry)


def update_dispatch_table_and_choices_str(indices:set) -> tuple[dict, str]:
    """Return updated dispatch table and choices string
    for the given indices.
    """
    dispatch_table = DISPATCH_TABLE
    choices_str = ", ".join(f"{entry}" for entry in sorted(list(indices)))
    dispatch_table = {str(i): dispatch_table[str(i)] for i in indices}
    return dispatch_table, choices_str


def run_cli_with_input_listener():
    """Run the command line interface, showing the menu with input listener."""
    while True:
        clear_screen()
        # ---------------------------------------------------------
        # Update dispatch table and choices string if applicable
        if is_default_user(current_user_id):
            indices = MENU_INDICES_ON_NO_USER
            dispatch_table, choices_str = update_dispatch_table_and_choices_str(indices)
        elif not user_has_movie_ratings(current_user_id):
            indices = MENU_INDICES_ON_NO_DATA
            dispatch_table, choices_str = update_dispatch_table_and_choices_str(indices)
        else:
            dispatch_table = DISPATCH_TABLE
            choices_str = None
        show_menu()
        choice = ask_for_user_choice(choices=choices_str)
        # Rebuild the menu with highlighted menu entry.
        # This only works for numbers.
        if choice.isdigit():
            clear_screen()
            show_menu(choice)
        # Option to exit the program.
        if choice == "0":
            say_bye()
            break
        # Execute the selected action.
        if execute_user_choice(choice, dispatch_table):
            pass
        # Intentionally pause after every action,
        # to allow for reading of information or error messages.
        wait_for_enter_key()


# ---------------------------------------------------------------------
# PROMPTS
# ---------------------------------------------------------------------
def ask_for_user_choice(entries=len(MENU_ENTRIES),
                        start_at_zero=True,
                        prompt="Enter choice",
                        choices=""):
    """Ask user for their (menu) choice."""
    if choices:
        choice = cprompt(f"\n{prompt} ({choices}): ")
    else:
        if start_at_zero:
            start = 0
            end = entries - 1
        else:
            start = 1
            end = entries
        if entries == 1:
            range = f"{start}"
        else:
            range = f"{start}-{end}"
        choice = cprompt(f"\n{prompt} ({range}): ")
    return choice


def ask_for_user_data(prompt, allow_blank=False):
    """Ask for user data (username, first name, last name)
    and return this value.

    Return early when user wants to cancel and '..' is entered.
    """
    while True:
        name = cprompt(f"{prompt} or '..' to cancel: ")
        if name == "" and allow_blank is False:
            cprint_error("Username should not be empty!")
        elif name == "..":
            raise CancelDialog
        elif not is_valid_username(name):
            cprint_error("Username should only contain letters and numbers!")
        else:
            break
    return name


def ask_for_password(prompt="Please enter your password"):
    """Ask user for their password and return this value.

    Return early when user wants to cancel and '..' is entered.
    """
    while True:
        password = cprompt_pw(f"{prompt} or '..' to cancel: ")
        if password == "..":
            raise CancelDialog
        elif not is_valid_password(password):
            cprint_error("Maximum password length is 72 characters!")
            pass
        else:
            break
    return password


def ask_for_name():
    """Ask user for the name of a movie and return this value.

    Return early when user wants to cancel and '..' is entered.
    """
    while True:
        movie_name = cprompt("\nEnter the movie name or '..' to cancel: ")
        if movie_name == "":
            cprint_error("\nMovie name should not be empty!")
        elif movie_name == "..":
            raise CancelDialog
        else:
            break
    return movie_name


def ask_for_name_part():
    """Ask user for a part of a movie name and return this value.

    Return early when user wants to cancel and '..' is entered.
    """
    while True:
        movie_name = cprompt("\nEnter movie name, a part of it or "
                             "'..' to cancel: ")
        if movie_name == "":
            cprint_error("Movie name or part of it should not be empty!")
        elif movie_name == "..":
            raise CancelDialog
        else:
            break
    return movie_name


def ask_for_rating(allow_blank=False,
                   prompt="Enter the movie rating (0-10) "
                          "or '..' to cancel: "):
    """Ask the user for the rating of a movie and return this value.

    Return early when user wants to cancel and '..' is entered.
    """
    while True:
        try:
            rating = cprompt(prompt)
            # For function calls that allow blank input.
            if allow_blank and rating == "":
                return None
            # Action should be cancelled.
            if rating == "..":
                raise CancelDialog
            # Rating should be within valid range.
            if not 0 <= float(rating) <= 10:
                raise RatingOutOfRangeError
            return float(rating)
        except ValueError:
            cprint_error("Invalid input")
        except RatingOutOfRangeError:
            cprint_error("Rating must be between 0 and 10 (inclusive).")


def ask_for_year(allow_blank=False,
                 prompt="Enter the year of release "
                        "or '..' to cancel: "):
    """Ask the user for the year of release of a movie
    and return this value.

    Return early when user wants to cancel and '..' is entered.
    """
    while True:
        error_msg = "Invalid input"
        try:
            year = cprompt(prompt)
            # For function calls that allow blank input.
            if allow_blank and year == "":
                return None
            # Action should be cancelled.
            if year == "..":
                raise CancelDialog
            # Return year if input is valid.
            if date.today().year < int(year):
                error_msg = "Year should not lie in the future."
                raise InvalidYearError
            return int(year)
        except (ValueError, InvalidYearError):
            cprint_error(error_msg)


def ask_for_country(allow_blank=False,
                 prompt="Enter the country of origin "
                        "or '..' to cancel: "):
    """Ask the user for the country of origin of a movie
    and return this value.

    Return early when user wants to cancel and '..' is entered.
    """
    while True:
        error_msg = "Invalid input"
        try:
            country = cprompt(prompt)
            # For function calls that allow blank input.
            if allow_blank and country == "":
                return None
            # Action should be cancelled.
            if country == "..":
                raise CancelDialog
            # Return country name if input is valid.
            return country
        except ValueError:
            cprint_error(error_msg)


def ask_for_sort_order():
    """Ask the user for descending or ascending order."""
    accepted_input = {"first", "last"}
    while True:
        try:
            prompt = ("\nDo you want to see the latest movies first or last?"
                      "\nEnter 'first' or 'last: ")
            sort_order = cprompt(prompt).lower()
            if sort_order == "..":
                raise CancelDialog
            if not sort_order in accepted_input:
                raise InvalidInputError
            return sort_order
        except (ValueError, InvalidInputError):
            cprint_error("Invalid input")


def ask_for_rating_note(update=True):
    """Ask the user to enter a rating note.

    Return the following values depending on user input:
    - '..' -> False
    - 'DELETE' -> -1
    - empty string -> 1
    - other string -> string
    """
    prompt = "Here you can add a note for the movie...\n"
    if update:
        prompt  += " - leave empty to keep existing note\n"
    else:
        prompt += " - leave empty to skip\n"
    prompt += " - type '..' to cancel and go back to the menu\n"
    if update:
        prompt += " - type 'DELETE' (all uppercase) to delete a previous note\n"
    prompt += "Enter your note here: "
    note = cprompt(prompt)
    if note == "..":
        raise CancelDialog
    elif note == "" and update:
        return 1 # leave note unchanged
    elif note == "DELETE" and update:
        return -1 # delete note
    return note # add or update note


def wait_for_enter_key():
    """Stop the program until user hits enter key."""
    cprompt("\nPress enter key to continue.\n")


# ---------------------------------------------------------------------
# DYNAMIC MOVIE RETRIEVAL, SELECTION, FUZZY SEARCH FROM API OR DATABASE
# ---------------------------------------------------------------------
def list_api_search_results(search_term: str) -> tuple[str, dict]:
    """Return retrieved movies from API as a formatted string
    and a dispatch table to allow user to select.
    """
    dispatch_table = {}
    output = ""
    cprint_info("Looking up in OMDB...")
    results_raw = api.find_movies(search_term)
    if results_raw:
        results = data_processing.std_search_results_from_api(results_raw)
        for i, movie in enumerate(results, start=1):
            imdb_id = movie["imdb_id"]
            title = movie["title"]
            type = movie["type"]
            extended_movie_obj = get_movie_details_from_api(imdb_id)[imdb_id]
            countries = extended_movie_obj["country"]
            year = extended_movie_obj["year"]
            if year == "":
                year = "N/A"
            dispatch_table[str(i)] = (imdb_id, title)
            emojis = " ".join(
                data_processing.get_country_emoji(country)
                for country in countries
            )
            if emojis == False:
                emojis = movie["imdbID"]["country"]
            output += (f"\n{i:>3}: {title} ({year}) [{type}] - {emojis}")
    return output, dispatch_table


def select_movie_from_api_or_db(search_term=None, source="api"):
    """Return imdb_id and title or id and title for a specific movie
    selected from a list of movies retrieved via API / DB.
    """
    if source == "api":
        message = f"\nMovies matching search term '{search_term}':"
        results = list_api_search_results(search_term)
    else:
        message = "\nMovies matching your search:"
        imdb_ids = list(fuzzy_search_movie_in_db(search_term))
        results = list_db_search_results(imdb_ids)
    if all(results):
        output, dispatch_table = results
        cprint_output(message)
        cprint_output(output)
        while True:
            choice = ask_for_user_choice(len(dispatch_table),
                                         start_at_zero=False,
                                         prompt="Please select a movie")
            if choice == "..":
                raise CancelDialog
            elif is_valid_user_choice(choice, dispatch_table):
                break
        if choice:
            imdb_id, title = dispatch_table[choice]
            return imdb_id, title
    else:
        if source == "api":
            cprint_info(f"Online search couldn't"
                        f"find any movies matching '{search_term}'")
    return (False, False)


def get_movie_details_from_api(imdb_id):
    """Return movie object for the given imdbID."""
    movie_object_raw = api.fetch_movie_details(imdb_id)
    movie_object = data_processing.std_extended_movie_object_from_api(movie_object_raw)
    return movie_object


def list_db_search_results(imdb_ids: list[str]) -> tuple[str, dict]:
    """Print retrieved movies from fuzzy search a user has rated and
    return a dispatch table to allow user to select.
    """
    dispatch_table = {}
    output = ""
    for i, imdb_id in enumerate(imdb_ids, start=1):
        movie = data_processing.get_movie(imdb_id)
        movie_id = movie["id"]
        title = movie["title"]
        year = movie["year"]
        rating_obj = data_processing.get_rating(current_user_id, movie_id)
        rating = rating_obj["rating"]
        emojis = " ".join(data_processing.get_country_emojis_for_movie(movie_id))
        dispatch_table[str(i)] = (imdb_id, title)
        output += (f"\n{i:>3}: {title} ({year}) - {rating} - {emojis}")
    return output, dispatch_table


def sequence_matcher(search_term, input_dict, n, cutoff):
    """Return key value pairs as a list of dictionaries
    for a fuzzy search on the given dictionary.
    """
    input_list = input_dict.items()
    matches = {}
    for key, value in input_list:
        if len(matches) > n:
            break
        if difflib.SequenceMatcher(None, search_term, value).ratio() >= cutoff:
            matches[key] = value
            # matches.append(match)
    return matches


def fuzzy_search_movie_in_db(search_term=None) -> dict | bool:
    """Return movie titles received by fuzzy search for search term.

    If no search term was given ask for a movie title or part of it.
    """
    data = data_processing.get_movies(current_user_id)
    if not search_term:
        search_term = ask_for_name_part()
    # using sequence matcher, since we need both, imdb_id and title
    movies_dict = get_imdb_ids_with_title(data)
    suggestions = sequence_matcher(search_term, movies_dict, 4, 0.3)
    if len(suggestions) == 0:
        cprint_info(f"A movie containing '{search_term}' could not be found.")
        return dict()
    return suggestions


def get_imdb_id_and_title_from_db_search():
    """Return imdb_id and title for the user selection of a fuzzy search."""
    results = fuzzy_search_movie_in_db()
    if results:
        imdb_id, title = select_movie_from_api_or_db(results, "db")
        return imdb_id, title
    return False


# ---------------------------------------------------------------------
# CLI COMMAND FUNCTIONS
# ---------------------------------------------------------------------
def login_or_switch_user():
    """Login or switch user.

    Provide the option to create a new user
    if username couldn't be found.
    """
    global current_user_id
    should_create_new_user = False
    # -----------------------------------------------------------------
    # Get username and check for existing user
    print()
    username = ask_for_user_data("Please enter or choose your username").lower()
    if not user_exists(username):
        cprint_error(f"Username {username} does not exist.")
        if cprompt("Do you want to add this user? ('y'/'n'): ").lower() == "y":
            should_create_new_user = True
        else:
            raise CancelDialog
    # -----------------------------------------------------------------
    # Prompt for password and add or authenticate user
    while True:
        password = ask_for_password("Enter your password")
        if not should_create_new_user:
            break
        confirmed_password = ask_for_password("Confirm your password")
        if password == confirmed_password:
            break
        cprint_error("Passwords do not match. Please try again!")
    if should_create_new_user:
        hashed_password = auth.hash_password(password)
        current_user_id = data_processing.add_user(username, hashed_password)
        cprint_info(f"New user '{username}' has been added and logged in.")
        return True
    else:
        if auth.authenticate_user(username, password):
            current_user_id = data_processing.get_user(username)["id"]
            cprint_info("You were successfully authenticated and logged in.")
            return True
    cprint_error("Authentication failed for the provided credentials!")
    return False


def format_movie_entry(title, year, rating, emojis):
    """Return a formatted movie entry."""
    emojis_str = " ".join(emojis)
    return f"{title} ({year}) - {rating:.1f} - {emojis_str}"


def list_movies(*data, nested_call=False):
    """Show all the movies in the database with their details.

    The function can also be called by the sort or search function.
    """
    print()
    if not nested_call:
        data = data_processing.get_movies(current_user_id)
        cprint_output(f"{len(data)} movies in total:\n")
    else:
        # Because we passed the data as an optional argument...
        # ...we need to unpack tuple of one element.
        data = data[0]
    for imdb_id, details in data.items():
        movie_id = details["movie_id"]
        title = details["title"]
        year = details["year"]
        rating = details["rating"]
        emojis = data_processing.get_country_emojis_for_movie(movie_id)
        cprint_output(f"{format_movie_entry(title, year, rating, emojis)}")


def add_movie_rating():
    """Add movie rating to the Database."""
    # -----------------------------------------------------------------
    # Always return early if user wants to cancel / has entered '..'.
    data_current_user = data_processing.get_movies(current_user_id)
    data_all_users = data_processing.get_movies()
    movie_title = ask_for_name()
    # -----------------------------------------------------------------
    # Dynamically retrieve movie suggestions
    # for the given title via API
    selected_movie = select_movie_from_api_or_db(movie_title)
    imdb_id, movie_title = selected_movie
    # -----------------------------------------------------------------
    # Check if current user already rated the movie.
    if is_in_movies(data_current_user, imdb_id):
        cprint_error(f"You already rated '{movie_title}'!")
        return False
    # -----------------------------------------------------------------
    # If movie is found in the movies table
    # skip fetching movie details.
    if is_in_movies(data_all_users, imdb_id):
        # get movie details from database
        movie_details = data_processing.get_movie(imdb_id)
        cprint_info(f"Found movie '{movie_title} ({imdb_id})' in the database.")
        cprint_info("Skip fetching movie details from OMDB...")
        movie_id = movie_details["id"]
    # -----------------------------------------------------------------
    # ...otherwise fetch movie details from API.
    else:
        cprint_info("Fetching movie details from OMDB...")
        movie_obj = get_movie_details_from_api(imdb_id)[imdb_id]
        year = movie_obj["year"]
        if year == "":
            cprint_error("Couldn't retrieve a valid year from OMDB.")
            prompt = "Please enter the year of release manually ('..' to cancel): "
            year = str(ask_for_year(prompt=prompt))
        image_url = movie_obj["image_url"]
        imdb_rating = movie_obj["imdb_rating"]
        countries = movie_obj["country"]
        cprint_info("Movie details complete. Adding movie to database...")
        # Add movie to the database.
        movie_id = data_processing.add_movie(imdb_id,
                                             movie_title,
                                             year,
                                             image_url,
                                             imdb_rating)
        cprint_info(f"Successfully added '{movie_title}'. (ID: {movie_id})")
        # Finally add new country objects to the database...
        # ...and create movie-country relationships.
        cprint_info("Processing country details...")
        for country in countries:
            add_country_if_new(country)
            country_id = data_processing.get_country_by_name(country)["id"]
            data_processing.add_movie_country_relationship(movie_id, country_id)
            cprint_info(f"Successfully created movie-country "
                        f"relationship for '{country}'.")
    # -----------------------------------------------------------------
    # Finally ask for rating / note and store it in the database.
    rating = ask_for_rating()
    note = ask_for_rating_note(update=False)
    data_processing.add_rating(current_user_id, movie_id, rating, note)
    cprint_info(f"Successfully added rating for movie '{movie_title}'.")
    if note:
        cprint_info("Note for the movie's rating has been added.")
    else:
        cprint_info("No note has been added.")
    return True


def add_country_if_new(country_name):
    """Add the given country object to the database
    and return its id.
    """
    country_object = data_processing.get_country_by_name(country_name)
    country_id = country_object["id"]
    # Only new countries receive a temporary id (-1)
    # should be added to the database.
    if country_id == -1:
        cprint_info("Adding country data to database...")
        name = country_object["name"]
        code = country_object["code"]
        country_id = data_processing.add_country(name, code)
        cprint_info(f"Successfully added country data for"
                    f" '{name}'. (ID: {country_id})")
        return country_id
    return False


def delete_movie_rating():
    """Delete a movie's rating from the database."""
    imdb_id, movie_title = select_movie_from_api_or_db(source="db")
    movie_id = data_processing.get_movie(imdb_id)["id"]
    data_processing.delete_rating(current_user_id, movie_id)
    cprint_info(f"Rating for '{movie_title}' successfully deleted")
    return True


def update_movie_rating_and_note():
    """Update a movie’s rating (and note) in the database."""
    # -----------------------------------------------------------------
    # Let the user chose which movie to re-rate
    results = select_movie_from_api_or_db(source="db")
    if results == (False, False):
        raise MovieRatingNotFoundError
    elif any(results):
        imdb_id, movie_title = results
        movie_id = data_processing.get_movie(imdb_id)["id"]
    # -----------------------------------------------------------------
    # Set 'rating' for the movie
    rating_prompt = ("Enter the movie rating (0-10), leave empty\n"
                     "to keep previous rating or type '..' to cancel: ")
    rating = ask_for_rating(allow_blank=True, prompt=rating_prompt)
    # -----------------------------------------------------------------
    # Set action for the rating note depending on user's choice
    previous_rating = data_processing.get_rating(current_user_id, movie_id)
    note = ask_for_rating_note()
    if note == -1:
        note = ""
        note_msg = (f"Note for the movie's rating has been deleted.")
    elif note == 1:
        note = previous_rating["note"]
        note_msg = (f"Note for the movie's rating has been left unchanged.")
    else:
        note_msg = (f"Note for the movie's rating has been updated.")
    # Update the rating or keep previous value
    if rating == None:
        rating = previous_rating["rating"]
        cprint_info(f"Leave previous rating of '{rating}' unchanged.")
    else:
        cprint_info(f"Change rating to '{rating}'.")
    data_processing.update_rating(current_user_id, movie_id, rating, note)
    cprint_info(f"Successfully updated rating entry for '{movie_title}'.")
    cprint_info(note_msg)
    return True


def get_ratings(data):
    """Return the rating for each movie as a list."""
    return [values["rating"] for values in data.values()]


def get_average_rating(ratings):
    """Return the average rating from a list of ratings."""
    return round(statistics.mean(ratings), 1)


def get_median_rating(ratings):
    """Return the median rating of all movies."""
    return round(statistics.median(ratings), 1)


def get_best_or_worst_movies(data, get_best=True):
    """Return a list with the best / worst rated movie(s)."""
    for i, (imdb_id, movie_details) in enumerate(data.items()):
        rating =  movie_details["rating"]
        # Initialize best / worst movie(s) on first iteration only.
        if i == 0:
            best_or_worst_rating = rating
            best_or_worst_movies = [imdb_id]
        elif rating == best_or_worst_rating:
            best_or_worst_movies.append(imdb_id)
        elif get_best is True and rating > best_or_worst_rating:
            best_or_worst_rating = rating
            best_or_worst_movies = [imdb_id]
        elif get_best is False and rating < best_or_worst_rating:
            best_or_worst_rating = rating
            best_or_worst_movies = [imdb_id]
    return best_or_worst_movies


def get_movie_stats():
    """Print statistics for movies in the database.

    Show average and median rating,
    best and worst movies.
    """
    # Get the data
    data = data_processing.get_movies(current_user_id)
    ratings = get_ratings(data)
    average_rating = get_average_rating(ratings)
    median_rating = get_median_rating(ratings)
    best_movies = get_best_or_worst_movies(data)
    worst_movies = get_best_or_worst_movies(data, get_best=False)
    # Show stats...
    cprint_output(f"\nAverage rating: {average_rating}")
    cprint_output(f"Median rating: {median_rating}")
    # ...and make sure multiple best and worst movies are shown.
    cprint_output("Best movie(s): ", end="")
    # create formatted list of the best movies
    best_movies_formatted = [format_movie_entry(
        data[imdb_id]['title'],
        data[imdb_id]['year'],
        data[imdb_id]['rating'],
        data_processing.get_country_emojis_for_movie(data[imdb_id]['movie_id']))
        for imdb_id in best_movies
    ]
    cprint_output(" | ".join(best_movies_formatted))
    cprint_output("Worst movie(s): ", end="")
    # create formatted list of the worst movies
    worst_movie_objects = [format_movie_entry(
        data[imdb_id]['title'],
        data[imdb_id]['year'],
        data[imdb_id]['rating'],
        data_processing.get_country_emojis_for_movie(data[imdb_id]['movie_id']))
        for imdb_id in worst_movies
    ]
    cprint_output(f"{' | '.join(worst_movie_objects)}")


def get_random_movie():
    """Show the details for a random movie."""
    data = data_processing.get_movies(current_user_id)
    imdb_ids = get_imdb_ids(data)
    random_imdb_id = random.choice(imdb_ids)
    random_title = data[random_imdb_id]["title"]
    rating = data[random_imdb_id]["rating"]
    year = data[random_imdb_id]["year"]
    movie_id = data[random_imdb_id]["movie_id"]
    emojis = " ".join(data_processing.get_country_emojis_for_movie(movie_id))
    cprint_output(f"\nYour movie for tonight: "
          f"{random_title} ({year}) - {emojis}, it's rated {rating}")


def search_movie():
    """Ask the user to enter a part of a movie name,
    and then search all movies in the database
    and prints all movies that matched the user’s query,
    along with the rating. (case-insensitive).

    If movie's title could not be found,
    display suggestions received by fuzzy search.
    """
    data = data_processing.get_movies(current_user_id)
    search_term = ask_for_name_part()
    found = False
    for imdb_id, details in data.items():
        movie_id = details["movie_id"]
        title = details["title"]
        year = details["year"]
        rating = details["rating"]
        emojis = data_processing.get_country_emojis_for_movie(movie_id)
        if search_term.lower() in title.lower():
            cprint_output(f"{format_movie_entry(title,
                                                year,
                                                rating,
                                                emojis)}")
            found = True
    if not found:
        # suggest titles by fuzzy search
        cprint_info(f"A movie containing '{search_term}' could not be found.")
        # look for alternatives using fuzzy search
        movies_dict = get_imdb_ids_with_title(data)
        suggestions = sequence_matcher(search_term, movies_dict, 4, 0.3)
        # show only if fuzzy search finds alternatives
        if not len(suggestions) == 0:
            cprint_output("\nDid you mean:\n")
            for imdb_id, title in suggestions.items():
                movie_id = data[imdb_id]["movie_id"]
                title = data[imdb_id]["title"]
                year = data[imdb_id]["year"]
                rating = data[imdb_id]["rating"]
                emojis = data_processing.get_country_emojis_for_movie(movie_id)
                cprint_output(format_movie_entry(title, year, rating, emojis))
    return True


def sort_movies_by_rating():
    """Sort movies in descending order by their rating."""
    data = data_processing.get_movies(current_user_id)
    movies_sorted = dict(sorted(data.items(),
                           key=lambda item: item[1]["rating"],
                           reverse=True))
    list_movies(movies_sorted, nested_call=True)


def sort_movies_by_year():
    """Sort movies in chronological order.

    Ask the user whether they want to see
    the latest movies first or last.
    """
    sort_order = ask_for_sort_order()
    is_reverse = bool(sort_order == "first")
    data = data_processing.get_movies(current_user_id)
    movies_sorted = dict(sorted(data.items(),
                           key=lambda item: item[1]["year"],
                           reverse=is_reverse))
    list_movies(movies_sorted, nested_call=True)


def apply_filter(pair, *args):
    """Return True if all filter conditions are met."""
    _, value = pair
    year_start, year_end, rating_threshold = args
    if rating_threshold and value["rating"] < rating_threshold:
        return False
    if year_start is not None and value["year"] < year_start:
        return False
    if year_end is not None and value["year"] > year_end:
        return False
    return True


def filter_movies():
    """Filter movies based on specific criteria
    such as minimum rating, start year, and end year.
    """
    rating_threshold = ask_for_rating(
        allow_blank=True,
        prompt="\nEnter minimum rating (leave blank for no minimum rating): ")
    year_start = ask_for_year(
        allow_blank=True,
        prompt="Enter start year (leave blank for no start year): ")
    year_end = ask_for_year(
        allow_blank=True,
        prompt="Enter end year (leave blank for no end year): ")
    data = data_processing.get_movies(current_user_id)
    filtered_movies = dict(filter(
        lambda movie: apply_filter(
            movie,
            year_start,
            year_end,
            rating_threshold), data.items()))
    cprint_output("\nFiltered Movies:")
    # sort movies by year (descending)
    filtered_movies_sorted = dict(sorted(filtered_movies.items(),
                                         key=lambda item: item[1]["year"],
                                         reverse=True))
    list_movies(filtered_movies_sorted, nested_call=True)


def generate_website():
    """Generate webpage showing all movies rated by the given user."""
    username = data_processing.get_user(current_user_id, find_by_id=True)["user_name"]
    render_webpage(current_user_id)
    cprint_info(f"\nWebsite for '{username}' was generated successfully.")


# ---------------------------------------------------------------------
# SIMPLE LIST AND DICT RETURNING FUNCTIONS
# ---------------------------------------------------------------------
def get_movie_titles(data):
    """Return a list of all movie titles."""
    titles = [imdb_id["title"] for imdb_id in data]
    return titles


def get_imdb_ids_with_title(data):
    """Return a dictionary of all imdb_ids with their title."""
    return {imdb_id: details["title"] for imdb_id, details in data.items()}


def get_imdb_ids(data):
    """Return a list of all movie imdb_ids."""
    return list(data)


# ---------------------------------------------------------------------
# PRINT HELPER FUNCTIONS
# ---------------------------------------------------------------------
def print_action_cancelled():
    """Print an information that an action has been canceled."""
    cprint_info("Action canceled, returning back to menu...")


def not_implemented():
    """Dummy function."""
    cprint_error("Not implemented")


def do_nothing():
    """Another dummy function."""
    return True


def invalid_choice():
    """Display a message for invalid menu choices."""
    cprint_error("\nInvalid choice")


def say_bye():
    """Print 'Bye!' on exit of the program."""
    cprint_info("\nBye!")


# ---------------------------------------------------------------------
# BOOLEAN FUNCTIONS
# ---------------------------------------------------------------------
def is_valid_user_choice(choice, dispatch_table):
    """Return user choice if it's a member of a given dispatch table."""
    if not dispatch_table.get(choice):
        invalid_choice()
        return False
    return choice


def is_in_movies(data, imdb_id):
    """Check if a movie is in the movies-database."""
    if imdb_id.strip() in data:
        return True
    return False


def user_has_movie_ratings(user_id=DEFAULT_USER_ID):
    """Return True if user rated at least one movie."""
    if data_processing.count_movie_ratings_for_user(user_id) > 0:
        return True
    return False


def is_default_user(user_id):
    """Return True if the given user id is the default user."""
    return user_id == DEFAULT_USER_ID


def is_valid_username(username):
    """Return True if username conforms to requirements.

    Currently, a username should only consist of
    alphanumeric characters.
    """
    return username.isalnum()


def is_valid_password(password):
    """Return True if password conforms to requirements.

    Currently, there are no restrictions on password strength,
    even an empty password is allowed. The only limitation is
    bcrypt's maximum password length of 72 characters.
    """
    return len(password) <= 72


def user_exists(username):
    """Return True if the username exists in the database."""
    if data_processing.get_user(username):
        return True
    return False


# ---------------------------------------------------------------------
# FUNCTION DISPATCHER
# ---------------------------------------------------------------------
DISPATCH_TABLE = {
    "0": do_nothing,
    "1": list_movies,
    "2": add_movie_rating,
    "3": delete_movie_rating,
    "4": update_movie_rating_and_note,
    "5": get_movie_stats,
    "6": get_random_movie,
    "7": search_movie,
    "8": sort_movies_by_rating,
    "9": sort_movies_by_year,
    "10": filter_movies,
    "11": generate_website,
    "12": login_or_switch_user
}


def execute_user_choice(choice, dispatch_table=None):
    """Execute a function for the corresponding user choice.

    Return False if the choice was invalid, otherwise True.
    """
    if dispatch_table is None:
        dispatch_table = DISPATCH_TABLE
    if DISPATCH_TABLE.get(choice) and not dispatch_table.get(choice):
        if is_default_user(current_user_id):
            cprint_error(f"\nPlease login to use this function.")
        if not user_has_movie_ratings(current_user_id):
            cprint_error(f"\nAdd a movie rating to enable this function.")
        # return False
    if not dispatch_table.get(choice):
        invalid_choice()
        return False
    try:
        dispatch_table[choice]()
    except CancelDialog:
        print_action_cancelled()
    except MovieRatingNotFoundError:
        pass
    except requests_exceptions.Timeout:
        cprint_error("Connection to the OMDB API has timed out.")
    except requests_exceptions.ConnectionError:
        cprint_error("Couldn't connect to the OMDB API.")
    except SQLAlchemyError as e:
        cprint_error("The following exception was raised during a database operation:")
        cprint_inactive(f"{e}")
    return True


def main():
    """Main function for testing when running the script under main."""
    pass


if __name__ == "__main__":
    main()