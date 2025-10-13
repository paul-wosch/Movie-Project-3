import random
import difflib
import statistics
from datetime import date

import movie_storage
import data_processing
import cli_style as style
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
    style.color_on("green", False)
    # Display the heading always with the menu.
    print("********** My Movies Database **********\n")
    print("Menu:")
    # Build the menu entries from a list of menu items.
    for i, entry in enumerate(MENU_ENTRIES):
        # Check if menu item is active and change color accordingly.
        if int(active) == i and int(active) != 0:
            print(f"{style.ACTIVE}{entry}{style.OFF}")
        else:
            print(f"{style.DEFAULT}{entry}{style.OFF}")


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
    choice = input(f"{style.PROMPT}{prompt} ({start}-{end}): {style.OFF}")
    return choice


def wait_for_enter_key():
    """Stop the program until user hits enter key."""
    input(f"{style.PROMPT}\nPress enter key to continue.\n{style.OFF}")


def get_movie_titles(data):
    """Return a list of all movie titles."""
    return list(data)


def is_in_movies(data, title):
    """Check if a movie is in the movies-database."""
    if title.strip() in data:
        return True
    return False


def format_movie_entry(title, year, rating):
    """Return a formatted movie entry."""
    return f"{title} ({year}) - {rating:.1f}"


def list_movies(*data, nested_call=False):
    """Show all the movies in the database with their details.

    The function can also be called by the sort or search function."""
    # TODO: Check behaviour when movies table is empty.
    user_id = CURRENT_USER_ID
    print()
    if not nested_call:
        data = data_processing.get_movies(user_id=user_id)
        print(f"{style.OUTPUT}{len(data)} movies in total:\n{style.OFF}")
    else:
        # Because we passed the data as an optional argument...
        # ...we need to unpack tuple of one element.
        data = data[0]
    for title, details in data.items():
        year = details["year"]
        rating = details["rating"]
        print(f"{style.OUTPUT}{format_movie_entry(title, year, rating)}{style.OFF}")


def print_action_cancelled():
    """Print an information that an action has been canceled."""
    print(f"{style.INFO}Action canceled, returning back to menu...{style.OFF}")


# ---------------------------------------------------------------------
# PROMPTS
# ---------------------------------------------------------------------
def ask_for_name():
    """Ask user for the name of a movie and return this value.

    Return early when user wants to cancel and '..' is entered.
    """
    while True:
        movie_name = input(f"{style.PROMPT}\nEnter the movie name "
                           f"or '..' to cancel: {style.OFF}").strip()
        if movie_name == "":
            print(f"{style.ERROR}\nMovie name should not be empty!{style.OFF}")
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
        movie_name = input(f"{style.PROMPT}\nEnter movie name, a part of it "
                           f"or '..' to cancel: {style.OFF}").strip()
        if movie_name == "":
            print(f"{style.ERROR}Movie name or part of it should not be empty!{style.OFF}")
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
            rating = input(f"{style.PROMPT}{prompt}{style.OFF}").strip()
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
            print(f"{style.ERROR}Invalid input{style.OFF}")
        except RatingOutOfRangeError:
            print(f"{style.ERROR}Rating must be between 0 and 10 (inclusive).{style.OFF}")


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
            year = input(f"{style.PROMPT}{prompt}{style.OFF}").strip()
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
            print(f"{style.ERROR}error_msg{style.OFF}")


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
            country = input(f"{style.PROMPT}{prompt}{style.OFF}").strip()
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
            print(f"{style.ERROR}error_msg{style.OFF}")


def ask_for_sort_order():
    """Ask the user for descending or ascending order."""
    accepted_input = {"first", "last"}
    while True:
        try:
            sort_order = input(f"{style.PROMPT}Do you want to see the "
                               "latest movies first or last?"
                               f"\nEnter 'first' or 'last: {style.OFF}").strip().lower()
            if not sort_order in accepted_input:
                raise InvalidInputError
            return sort_order
        except (ValueError, InvalidInputError):
            print(f"{style.ERROR}Invalid input{style.OFF}")


# ---------------------------------------------------------------------
# DYNAMIC MOVIE RETRIEVAL AND SELECTION FROM API
# ---------------------------------------------------------------------
def list_api_search_results(search_term):
    """Print retrieved movies from API and return a dispatch table
    to allow user selection.
    """
    results_raw = api.find_movies(search_term)
    results = data_processing.std_search_results_from_api(results_raw)
    dispatch_table = {}
    output = ""
    for i, movie in enumerate(results, start=1):
        dispatch_table[str(i)] = (movie["imdbID"], movie["title"])
        output += (f"{i:>3}: {movie['title']} ({movie['year']}) [{movie['type']}]\n")
    return output, dispatch_table


