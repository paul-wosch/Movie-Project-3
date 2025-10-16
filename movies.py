import random
import difflib
import statistics
from datetime import date

import movie_storage
import data_processing
from cli_style import (cprint_default,
                       cprint_info,
                       cprint_error,
                       cprint_output,
                       cprint_active,
                       cprompt)
import api_client as api

# Modify after implementing user management
DEFAULT_USER_ID = 1
CURRENT_USER_ID = DEFAULT_USER_ID

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
    "10. Filter movies"
]


class InvalidInputError(BaseException):
    """Raised when user input isn't valid"""


class InvalidYearError(BaseException):
    """Raised when year isn't valid"""


class RatingOutOfRangeError(BaseException):
    """Raised when rating is not between 0-10."""


def show_menu(active="0"):
    """Display the main menu with different options
    and ask for user's choice."""
    # Display the heading always with the menu.
    cprint_default("********** My Movies Database **********\n")
    cprint_default("Menu:")
    # Build the menu entries from a list of menu items.
    for i, entry in enumerate(MENU_ENTRIES):
        # Check if menu item is active and change color accordingly.
        if int(active) == i and int(active) != 0:
            cprint_active(entry)
        else:
            cprint_default(entry)


def get_user_choice(entries=len(MENU_ENTRIES),
                    start_at_zero=True,
                    prompt="Enter choice"):
    """Ask user for their menu choice."""
    if start_at_zero:
        start = 0
        end = entries - 1
    else:
        start = 1
        end = entries
    choice = cprompt(f"\n{prompt} ({start}-{end}): ")
    return choice


def wait_for_enter_key():
    """Stop the program until user hits enter key."""
    cprompt("\nPress enter key to continue.\n")


def get_movie_titles(data):
    """Return a list of all movie titles."""
    return list(data)


def is_in_movies(data, title):
    """Check if a movie is in the movies-database."""
    if title.strip() in data:
        return True
    return False


def format_movie_entry(title, year, rating, emojis):
    """Return a formatted movie entry."""
    emojis_str = " ".join(emojis)
    return f"{title} ({year}) - {rating:.1f} - {emojis_str}"


def list_movies(*data, nested_call=False):
    """Show all the movies in the database with their details.

    The function can also be called by the sort or search function."""
    # TODO: Check behaviour when movies table is empty.
    user_id = CURRENT_USER_ID
    print()
    if not nested_call:
        data = data_processing.get_movies(user_id=user_id)
        cprint_output(f"{len(data)} movies in total:\n")
    else:
        # Because we passed the data as an optional argument...
        # ...we need to unpack tuple of one element.
        data = data[0]
    for title, details in data.items():
        year = details["year"]
        rating = details["rating"]
        movie_id = details["movie_id"]
        emojis = data_processing.get_country_emojis_for_movie(movie_id)
        cprint_output(f"{format_movie_entry(title, year, rating, emojis)}")


def print_action_cancelled():
    """Print an information that an action has been canceled."""
    cprint_info("Action canceled, returning back to menu...")


# ---------------------------------------------------------------------
# PROMPTS
# ---------------------------------------------------------------------
def ask_for_name():
    """Ask user for the name of a movie and return this value.

    Return early when user wants to cancel and '..' is entered.
    """
    while True:
        movie_name = cprompt("\nEnter the movie name or '..' to cancel: ")
        if movie_name == "":
            cprint_error("\nMovie name should not be empty!")
        elif movie_name == "..":
            print_action_cancelled()
            return False
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
            print_action_cancelled()
            return False
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
                print_action_cancelled()
                return False
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
                print_action_cancelled()
                return False
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
                print_action_cancelled()
                return False
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
        print_action_cancelled()
        return False # cancel action
    elif note == "" and update:
        return 1 # leave note unchanged
    elif note == "DELETE" and update:
        return -1 # delete note
    return note # add or update note


# ---------------------------------------------------------------------
# DYNAMIC MOVIE RETRIEVAL AND SELECTION FROM API OR DATABASE
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
            imdbID = movie["imdbID"]
            title = movie["title"]
            year = movie['year']
            type = movie['type']
            countries = get_movie_details_from_api(imdbID)[title]["country"]
            print(countries)
            dispatch_table[str(i)] = (imdbID, title)
            emojis = " ".join(
                data_processing.get_country_emoji(country)
                for country in countries
            )
            if emojis == False:
                emojis = movie["imdbID"]["country"]
            output += (f"\n{i:>3}: {title} ({year}) [{type}] - {emojis}")
    return output, dispatch_table


