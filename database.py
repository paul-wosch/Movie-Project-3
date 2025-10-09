from sqlalchemy import create_engine, text
from sqlalchemy import event
from sqlalchemy.engine import Engine
import db_queries

# Define the database URL
DB_URL = "sqlite:///data/movies.sqlite3"
# Queries for database initialization
DB_INIT_QUERIES = [
    db_queries.CREATE_TABLE_USERS,
    db_queries.CREATE_TABLE_COUNTRIES,
    db_queries.CREATE_TABLE_MOVIES,
    db_queries.CREATE_TABLE_USERS_MOVIES
]

# Create the engine
engine = create_engine(DB_URL, echo=True)


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Enforce foreign key constraints with listener function."""
    dbapi_connection.execute("PRAGMA foreign_keys=ON")


def modify_database(query):
    """Modify database with the given sql query
    to produce permanent changes like
    adding, updating, or deleting objects.
    """
    with engine.connect() as connection:
        connection.execute(text(query))
        connection.commit()


def query_database(query):
    """Return results for the given query from a database."""
    with engine.connect() as connection:
        results = connection.execute(text(query))
    return results.fetchall()


def initialize_database(queries):
    """Initialize database with the given list of queries."""
    for query in queries:
        modify_database(query)


def main():
    initialize_database(DB_INIT_QUERIES)


if __name__ == "__main__":
    main()