def select_movie_from_api(search_term):
    """Return imdbID and title for a specific movie
    selected from a list of movies automatically retrieved via API.
    """
    output, dispatch_table = list_api_search_results(search_term)
    print(f"{style.INFO}Movies matching the search term "
          f"'{search_term}':\n{style.OFF}")
    print(f"{style.INFO}{output}{style.OFF}")
    while True:
        choice = get_user_choice(len(dispatch_table),
                                 start_at_zero=False,
                                 prompt="Please make your choice")
        if choice == "..":
            choice = False
            print_action_cancelled()
            break
        elif is_valid_user_choice(choice, dispatch_table):
            break
    if choice:
        imdbID, title = dispatch_table[choice]
        return imdbID, title
    return (False, False)


def get_movie_details_from_api(imdbID):
    """Return movie object for the given imdbID."""
    movie_object_raw = api.fetch_movie_details(imdbID)
    movie_object = data_processing.std_movie_from_api(movie_object_raw)
    return movie_object


# ---------------------------------------------------------------------
# CRUD OPERATIONS
# ---------------------------------------------------------------------
def add_movie_rating():
    """Add movie rating to the Database."""
    # -----------------------------------------------------------------
    # Always return early if user wants to cancel / has entered '..'.
    data_current_user = data_processing.get_movies(CURRENT_USER_ID)
    data_all_users = data_processing.get_movies()
    movie_title = ask_for_name()
    if movie_title is False:
        return False
    # -----------------------------------------------------------------
    # Dynamically retrieve movie suggestions
    # for the given title via API
    imdbID, movie_title = select_movie_from_api(movie_title)
    if movie_title is False:
        return False
    # -----------------------------------------------------------------
    # Check if current user already rated the movie.
    if is_in_movies(data_current_user, movie_title):
        print(f"{style.ERROR}You already rated '{movie_title}'!{style.OFF}")
        return False
    # -----------------------------------------------------------------
    # If movie is found in the movies table
    # skip fetching movie details.
    if is_in_movies(data_all_users, movie_title):
        # get movie details from database
        movie_details = data_processing.get_movie(movie_title)
        print(f"{style.INFO}Found movie '{movie_title}' in the database.")
        print(f"Skip fetching movie details from OMDB...{style.OFF}")
        movie_id = movie_details["id"]
    # -----------------------------------------------------------------
    # ...otherwise fetch movie details from API.
    else:
        movie_obj = get_movie_details_from_api(imdbID)[movie_title]
        print(movie_obj)
        year = movie_obj["year"]
        image_url = movie_obj["image_url"]
        omdb_rating = movie_obj["omdb_rating"]
        countries = movie_obj["country"]
        print(f"{style.INFO}Movie details complete. Adding movie to database...{style.OFF}")
        # Add movie to the database.
        movie_id = data_processing.add_movie(movie_title, year, image_url, omdb_rating)
        print(f"{style.INFO}Successfully added '{movie_title}'. (ID: {movie_id}){style.OFF}")
        # Finally add new country objects to the database...
        # ...and create movie-country relationships.
        print(f"{style.INFO}Processing country details...{style.OFF}")
        for country in countries:
            add_country_if_new(country)
            country_id = data_processing.get_country_by_name(country)["id"]
            data_processing.add_movie_country_relationship(movie_id, country_id)
            print(f"{style.INFO}Successfully created movie-country relationship for '{country}'.{style.OFF}")
    # -----------------------------------------------------------------
    # Finally ask for the rating and store it in the database.
    rating = ask_for_rating()
    if rating is False:
        return False
    data_processing.add_rating(CURRENT_USER_ID, movie_id, rating)
    print(f"{style.INFO}Successfully added rating for movie '{movie_title}'.{style.OFF}")
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
        print(f"{style.INFO}Adding country data to database...{style.OFF}")
        name = country_object["name"]
        code = country_object["code"]
        country_id = data_processing.add_country(name, code)
        print(f"{style.INFO}Successfully added country data for "
              f"'{name}'. (ID: {country_id}){style.OFF}")
        return country_id
    return False


def delete_movie_rating():
    """Delete a movie rating from the database."""
    data = movie_storage.get_movies()
    movie_title = ask_for_name()
    # Return early if user wants to cancel.
    if movie_title is False:
        return False
    # Only remove film if it exists.
    if not is_in_movies(data, movie_title):
        print(f"{style.ERROR}Movie '{movie_title}' doesn't exist!{style.OFF}")
        # Recurse to start the function again.
        delete_movie_rating()
    else:
        movie_storage.delete_movie(movie_title)
        print(f"{style.INFO}Movie '{movie_title}' successfully deleted{style.OFF}")
    return True