def select_movie_from_api_or_db(search_term, source="api"):
    """Return imdbID and title or id / title for a specific movie
    selected from a list of movies retrieved via API / DB.
    """
    if source == "api":
        message = f"\nMovies matching search term '{search_term}':"
        results = list_api_search_results(search_term)
    else:
        message = "\nMovies matching your search:"
        results = list_db_search_results(search_term)
    if all(results):
        output, dispatch_table = results
        cprint_output(message)
        cprint_output(output)
        while True:
            choice = get_user_choice(len(dispatch_table),
                                     start_at_zero=False,
                                     prompt="Please select a movie")
            if choice == "..":
                choice = False
                print_action_cancelled()
                break
            elif is_valid_user_choice(choice, dispatch_table):
                break
        if choice:
            id, title = dispatch_table[choice]
            return id, title
    else:
        cprint_info(f"Online search couldn't find any movies matching '{search_term}'")
    return (False, False)


def get_movie_details_from_api(imdbID):
    """Return movie object for the given imdbID."""
    movie_object_raw = api.fetch_movie_details(imdbID)
    movie_object = data_processing.std_movie_from_api(movie_object_raw)
    return movie_object


def list_db_search_results(movie_titles: list[str]) -> tuple[str, dict]:
    """Print retrieved movies from fuzzy search a user has rated and
    return a dispatch table to allow user to select.
    """
    user_id = CURRENT_USER_ID
    dispatch_table = {}
    output = ""
    for i, title in enumerate(movie_titles, start=1):
        movie = data_processing.get_movie(title)
        movie_id = movie["id"]
        title = movie["title"]
        year = movie["year"]
        rating_obj = data_processing.get_rating(user_id, movie_id)
        rating = rating_obj["rating"]
        emojis = " ".join(data_processing.get_country_emojis_for_movie(movie_id))
        dispatch_table[str(i)] = (movie["id"], movie["title"])
        output += (f"\n{i:>3}: {title} ({year}) - {rating} - {emojis}")
    return output, dispatch_table


def fuzzy_search_movie_in_db(search_term=False) -> list[str] | bool:
    """Return movie titles received by fuzzy search for search term.

    If no search term was given ask for a movie title or part of it.
    """
    user_id = CURRENT_USER_ID
    data = data_processing.get_movies(user_id)
    if not search_term:
        search_term = ask_for_name_part()
    # Return early if user wants to cancel.
    if search_term is False:
        return False
    # Always suggest titles by fuzzy search.
    suggestions = difflib.get_close_matches(search_term, list(data), 4, 0.3)
    if len(suggestions) == 0:
        cprint_info("A movie containing '{search_term}' could not be found.")
        return []
    return suggestions


def get_movie_id_and_title_from_db_search():
    """Return movie id and title for the user selection of a fuzzy search."""
    titles = fuzzy_search_movie_in_db()
    # return early if user wants to cancel
    if titles is False:
        return False
    if titles:
        movie_id, title = select_movie_from_api_or_db(titles, "db")
        return movie_id, title
    return False


# ---------------------------------------------------------------------
# CRUD OPERATIONS
# ---------------------------------------------------------------------
def add_movie_rating():
    """Add movie rating to the Database."""
    # -----------------------------------------------------------------
    # Always return early if user wants to cancel / has entered '..'.
    user_id = CURRENT_USER_ID
    data_current_user = data_processing.get_movies(user_id)
    data_all_users = data_processing.get_movies()
    movie_title = ask_for_name()
    if movie_title is False:
        return False
    # -----------------------------------------------------------------
    # Dynamically retrieve movie suggestions
    # for the given title via API
    selected_movie = select_movie_from_api_or_db(movie_title)
    if any(selected_movie) is False:
        return False
    imdbID, movie_title = selected_movie
    # -----------------------------------------------------------------
    # Check if current user already rated the movie.
    if is_in_movies(data_current_user, movie_title):
        cprint_error(f"You already rated '{movie_title}'!")
        return False
    # -----------------------------------------------------------------
    # If movie is found in the movies table
    # skip fetching movie details.
    if is_in_movies(data_all_users, movie_title):
        # get movie details from database
        movie_details = data_processing.get_movie(movie_title)
        cprint_info(f"Found movie '{movie_title}' in the database.")
        cprint_info("Skip fetching movie details from OMDB...")
        movie_id = movie_details["id"]
    # -----------------------------------------------------------------
    # ...otherwise fetch movie details from API.
    else:
        movie_obj = get_movie_details_from_api(imdbID)[movie_title]
        print(movie_obj)
        year = movie_obj["year"]
        image_url = movie_obj["image_url"]
        imdb_rating = movie_obj["imdb_rating"]
        countries = movie_obj["country"]
        cprint_info("Movie details complete. Adding movie to database...")
        # Add movie to the database.
        movie_id = data_processing.add_movie(movie_title,
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
    if rating is False:
        return False
    note = ask_for_rating_note(update=False)
    if note is False:
        return False
    data_processing.add_rating(CURRENT_USER_ID, movie_id, rating, note)
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
                    f" '{name}'. (ID: {country_id}")
        return country_id
    return False


