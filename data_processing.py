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
                                  "country": movie[2],
                                  "rating": movie[3],
                                  "note": movie[4]}
                       for movie in movies}
    else:
        movies = db.get_movies()
        movies_dict = {movie[0]: {"year": movie[1],
                                  "country": movie[2]}
                       for movie in movies}
    return movies_dict


def get_country_code():
    country_code = "US"
    print(country_code)
    print(db.get_country(country_code))
    print(pycountry.countries.lookup('us'))


def add_country():
    # --- ADD COUNTRY ---
    country_name = "United Kingdom"
    country = pycountry.countries.lookup(country_name)
    country_dict = dict(country)
    code = country_dict["alpha_2"]
    params = {"name": country_name, "code": code}
    if not db.get_country(code):
        db.add_country(params)


def add_movie():
    # --- ADD MOVIE ---
    title = "The Frog 3"
    year = "1992"
    country_code = "ES"
    # country_id = get_country("DE")[0][0]
    # params = {"title": title, "year": year, "country_id": country_id}
    params = {"title": title, "year": year, "country_code": country_code}
    db.add_movie(params)


def rate_movie():
    """Rate new or existing movie."""
    pass


def main():
    # print(get_movies(1))
    pass


if __name__ == "__main__":
    main()