def update_movie_rating():
    """Ask the user to enter a movie name
    and update the movie’s rating in the database.
    """
    data = movie_storage.get_movies()
    movie_title = ask_for_name()
    # Return early if user wants to cancel.
    if movie_title is False:
        return False
    # Check if the film already exists.
    if not is_in_movies(data, movie_title):
        print(f"{style.ERROR}Movie '{movie_title}' doesn't exist!{style.OFF}")
        # Recurse to start the function again:
        update_movie_rating()
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
        print(f"{style.INFO}Movie '{movie_title}' successfully updated{style.OFF}")
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
    data = movie_storage.get_movies()
    ratings = get_ratings(data)
    average_rating = get_average_rating(ratings)
    median_rating = get_median_rating(ratings)
    best_movies = get_best_or_worst_movies(data)
    worst_movies = get_best_or_worst_movies(data, get_best=False)
    # Show stats...
    print(f"{style.OUTPUT}\nAverage rating: {average_rating}")
    print(f"Median rating: {median_rating}")
    # ...and make sure multiple best and worst movies are shown.
    print("Best movie(s): ", end="")
    print(" | ".join(format_movie_entry(title,
                                        data[title]['year'],
                                        data[title]['rating'])
                     for title in best_movies))
    print("Worst movie(s): ", end="")
    print(f"{' | '.join(format_movie_entry(title,
                                        data[title]['year'],
                                        data[title]['rating'])
                     for title in worst_movies)}{style.OFF}")


def get_random_movie():
    """Show the details for a random movie."""
    data = movie_storage.get_movies()
    movie_titles = get_movie_titles(data)
    random_title = random.choice(movie_titles)
    rating = data[random_title]["rating"]
    year = data[random_title]["year"]
    print(f"{style.OUTPUT}\nYour movie for tonight: "
          f"{random_title} ({year}), it's rated {rating}{style.OFF}")


def search_movie():
    """Ask the user to enter a part of a movie name,
    and then search all movies in the database
    and prints all movies that matched the user’s query,
    along with the rating. (case-insensitive).

    If movie's title could not be found,
    display suggestions received by fuzzy search.
    """
    data = movie_storage.get_movies()
    search_term = ask_for_name_part()
    # Return early if user wants to cancel.
    if search_term is False:
        return False
    found = False
    for title, details in data.items():
        if search_term.lower() in title.lower():
            print(f"{style.OUTPUT}"
                  f"{format_movie_entry(title,
                                        details['year'],
                                        details['rating'])}"
                  f"{style.OFF}")
            found = True
    if not found:
        # suggest titles by fuzzy search
        print()
        print(f"{style.INFO}A movie containing '{search_term}' "
              f"could not be found.{style.OFF}", end="")
        # look for alternatives using fuzzy search
        suggestions = difflib.get_close_matches(search_term, list(data), 4, 0.3)
        # show only if fuzzy search finds alternatives
        if not len(suggestions) == 0:
            print(f"{style.INFO} Did you mean:{style.OFF}", end="\n")
            for suggestion in suggestions:
                title = suggestion
                year = data[suggestion]["year"]
                rating = data[suggestion]["rating"]
                print(f"{style.OUTPUT}{format_movie_entry(title, year, rating)}{style.OFF}")
    return True


def sort_movies_by_rating():
    """Sort movies in descending order by their rating."""
    data = movie_storage.get_movies()
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
    data = movie_storage.get_movies()
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
        prompt="Enter minimum rating (leave blank for no minimum rating): ")
    year_start = ask_for_year(
        allow_blank=True,
        prompt="Enter start year (leave blank for no start year): ")
    year_end = ask_for_year(
        allow_blank=True,
        prompt="Enter end year (leave blank for no end year): ")
    data = movie_storage.get_movies()
    filtered_movies = dict(filter(
        lambda movie: apply_filter(
            movie,
            year_start,
            year_end,
            rating_threshold), data.items()))
    print(f"{style.OUTPUT}\nFiltered Movies:{style.OFF}")
    # sort movies by year (descending)
    filtered_movies_sorted = dict(sorted(filtered_movies.items(),
                                         key=lambda item: item[1]["year"],
                                         reverse=True))
    list_movies(filtered_movies_sorted, nested_call=True)


def not_implemented():
    """Dummy function."""
    print(f"{style.ERROR}Not implemented{style.OFF}")


def do_nothing():
    """Another dummy function."""
    return True


def invalid_choice():
    """Display a message for invalid menu choices."""
    print(f"{style.ERROR}Invalid choice{style.OFF}")


DISPATCH_TABLE = {
    "0": do_nothing,
    "1": list_movies,
    "2": add_movie_rating,
    "3": delete_movie_rating,
    "4": update_movie_rating,
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
    print(f"{style.INFO}\nBye!\n{style.OFF}")


def main():
    """Main function for testing when running the script under main."""
    pass


if __name__ == "__main__":
    main()