def delete_movie_rating():
    """Delete a movie's rating from the database."""
    user_id = CURRENT_USER_ID
    result = get_movie_id_and_title_from_db_search()
    # Return early if user wants to cancel.
    if result is False:
        return False
    movie_id, movie_title = result
    data_processing.delete_rating(user_id, movie_id)
    cprint_info(f"Rating for '{movie_title}' successfully deleted")
    return True


def update_movie_rating_and_note():
    """Update a movie’s rating (and note) in the database."""
    # -----------------------------------------------------------------
    # Let the user chose which movie to re-rate
    user_id = CURRENT_USER_ID
    result = get_movie_id_and_title_from_db_search()
    # Return early if user wants to cancel.
    if any(result) is False:
        return False
    movie_id, movie_title = result
    # -----------------------------------------------------------------
    # Set 'rating' for the movie
    rating = ask_for_rating()
    if rating is False:
        return False
    # -----------------------------------------------------------------
    # Set action for the rating note depending on user's choice
    note = ask_for_rating_note()
    if note is False:
        return False
    elif note == -1:
        note = ""
        note_msg = (f"Note for the movie's rating has been deleted.")
    elif note == 1:
        note = data_processing.get_rating(user_id, movie_id)["note"]
        note_msg = (f"Note for the movie's rating has been left unchanged.")
    else:
        note_msg = (f"Note for the movie's rating has been updated.")
    data_processing.update_rating(user_id, movie_id, rating, note)
    cprint_info(f"Successfully updated rating for '{movie_title}'.")
    cprint_info(note_msg)
    return True


def update_movie_rating_old():
    """Update a movie’s rating in the database."""
    data = movie_storage.get_movies()
    movie_title = ask_for_name()
    # Return early if user wants to cancel.
    if movie_title is False:
        return False
    # Check if the film already exists.
    if not is_in_movies(data, movie_title):
        cprint_error(f"Movie '{movie_title}' doesn't exist!")
        # Recurse to start the function again:
        update_movie_rating_and_note()
    else:
        title = movie_title
        # Ask for movie details
        # and return early if user wants to cancel.
        rating = ask_for_rating()
        if rating is False:
            return False
        year = ask_for_year()
        if year is False:
            return False
        # Update the movie.
        movie_storage.update_movie(title, year, rating)
        cprint_info(f"Movie '{movie_title}' successfully updated")
    return True


def get_ratings(data):
    """Return th rating for each movie as a list."""
    return [values["rating"] for values in data.values()]


def get_average_rating(ratings):
    """Return the average rating from a list of ratings."""
    return round(statistics.mean(ratings), 1)


def get_median_rating(ratings):
    """Return the median rating of all movies."""
    return round(statistics.median(ratings), 1)


def get_best_or_worst_movies(data, get_best=True):
    """Return a list with the best / worst rated movie(s)."""
    for i, (movie_title, movie_details) in enumerate(data.items()):
        rating =  movie_details["rating"]
        # Initialize best / worst movie(s) on first iteration only.
        if i == 0:
            best_or_worst_rating = rating
            best_or_worst_movies = [movie_title]
        elif rating == best_or_worst_rating:
            best_or_worst_movies.append(movie_title)
        elif get_best is True and rating > best_or_worst_rating:
            best_or_worst_rating = rating
            best_or_worst_movies = [movie_title]
        elif get_best is False and rating < best_or_worst_rating:
            best_or_worst_rating = rating
            best_or_worst_movies = [movie_title]
    return best_or_worst_movies


