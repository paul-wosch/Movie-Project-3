"""This module contains all sqlite queries used.

Those queries serve as a documentation for the different key value pairs
needed to pass when calling the customized python functions
performing CRUD operations to the database.

Database structure for the project:

Paste the following code to the ERD editor on
https://app.eraser.io/#note-title-editor

--- BEGIN CODE ---
// title
title Movie Rating Platform Data Model

// define tables
users [icon: user, color: yellow]{
  id int pk auto
  user_name text unique
  first_name text
  last_name text
  password_hash text
}

movies [icon: film, color: blue]{
  id int pk auto
  imdb_id text unique
  title text
  year int
  image_url text
  imdb_rating real
}

countries [icon: flag, color: green]{
  id int pk auto
  name text
  code text
}

movies_countries [icon: globe, color: lightblue]{
  movie_id int fk
  country_id int fk
}

ratings [icon: star, color: orange]{
  user_id int fk
  movie_id int fk
  rating real
  note text
}

// define relationships
movies_countries.movie_id > movies.id
movies_countries.country_id > countries.id
ratings.user_id > users.id
ratings.movie_id > movies.id
--- END CODE ---
"""

# ---------------------------------------------------------------------
# INITIALIZE
# ---------------------------------------------------------------------
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
        imdb_id     TEXT UNIQUE NOT NULL,
        title       TEXT NOT NULL,
        year        INTEGER,
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
ADD_DEFAULT_USER = "INSERT OR IGNORE INTO users (user_name) VALUES ('default')"
# ---------------------------------------------------------------------
# CREATE
# ---------------------------------------------------------------------
ADD_USER = """
           INSERT INTO users (
               user_name,
               first_name,
               last_name,
               password_hash)
           VALUES (:user_name, :first_name, :last_name, :password_hash)
"""
ADD_COUNTRY = "INSERT INTO countries (name, code) VALUES (:name, :code)"
ADD_MOVIE = ("INSERT INTO movies (imdb_id, title, year, image_url, imdb_rating)"
             "VALUES (:imdb_id, :title, :year, :image_url, :imdb_rating)")
ADD_RATING = ("INSERT INTO ratings (user_id, movie_id, rating, note)"
              "VALUES (:user_id, :movie_id, :rating, :note)")
ADD_MOVIE_COUNTRY = """
    INSERT INTO movies_countries (movie_id, country_id)
    VALUES (:movie_id, :country_id)
"""
# ---------------------------------------------------------------------
# READ
# ---------------------------------------------------------------------
GET_USER_BY_USERNAME = "SELECT * FROM users WHERE user_name = :user_name"
GET_USER_BY_ID = "SELECT * FROM users WHERE id = :id"
GET_MOVIES = """
    SELECT
        movies.id,
        movies.imdb_id,
        movies.title,
        movies.year,
        movies.image_url,
        movies.imdb_rating,
        ratings.rating,
        ratings.note
    FROM ratings
    JOIN
        users ON ratings.user_id = users.id
    JOIN
        movies ON ratings.movie_id = movies.id
    WHERE ratings.user_id = :user_id
"""
GET_MOVIES_ALL_USERS = """
    SELECT
        movies.id,
        movies.imdb_id,
        movies.title,
        movies.year,
        movies.image_url,
        movies.imdb_rating
    FROM movies
"""
GET_MOVIE_BY_TITLE = """
    SELECT
        movies.id,
        movies.imdb_id,
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
        movies.imdb_id,
        movies.title,
        movies.year,
        movies.image_url,
        movies.imdb_rating
    FROM movies
    WHERE movies.id = :id
"""
GET_MOVIE_BY_IMDBID = """
    SELECT
        movies.id,
        movies.imdb_id,
        movies.title,
        movies.year,
        movies.image_url,
        movies.imdb_rating
    FROM movies
    WHERE movies.imdb_id = :imdb_id
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
    SET imdb_id = :imdb_id, title = :title, year = :year, image_url = :image_url, imdb_rating = :imdb_rating
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
# ---------------------------------------------------------------------
# COUNT
# ---------------------------------------------------------------------
COUNT_RATINGS_FOR_USER = "SELECT COUNT(*) FROM ratings WHERE user_id = :user_id"
