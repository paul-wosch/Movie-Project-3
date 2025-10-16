"""This module contains all sqlite queries used.

It also serves as a documentation for the different key value pairs
needed to pass when calling the different sqlite query functions
performing CRUD operations to the database.

Simplified database structure for the project:

    users: id:int (PK), user_name:text (unique), first_name:text, last_name:text, password_hash:text
    movies: id:int (PK), title:text (unique), year:int, image_url:text, imdb_rating:real
    countries: id:int (PK), name:text, code:text, flag_url:text
    movies_countries: movie_id:int (FK), country_id:int (FK)
    ratings: user_id:int (PK, FK), movie_id:int (PK, FK), rating:real, note:text
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
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        user_name       TEXT UNIQUE NOT NULL,
        first_name      TEXT,
        last_name       TEXT,
        password_hash   TEXT
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
        image_url   TEXT,
        imdb_rating REAL
    )"""
CREATE_TABLE_MOVIES_COUNTRIES = """
        CREATE TABLE IF NOT EXISTS movies_countries (
        movie_id    INTEGER,
        country_id  INTEGER,
        FOREIGN KEY(movie_id) REFERENCES movies(id),
        FOREIGN KEY(country_id) REFERENCES countries(id)
    )"""
CREATE_TABLE_RATINGS = """
    CREATE TABLE IF NOT EXISTS ratings (
        rating      REAL NOT NULL,
        user_id     INTEGER,
        movie_id    INTEGER,
        note        TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(movie_id) REFERENCES movies(id)
    )"""
# ---------------------------------------------------------------------
# CREATE
# ---------------------------------------------------------------------
ADD_USER = ""
ADD_COUNTRY = "INSERT INTO countries (name, code) VALUES (:name, :code)"
ADD_MOVIE = ("INSERT INTO movies (title, year, image_url, imdb_rating)"
             "VALUES (:title, :year, :image_url, :imdb_rating)")
ADD_RATING = ("INSERT INTO ratings (user_id, movie_id, rating, note)"
              "VALUES (:user_id, :movie_id, :rating, :note)")
ADD_MOVIE_COUNTRY = """
    INSERT INTO movies_countries (movie_id, country_id)
    VALUES (:movie_id, :country_id)
"""
# ---------------------------------------------------------------------
# READ
# ---------------------------------------------------------------------
GET_MOVIES = """
    SELECT
        movies.title,
        movies.year,
        movies.image_url,
        movies.imdb_rating,
        ratings.rating,
        ratings.note,
        movies.id
    FROM ratings
    JOIN
        users ON ratings.user_id = users.id
    JOIN
        movies ON ratings.movie_id = movies.id
    WHERE ratings.user_id = :user_id
"""
GET_MOVIES_ALL_USERS = """
    SELECT
        movies.title,
        movies.year,
        movies.image_url,
        movies.imdb_rating,
        movies.id
    FROM movies
"""
GET_MOVIE_BY_TITLE = """
    SELECT
        movies.id,
        movies.title,
        movies.year,
        movies.image_url,
        movies.imdb_rating
    FROM movies
    WHERE movies.title = :title
"""
GET_MOVIE_BY_ID = """
    SELECT
        movies.id,
        movies.title,
        movies.year,
        movies.image_url,
        movies.imdb_rating
    FROM movies
    WHERE movies.id = :id
"""
GET_COUNTRY_BY_CODE = "SELECT * FROM countries WHERE code = :code"
GET_COUNTRY_BY_NAME = "SELECT * FROM countries WHERE name = :name"
GET_COUNTRY_BY_ID = "SELECT * FROM countries WHERE id = :id"
GET_COUNTRIES_FOR_MOVIE = """
    SELECT * FROM countries
    JOIN
        movies_countries ON movies_countries.country_id = countries.id
    JOIN
        movies ON movies_countries.movie_id = movies.id
    WHERE movies.id = :id
        
"""
GET_RATING = """
    SELECT * FROM ratings
    WHERE user_id = :user_id AND movie_id = :movie_id
"""
# ---------------------------------------------------------------------
# UPDATE
# ---------------------------------------------------------------------
UPDATE_USER = ""
UPDATE_MOVIE = """
    UPDATE movies 
    SET title = :title, year = :year, image_url = :image_url, imdb_rating = :imdb_rating
    WHERE id = :id
"""
UPDATE_RATING = """
    UPDATE ratings
    SET rating = :rating, note = :note
    WHERE user_id = :user_id AND movie_id = :movie_id
"""
# ---------------------------------------------------------------------
# DELETE
# ---------------------------------------------------------------------
DELETE_USER = ""
DELETE_RATING = """
    DELETE FROM ratings
    WHERE user_id = :user_id AND movie_id = :movie_id
"""
