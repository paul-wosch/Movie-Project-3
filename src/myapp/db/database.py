from sqlalchemy import create_engine, text
from sqlalchemy import event
from sqlalchemy.engine import Engine
from myapp.db import db_queries
from pathlib import Path

# Get the project root and go up three levels
PROJECT_ROOT = Path(__file__).resolve().parents[3]
# Set path to database
db_path = (PROJECT_ROOT / "data" / "movies.sqlite3").resolve()
# Use 3 slashes for absolute path; ensure POSIX format
DB_URL = f"sqlite:///{db_path.as_posix()}"
# Show SQL queries in the CLI
ECHO_SQL = False
# Queries for database initialization
DB_INIT_QUERIES = [
    db_queries.CREATE_TABLE_USERS,
    db_queries.CREATE_TABLE_COUNTRIES,
    db_queries.CREATE_TABLE_MOVIES,
    db_queries.CREATE_TABLE_MOVIES_COUNTRIES,
    db_queries.CREATE_TABLE_RATINGS,
    db_queries.ADD_DEFAULT_USER
]

# Create the engine
engine = create_engine(DB_URL, echo=ECHO_SQL)


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Enforce foreign key constraints with listener function."""
    dbapi_connection.execute("PRAGMA foreign_keys=ON")


def modify_database(query, params):
    """Modify database with the given sql query
    to produce permanent changes like
    adding, updating, or deleting objects.
    """
    with engine.connect() as connection:
        connection.execute(text(query), params)
        connection.commit()


def query_database(query, params):
    """Return results for the given query from a database."""
    with engine.connect() as connection:
        results = connection.execute(text(query), params)
    return results.fetchall()


def initialize_database(queries=None):
    """Initialize database with the given list of queries."""
    if queries is None:
        queries = DB_INIT_QUERIES
    for query in queries:
        modify_database(query, params={})


# ---------------------------------------------------------------------
# CRUD OPERATIONS
# ---------------------------------------------------------------------
def get_user(params):
    """Return a user's record from the database by id or username."""
    if params.get("id"):
        query = db_queries.GET_USER_BY_ID
    else:
        query = db_queries.GET_USER_BY_USERNAME
    movie = query_database(query, params)
    return movie


def get_movies(params=None):
    """Return movies from the database (for the given user).

    Include rating information only when querying by user.
    """
    if params:
        query = db_queries.GET_MOVIES
        movies = query_database(query, params)
        return movies
    else:
        query = db_queries.GET_MOVIES_ALL_USERS
        movies = query_database(query, params={})
        return movies


def get_movie(params):
    """Return a single movie from the database."""
    if params.get("id"):
        query = db_queries.GET_MOVIE_BY_ID
    elif params.get("imdb_id"):
        query = db_queries.GET_MOVIE_BY_IMDBID
    else:
        query = db_queries.GET_MOVIE_BY_TITLE
    movie = query_database(query, params)
    return movie


def add_user(params):
    """Add user record to the users table."""
    query = db_queries.ADD_USER
    modify_database(query, params)


def add_movie(params):
    """Add movie to the movies table."""
    query = db_queries.ADD_MOVIE
    modify_database(query, params)


def get_country(params):
    """Return country object from the countries table."""
    if params.get("id"):
        query = db_queries.GET_COUNTRY_BY_ID
    elif params.get("code"):
        query = db_queries.GET_COUNTRY_BY_CODE
    else:
        query = db_queries.GET_COUNTRY_BY_NAME
    country = query_database(query, params)
    return country


def get_countries_for_movie(params):
    """Return countries for a given movie id."""
    query = db_queries.GET_COUNTRIES_FOR_MOVIE
    countries = query_database(query, params)
    return countries


def add_country(params):
    """Add country to the countries table."""
    query = db_queries.ADD_COUNTRY
    modify_database(query, params)


def add_movie_country_relationship(params):
    """Add movie-country relationship to movies_countries table."""
    query = db_queries.ADD_MOVIE_COUNTRY
    modify_database(query, params)


def add_rating(params):
    """Add rating to the ratings table."""
    query = db_queries.ADD_RATING
    modify_database(query, params)


def get_rating(params):
    """Return a single rating from the ratings table."""
    query = db_queries.GET_RATING
    rating =  query_database(query, params)
    return rating


def delete_rating(params):
    """Delete a movie's rating in the database."""
    query = db_queries.DELETE_RATING
    modify_database(query, params)


def update_rating(params):
    """Update a movie's rating in the database."""
    query = db_queries.UPDATE_RATING
    modify_database(query, params)


# ---------------------------------------------------------------------
# OTHER QUERIES
# ---------------------------------------------------------------------

def count_ratings_for_user(params):
    """Return the number of movie's rated by a user."""
    query = db_queries.COUNT_RATINGS_FOR_USER
    ratings_count = query_database(query, params)
    return ratings_count


initialize_database()


def main():
    """Main function for testing when running the script under main."""
    pass


if __name__ == "__main__":
    main()
