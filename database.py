from sqlalchemy import create_engine, text
from sqlalchemy import event
from sqlalchemy.engine import Engine
import db_queries

# Show SQL queries in the CLI
ECHO_SQL = False
# Define the database URL
DB_URL = "sqlite:///data/movies.sqlite3"
# Queries for database initialization
DB_INIT_QUERIES = [
    db_queries.CREATE_TABLE_USERS,
    db_queries.CREATE_TABLE_COUNTRIES,
    db_queries.CREATE_TABLE_MOVIES,
    db_queries.CREATE_TABLE_RATINGS
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


def initialize_database(queries):
    """Initialize database with the given list of queries."""
    for query in queries:
        modify_database(query, params={})


# ---------------------------------------------------------------------
# CRUD OPERATIONS
# ---------------------------------------------------------------------
def get_movies(params=None):
    """Return movies from the database (for the given user).

    Include rating information only when querying by user.
    """
    if params:
        query = db_queries.LIST_MOVIES
        movies = query_database(query, params)
        return movies
    else:
        query = db_queries.LIST_MOVIES_ALL_USERS
        movies = query_database(query, params={})
        return movies


def get_movie(params):
    """Return a single movie from the database."""
    if params.get("id"):
        query = db_queries.GET_MOVIE_BY_ID
    else:
        query = db_queries.GET_MOVIE_BY_TITLE
    movie = query_database(query, params)
    return movie


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


def add_country(params):
    """Add country to the countries table."""
    query = db_queries.ADD_COUNTRY
    modify_database(query, params)


def add_rating(params):
    """Add rating to the ratings table."""
    query = db_queries.ADD_RATING
    modify_database(query, params)


def add_movie(params):
    """Add movie to the movies table."""
    query = db_queries.ADD_MOVIE
    modify_database(query, params)


def delete_rating(params):
    """Delete a movie's rating in the database."""
    query = db_queries.DELETE_RATING
    modify_database(query, params)


def update_rating(params):
    """Update a movie's rating in the database."""
    query = db_queries.UPDATE_MOVIE
    modify_database(query, params)


def main():
    """Main function for testing when running the script under main."""
    # initialize_database(DB_INIT_QUERIES)
    print(get_country({"id": 1}))
    print(get_country({"name": "Poland"}))

if __name__ == "__main__":
    main()
