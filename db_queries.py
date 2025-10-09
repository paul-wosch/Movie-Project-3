# --- DATA MODEL ------------------------------------------------------
#
# users: id:int (PK), user_name (unique), first_name, last_name
# movies: id:int (PK), title:text (unique), year:int, country_id:in (FK)
# countries: id:int (PK), name:text, code:text
# users_movies: user_id:int (PK, FK), movie_id:int (PK, FK), rating:real
#
#
# ---------------------------------------------------------------------

# INITIALIZE DATABASE WITH TABLES
CREATE_TABLE_MOVIES_EXAMPLE = """
    CREATE TABLE IF NOT EXISTS movies (
        id      INTEGER PRIMARY KEY AUTOINCREMENT,
        title   TEXT UNIQUE NOT NULL,
        year    INTEGER NOT NULL,
        rating  REAL NOT NULL
        )"""
CREATE_TABLE_USERS = """
    CREATE TABLE IF NOT EXISTS users (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        user_name   TEXT UNIQUE NOT NULL,
        first_name  TEXT,
        last_name   TEXT
    )"""
CREATE_TABLE_COUNTRIES = """
    CREATE TABLE IF NOT EXISTS countries (
        id      INTEGER PRIMARY KEY AUTOINCREMENT,
        name    TEXT UNIQUE NOT NULL,
        code    TEXT UNIQUE NOT NULL
    )"""
CREATE_TABLE_MOVIES = """
    CREATE TABLE IF NOT EXISTS movies (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        title       TEXT UNIQUE NOT NULL,
        year        INTEGER NOT NULL,
        country_id  INTEGER,
        FOREIGN KEY(country_id) REFERENCES countries(id)
    )"""
CREATE_TABLE_USERS_MOVIES = """
    CREATE TABLE IF NOT EXISTS users_movies (
        rating      REAL NOT NULL,
        user_id     INTEGER,
        movie_id    INTEGER,
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(movie_id) REFERENCES movies(id)
    )"""
# CREATE
CREATE_USER = ""
CREATE_MOVIE = ""
# READ

# UPDATE
UPDATE_USER = ""
UPDATE_MOVIE = ""
# DELETE
DELETE_USER = ""
DELETE_MOVIE = ""
