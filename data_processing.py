import pycountry
from sqlalchemy.exc import SQLAlchemyError
import database as db


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


def get_country_by_name(name):
    """Return a country object for the given search value."""
    params = {"name": name}
    country = db.get_country(params)
    # Retrieve country object from database...
    if country:
        country = country[0]
        country_dict = {"id": country[0],
                        "name": country[1],
                        "code": country[2]
                        }
    # ...or generate a new one using the 'pycountry' module.
    else:
        # Use temporary id to tag newly generated country object.
        temp_id = -1
        country = pycountry.countries.lookup(name)
        country_dict = {"id": temp_id,
                        "name": country.name,
                        "code": country.alpha_2
                        }
    return country_dict


def get_countries_for_movie(movie_id):
    """Return a list of country objects for the given movie id."""
    params = {"id": movie_id}
    countries = db.get_countries_for_movie(params)
    countries_list = [{"id": country[0],
                       "name": country[1],
                       "code": country[2],
                       "flag_url": country[3]
                       } for country in countries]
    return countries_list


def add_country(name, code):
    """Add country to the database and return the id."""
    params = {"name": name, "code": code}
    db.add_country(params)
    return get_country_by_name(name)["id"]


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


def main():
    """Main function for testing when running the script under main."""
    # initialize_database(DB_INIT_QUERIES)
    # print(get_movies())
    # print(get_movie(1, find_by_id=True))
    # print(get_country_by_name("United States"))
    # print(get_country_by_name("Poland"))
    # print(get_countries_for_movie(1))
    pass


if __name__ == "__main__":
    main()