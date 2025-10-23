import pycountry
from myapp.db import database as db

YEAR_STR_LENGTH = 4


# ---------------------------------------------------------------------
# CRUD OPERATIONS
# ---------------------------------------------------------------------
def get_user(search_value, find_by_id=False) -> dict:
    """Return a user object for the given 'id' or 'user_name'."""
    if find_by_id:
        params = {"id": search_value}
    else:
        params = {"user_name": search_value}
    user = db.get_user(params)
    if user:
        user = user[0]
        user_object = {"id": user[0],
                       "user_name": user[1],
                       "first_name": user[2],
                        "last_name": user[3],
                        "password_hash": user[4]
                        }
        return user_object
    return {}


def add_user(user_name, password_hash, first_name="", last_name="") -> int:
    """Add a user to the database and return the user id."""
    params = {'user_name': user_name,
              'first_name': first_name,
              'last_name': last_name,
              'password_hash': password_hash}
    db.add_user(params)
    return get_user(user_name)["id"]


def get_movies(user_id=None):
    """Return a dictionary of movie dictionaries for the given user.

    If user id is None return all movies.
    """
    params = {"user_id": user_id}
    if user_id:
        movies = db.get_movies(params)
        # movie[1] corresponds to 'imdb_id', main key for the sub dictionary
        movies_dict = {movie[1]: {"movie_id": movie[0],
                                  "title": movie[2],
                                  "year": movie[3],
                                  "image_url": movie[4],
                                  "imdb_rating": movie[5],
                                  "rating": movie[6],
                                  "note": movie[7]}
                       for movie in movies}
    else:
        movies = db.get_movies()
        movies_dict = {movie[1]: {"movie_id": movie[0],
                                  "title": movie[2],
                                  "year": movie[3],
                                  "image_url": movie[4],
                                  "imdb_rating": movie[5]}
                       for movie in movies}
    return movies_dict


def get_movie(search_value, find_by_id=False) -> dict:
    """Return a movie object for the given 'id' or 'imdb_id'."""
    if find_by_id:
        params = {"id": search_value}
    else:
        params = {"imdb_id": search_value}
    movie = db.get_movie(params)[0]
    movie_object = {"id": movie[0],
                    "imdb_id": movie[1],
                    "title": movie[2],
                    "year": movie[3],
                    "image_url": movie[4],
                    "imdb_rating": movie[5]
                    }
    return movie_object


def get_country_by_name(search_string):
    """Return a country object for the given search value."""
    # Retrieve country object from database...
    params = {"name": search_string}
    country = db.get_country(params)
    if country:
        country = country[0]
        # Extract attributes
        id = country[0]
        name = country[1]
        code = country[2]
        emoji = get_country_emoji(name)
        country_dict = {"id": id,
                        "name": name,
                        "code": code,
                        "emoji": emoji
                        }
    # ...or generate a new one using the 'pycountry' module.
    else:
        # Use temporary id to tag newly generated country object.
        temp_id = -1
        try:
            country = pycountry.countries.lookup(search_string)
            name = country.name
            code = country.alpha_2
            emoji = country.flag
        except LookupError:
            name = search_string
            code = search_string
            emoji = search_string
        country_dict = {"id": temp_id,
                        "name": name,
                        "code": code,
                        "emoji": emoji
                        }
    return country_dict


def get_countries_for_movie(movie_id):
    """Return a list of country objects for the given movie id."""
    params = {"id": movie_id}
    countries = db.get_countries_for_movie(params)
    countries_list = [{"id": country[0],
                       "name": country[1],
                       "code": country[2],
                       "emoji": get_country_emoji(country[1])
                       } for country in countries]
    return sorted(countries_list, key=lambda item: item["name"])


def add_country(name, code):
    """Add country to the database and return the id."""
    params = {"name": name, "code": code}
    db.add_country(params)
    return get_country_by_name(name)["id"]


def add_movie_country_relationship(movie_id, country_id):
    """Add movie-country relationship to the database."""
    params = {"movie_id": movie_id, "country_id": country_id}
    db.add_movie_country_relationship(params)