def get_movie_stats():
    """Print statistics for movies in the database.

    Show average and median rating,
    best and worst movies.
    """
    # Get the data.
    # data = movie_storage.get_movies()
    user_id = CURRENT_USER_ID
    data = data_processing.get_movies(user_id)
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
        title,
        data[title]['year'],
        data[title]['rating'],
        data_processing.get_country_emojis_for_movie(data[title]['movie_id']))
        for title in best_movies
    ]
    cprint_output(" | ".join(best_movies_formatted))
    cprint_output("Worst movie(s): ", end="")
    # create formatted list of the worst movies
    worst_movie_objects = [format_movie_entry(
        title,
        data[title]['year'],
        data[title]['rating'],
        data_processing.get_country_emojis_for_movie(data[title]['movie_id']))
        for title in worst_movies
    ]
    cprint_output(f"{' | '.join(worst_movie_objects)}")


def get_random_movie():
    """Show the details for a random movie."""
    user_id = CURRENT_USER_ID
    data = data_processing.get_movies(user_id)
    movie_titles = get_movie_titles(data)
    random_title = random.choice(movie_titles)
    rating = data[random_title]["rating"]
    year = data[random_title]["year"]
    movie_id = data[random_title]["movie_id"]
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
    user_id = CURRENT_USER_ID
    data = data_processing.get_movies(user_id)
    search_term = ask_for_name_part()
    # Return early if user wants to cancel.
    if search_term is False:
        return False
    found = False
    for title, details in data.items():
        if search_term.lower() in title.lower():
            movie_id = details["movie_id"]
            emojis = " ".join(data_processing.get_country_emojis_for_movie(movie_id))
            cprint_output(f"{format_movie_entry(title,
                                                details['year'],
                                                details['rating'],
                                                emojis)}")
            found = True
    if not found:
        # suggest titles by fuzzy search
        cprint_info(f"A movie containing '{search_term}' could not be found.")
        # look for alternatives using fuzzy search
        suggestions = difflib.get_close_matches(search_term, list(data), 4, 0.3)
        # show only if fuzzy search finds alternatives
        if not len(suggestions) == 0:
            cprint_output("\nDid you mean:\n")
            for suggestion in suggestions:
                title = suggestion
                year = data[suggestion]["year"]
                rating = data[suggestion]["rating"]
                movie_id = data[suggestion]["movie_id"]
                emojis = " ".join(data_processing.get_country_emojis_for_movie(movie_id))
                cprint_output(format_movie_entry(title, year, rating, emojis))
    return True


def sort_movies_by_rating():
    """Sort movies in descending order by their rating."""
    user_id = CURRENT_USER_ID
    data = data_processing.get_movies(user_id)
    movies_sorted = dict(sorted(data.items(),
                           key=lambda item: item[1]["rating"],
                           reverse=True))
    list_movies(movies_sorted, nested_call=True)


def sort_movies_by_year():
    """Sort movies in chronological order.

    Ask the user whether they want to see
    the latest movies first or last.
    """
    user_id = CURRENT_USER_ID
    sort_order = ask_for_sort_order()
    is_reverse = bool(sort_order == "first")
    data = data_processing.get_movies(user_id)
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
    user_id = CURRENT_USER_ID
    rating_threshold = ask_for_rating(
        allow_blank=True,
        prompt="Enter minimum rating (leave blank for no minimum rating): ")
    year_start = ask_for_year(
        allow_blank=True,
        prompt="Enter start year (leave blank for no start year): ")
    year_end = ask_for_year(
        allow_blank=True,
        prompt="Enter end year (leave blank for no end year): ")
    data = data_processing.get_movies(user_id)
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


def not_implemented():
    """Dummy function."""
    cprint_error("Not implemented")


def do_nothing():
    """Another dummy function."""
    return True


def invalid_choice():
    """Display a message for invalid menu choices."""
    cprint_error("Invalid choice")


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
    "10": filter_movies
}


def execute_user_choice(choice):
    """Execute a function for the corresponding user choice.

    Return False if the choice was invalid, otherwise True.
    """
    if not DISPATCH_TABLE.get(choice):
        invalid_choice()
        return False
    DISPATCH_TABLE[choice]()
    return True


def is_valid_user_choice(choice, dispatch_table):
    """Return user choice if it's a member of a given dispatch table."""
    if not dispatch_table.get(choice):
        invalid_choice()
        return False
    return choice


def say_bye():
    """Print 'Bye!' on exit of the program."""
    cprint_info("\nBye!\n")


def main():
    """Main function for testing when running the script under main."""
    pass


if __name__ == "__main__":
    main()
