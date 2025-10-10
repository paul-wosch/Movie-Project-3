"""This module contains all sqlite queries used.

It also serves as a documentation for the different key value pairs
needed to pass when calling the different sqlite query functions.

Simplified database structure for the project:

    users: id:int (PK), user_name (unique), first_name, last_name
    movies: id:int (PK), title:text (unique), year:int, country_id:in (FK)
    countries: id:int (PK), name:text, code:text
    users_movies: user_id:int (PK, FK), movie_id:int (PK, FK), rating:real
"""

# ---------------------------------------------------------------------
# INITIALIZE
# ---------------------------------------------------------------------
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
# ---------------------------------------------------------------------
# CREATE
# ---------------------------------------------------------------------
ADD_USER = ""
ADD_COUNTRY = "INSERT INTO countries (name, code) VALUES (:name, :code)"
ADD_MOVIE = ("INSERT INTO movies (title, year, country_id)"
             "VALUES (:title, :year, :country_id)")
ADD_RATING = ("INSERT INTO users_movies (rating, user_id, movie_id)"
              "VALUES (:rating, :user_id, :movie_id)")
# ---------------------------------------------------------------------
# READ
# ---------------------------------------------------------------------
LIST_MOVIES = """
    SELECT
        movies.title,
        movies.year,
        countries.name,
        users_movies.rating
    FROM users_movies
    JOIN
        users ON users_movies.user_id = users.id
    JOIN
        movies ON users_movies.movie_id = movies.id
    JOIN
        countries ON countries.id = movies.country_id
    WHERE users_movies.user_id = :user_id
"""
LIST_MOVIES_ALL_USERS = """
    SELECT
        movies.title,
        movies.year,
        countries.name
    FROM movies
    JOIN
        countries ON countries.id = movies.country_id
"""
GET_COUNTRY = "SELECT * FROM countries WHERE code = :code"
# ---------------------------------------------------------------------
# UPDATE
# ---------------------------------------------------------------------
UPDATE_USER = ""
UPDATE_MOVIE = """
    UPDATE movies 
    SET title = :title, year = :year, country_id = :country_id
    WHERE id = :id
"""
UPDATE_RATING = """
    UPDATE users_movies
    SET rating = :rating
    WHERE user_id = :user_id AND movie_id = :movie_id
"""
# ---------------------------------------------------------------------
# DELETE
# ---------------------------------------------------------------------
DELETE_USER = ""
DELETE_RATING = """
    DELETE FROM users_movies
    WHERE user_id = :user_id AND movie_id = :movie_id
"""