def add_movie(imdb_id, title, year, image_url, imdb_rating):
    """Add movie to the database and return the id."""
    params = {"imdb_id": imdb_id,
              "title": title,
              "year": year,
              "image_url": image_url,
              "imdb_rating": imdb_rating}
    db.add_movie(params)
    return get_movie(imdb_id)["id"]


def get_rating(user_id, movie_id):
    """Return the user's rating for a movie."""
    params = {"user_id": user_id,
              "movie_id": movie_id
              }
    rating_obj = db.get_rating(params)
    rating_obj = rating_obj[0]
    rating = rating_obj[0]
    note = rating_obj[-1]
    rating_dict = {"rating": rating,
                   "user_id": user_id,
                   "movie_id": movie_id,
                   "note": note
                   }
    return rating_dict


def add_rating(user_id, movie_id, rating, note=""):
    """Add movie rating to the database."""
    params = {"user_id": user_id,
              "movie_id": movie_id,
              "rating": rating,
              "note": note
              }
    db.add_rating(params)


def delete_rating(user_id, movie_id):
    """Delete rating for a movie from the database."""
    params = {"user_id": user_id,
              "movie_id": movie_id
              }
    db.delete_rating(params)


def update_rating(user_id, movie_id, rating, note):
    """Update rating for a movie in the database."""
    params = {"user_id": user_id,
              "movie_id": movie_id,
              "rating": rating,
              "note": note
              }
    db.update_rating(params)


# ---------------------------------------------------------------------
# PROCESS RECEIVED DATA FROM API
# ---------------------------------------------------------------------
def std_year_from_api(movie_obj):
    """Return standardized year for a movie retrieved from the API.

    If the movie was already selected by the user
    and standardization fails: Let user manually enter the year.
    """
    year = movie_obj["Year"]
    # Fallback 1 - get year from last 4 chars of the 'Released' field
    if not is_valid_year(year):
        year = movie_obj["Released"][-4:]
    # Fallback 2 - set year to empty string
    if not is_valid_year(year):
        year = ""
    return year


def std_movie_object_from_api(movie_obj):
    """Return a standardized movie object for a movie during an API search."""
    movie_object = {"title": movie_obj["Title"],
                    "imdb_id": movie_obj["imdbID"],
                    "year": movie_obj["Year"],
                    "type": movie_obj["Type"]
                    }
    return movie_object


def std_extended_movie_object_from_api(movie_obj):
    """Return standardized movie object for a single movie
    retrieved from the API and selected by a user.
    """
    countries = movie_obj["Country"].split(", ")
    countries = [std_country_name_from_api_or_db(country) for country in countries]
    year = std_year_from_api(movie_obj)
    movie_object = {movie_obj["imdbID"]: {"title": movie_obj["Title"],
                                          "year": year,
                                          "image_url": movie_obj["Poster"],
                                          "imdb_rating": movie_obj["imdbRating"],
                                          "country": countries
                                          }}
    return movie_object


def std_search_results_from_api(results):
    """Return API search results as a standardized list
    in reverse chronological order.
    """
    if results:
        return sorted([
            std_movie_object_from_api(result) for result in results],
            key=lambda x: x['year'], reverse=True)
    return []


def std_country_name_from_api_or_db(country_name):
    """Return standardized country name if possible."""
    try:
        return pycountry.countries.lookup(country_name).name
    except LookupError:
        return country_name


# ---------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------
def is_valid_year(year: str) -> bool:
    """Return True if a year string is valid."""
    if year.isdigit() and len(year) == YEAR_STR_LENGTH:
        return True
    return False


def get_country_emojis_for_movie(movie_id):
    """Return list of country emojis for a given film."""
    return [country["emoji"] for country in get_countries_for_movie(movie_id)]


def get_country_emoji(country_name):
    """Return the country flag emoji for a country."""
    try:
        return pycountry.countries.lookup(country_name).flag
    except LookupError:
        return country_name


def count_movie_ratings_for_user(user_id):
    """Return the number of rated movies for the given user id."""
    params = {"user_id": user_id}
    result = db.count_ratings_for_user(params)
    count = result[0][0]
    return count


def main():
    """Main function for testing when running the script under main."""
    pass


if __name__ == "__main__":
    main()
