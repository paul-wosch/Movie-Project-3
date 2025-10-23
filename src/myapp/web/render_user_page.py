"""Provide a template based webpage generator
to display movies rated by a user.
"""
from pathlib import Path
from myapp.models.data_processing import get_movies, get_user, get_country_emojis_for_movie

# Get the project root and go up three levels
PROJECT_ROOT = Path(__file__).resolve().parents[3]
# Set paths to template and output folder
TEMPLATE_FOLDER = "templates"
TEMPLATE_PATH = (PROJECT_ROOT / TEMPLATE_FOLDER).resolve()
TEMPLATE_FILE = "template.html"
TEMPLATE_FILE_PATH = (TEMPLATE_PATH / TEMPLATE_FILE).resolve()
OUTPUT_FOLDER = "static"
OUTPUT_PATH = (PROJECT_ROOT / OUTPUT_FOLDER).resolve()

PLACEHOLDER_TITLE = "__TEMPLATE_TITLE__"
PLACEHOLDER_MAIN = "        __TEMPLATE_MOVIE_GRID__"
INDENTATION = "    "
DUMMY_POSTER_URL = ("https://images.template.net/wp-content/"
                    "uploads/2017/02/17221912/Printable-Blank-Movie-Poster.jpg")
IMDB_URL = "https://imdb.com/title/"


def load_template(template_file):
    """Load and return html template."""
    with open(template_file, "r", encoding="utf-8") as file_obj:
        html_template = file_obj.read()
    return html_template


def write_file(file_name, content):
    """Write a file with the given content."""
    with open(file_name, "w", encoding="utf-8") as file_obj:
        file_obj.write(content)


def write_html_file(template_file, new_file_name, title, content):
    """Write a new html file for the given content."""
    new_file_path = (OUTPUT_PATH / new_file_name).resolve()
    html_template = load_template(template_file)
    html_with_title = html_template.replace(PLACEHOLDER_TITLE, title)
    html_with_content = html_with_title.replace(PLACEHOLDER_MAIN, content)
    write_file(new_file_path, html_with_content)


def indent(n):
    """Return n indentations."""
    return INDENTATION * n


def convert_emoji_to_html(symbol):
    """Return Unicode symbols (emojis) as HTML numeric entities."""
    html_numeric_entities = ""
    if not symbol.isascii():
        html_numeric_entities = "".join(['&#{:d};'.format(ord(item)) for item in symbol])
    return html_numeric_entities


def serialize_movie_to_html(imdb_id, movie_details):
    """Return movie details serialized as HTML."""
    # Get movie attributes
    movie_id = movie_details["movie_id"]
    title = movie_details["title"]
    image_url = movie_details["image_url"]
    imdb_url = IMDB_URL + imdb_id
    rating = movie_details["rating"]
    note = movie_details["note"]
    if image_url == "N/A":
        image_url = DUMMY_POSTER_URL
    year = movie_details["year"]
    # Create country emojis string as HTML numeric entities
    emojis_unicode = get_country_emojis_for_movie(movie_id)
    emojis_html = [convert_emoji_to_html(emoji) for emoji in emojis_unicode]
    emojis = "".join(emojis_html)
    # Begin serialization
    output = ''
    output += f'{indent(2)}<li>'
    output += f'\n{indent(3)}<div class="movie">'
    output += f'<a href="{imdb_url}" title="{note}" target="_blank">'
    output += f'\n{indent(4)}<img class="movie-poster" src="{image_url}"/>'
    output += '</a>'
    output += f'\n{indent(4)}<div class="movie-title">{title}</div>'
    output += f'\n{indent(4)}<div class="movie-year">{year}</div>'
    output += f'\n{indent(4)}<div class="rating">{rating}</div>'
    output += f'\n{indent(4)}<div class="rating">{emojis}</div>'
    output += f'\n{indent(3)}</div>'
    output += f'\n{indent(2)}</li>'
    return output


def serialize_all_movies_to_html(movies):
    """Return a user's movie ratings serialized as HTML."""
    output = ""
    for imdb_id, movie_details in movies.items():
        output += serialize_movie_to_html(imdb_id, movie_details) + "\n"
    return output


def render_webpage(user_id):
    """Generate webpage with all movies rated by the given user.

    Show the movies in reverse chronological order.
    """
    user = get_user(user_id, find_by_id=True)
    username = user["user_name"]
    page_title = f"{username}'s movie ratings"
    file_name = f"{username}.html"
    movies = get_movies(user_id)
    movies_sorted = dict(sorted(movies.items(),
                                key=lambda item: (item[1]["rating"], item[1]["year"]),
                                reverse=True))
    content = serialize_all_movies_to_html(movies_sorted)
    write_html_file(TEMPLATE_FILE_PATH, file_name, page_title, content)
    return True


def main():
    """Main function for testing when running the script under main."""


if __name__ == "__main__":
    main()
