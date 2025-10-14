import pycountry
from sqlalchemy.exc import SQLAlchemyError
import database as db


# ---------------------------------------------------------------------
# CRUD OPERATIONS
# ---------------------------------------------------------------------
def get_movies(user_id=None):
    """Return a dictionary of movie dictionaries for the given user.

    If user id is None return all movies.
    """
    params = {"user_id": user_id}
    if user_id:
        movies = db.get_movies(params)
        movies_dict = {movie[0]: {"year": movie[1],
                                  "image_url": movie[2],
                                  "omdb_rating": movie[3],
                                  "rating": movie[4],
                                  "note": movie[5]}
                       for movie in movies}
    else:
        movies = db.get_movies()
        movies_dict = {movie[0]: {"year": movie[1],
                                  "image_url": movie[2],
                                  "omdb_rating": movie[3]}
                       for movie in movies}
    return movies_dict


def get_movie(search_value, find_by_id=False) -> dict:
    """Return a movie object for the given search value (id/title)."""
    if find_by_id:
        params = {"id": search_value}
    else:
        params = {"title": search_value}
    movie = db.get_movie(params)[0]
    movie_object = {"id": movie[0],
                    "title": movie[1],
                    "year": movie[2],
                    "image_url": movie[3],
                    "omdb_rating": movie[4]
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
        emoji = pycountry.countries.get(alpha_2=code).flag
        country_dict = {"id": id,
                        "name": name,
                        "code": code,
                        "emoji": emoji
                        }
    # ...or generate a new one using the 'pycountry' module.
    else:
        country = pycountry.countries.lookup(search_string)
        # Use temporary id to tag newly generated country object.
        temp_id = -1
        name = country.name
        code = country.alpha_2
        emoji = country.flag
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
                       "flag_url": country[3],
                       "emoji": pycountry.countries.get(alpha_2=country[2]).flag
                       } for country in countries]
    return countries_list


def add_country(name, code):
    """Add country to the database and return the id."""
    params = {"name": name, "code": code}
    db.add_country(params)
    return get_country_by_name(name)["id"]


def add_movie_country_relationship(movie_id, country_id):
    """Add movie-country relationship to the database."""
    params = {"movie_id": movie_id, "country_id": country_id}
    db.add_movie_country_relationship(params)


def add_movie(title, year, image_url, omdb_rating):
    """Add movie to the database and return the id."""
    params = {"title": title,
              "year": year,
              "image_url": image_url,
              "omdb_rating": omdb_rating}
    db.add_movie(params)
    return get_movie(title)["id"]


def add_rating(user_id, movie_id, rating, note=""):
    """Add movie rating to the database."""
    params = {"user_id": user_id,
              "movie_id": movie_id,
              "rating": rating,
              "note": note
              }
    db.add_rating(params)


# ---------------------------------------------------------------------
# PROCESS RECEIVED DATA FROM API
# ---------------------------------------------------------------------
def std_movie_from_api_search(movie_from_api):
    """Return a standardized movie object for a movie retrieved from the API."""
    movie_object = {"title": movie_from_api["Title"],
                    "year": movie_from_api["Year"],
                    "imdbID": movie_from_api["imdbID"],
                    "type": movie_from_api["Type"]
                    }
    return movie_object


def std_search_results_from_api(results):
    """Return API search results as a standardized list
    in reverse chronological order.
    """
    if results:
        return sorted([
            std_movie_from_api_search(result) for result in results],
            key=lambda x: x['year'], reverse=True)
    return []


def std_movie_from_api(movie):
    """Return standardized movie object for a single movie
    retrieved from the API.
    """
    movie_object = {movie["Title"]: {"year": movie["Year"],
                                     "image_url": movie["Poster"],
                                     "omdb_rating": movie["imdbRating"],
                                     "country": movie["Country"].split(", ")
                                     }}
    return movie_object


def main():
    """Main function for testing when running the script under main."""
    # initialize_database(DB_INIT_QUERIES)
    # print(get_movies())
    # print(get_movie(1, find_by_id=True))
    # print(get_country_by_name("United States"))
    # print(get_country_by_name("Poland"))
    # print(get_countries_for_movie(16))
    # country flag lookup
    # print(pycountry.countries.lookup("United States"))
    # Country(alpha_2='US', alpha_3='USA', flag='🇺🇸', name='United States', numeric='840', official_name='United States of America')
    # print(pycountry.countries.lookup("United States").flag)
    pass


if __name__ == "__main__":
    main()