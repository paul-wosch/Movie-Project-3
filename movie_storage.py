import json

MOVIES_FILE = "movies.json"


def serialize_to_json(input_obj):
    """Return the input object as json formatted string."""
    return json.dumps(input_obj)


def deserialize_from_json(json_str):
    """Return a corresponding python object from a json string."""
    return json.loads(json_str)


def get_movies():
    """Return a dictionary of dictionaries that
    contains the movies information in the database
    from a JSON file.
    """
    with open(MOVIES_FILE, "r", encoding="utf-8") as file_obj:
        movies = json.load(file_obj)
    return movies


def save_movies(movies):
    """Get all movies as an argument and save them to a JSON file."""
    with open(MOVIES_FILE, "w", encoding="utf-8") as file_obj:
        json.dump(movies, file_obj, indent=2)


def add_movie(title, year, rating):
    """Add a movie to the movies-database.

    Load the information from the JSON file, add the movie,
    and save it. The function doesn't need to validate the input.
    """
    data = get_movies()
    data[title] = {"rating": rating, "year": year}
    save_movies(data)


def delete_movie(title):
    """Delete a movie from the movies-database.

    Load the information from the JSON file, delete the movie,
    and save it. The function doesn't need to validate the input.
    """
    data = get_movies()
    del data[title]
    save_movies(data)


def update_movie(title, year, rating):
    """Update a movie from the movies-database.

    Load the information from the JSON file, updates the movie,
    and save it. The function doesn't need to validate the input.
    """
    data = get_movies()
    data[title] = {"rating": rating, "year": year}
    save_movies(data)


def main():
    """Test any of the modul's functions here."""
    print()


if __name__ == "__main__":
    main()
