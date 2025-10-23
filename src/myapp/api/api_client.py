"""Provide API connection(s) and fetch data from online services."""
import requests
from dotenv import dotenv_values
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
# OMDB
DOTENV_FILE_PATH = (PROJECT_ROOT / ".env").resolve()
OMDB_API_KEY = dotenv_values(DOTENV_FILE_PATH).get("OMDB_API_KEY", None)
OMDB_BASE_URL = "http://www.omdbapi.com/"

TIMEOUT = 4


def retrieve_data_from_api(base_url,
                           endpoint="",
                           headers=None,
                           payload=None) -> requests.Response | None:
    """Return response from REST API for given endpoint and payload."""
    url = base_url + endpoint
    return requests.get(url, headers=headers, params=payload, timeout=TIMEOUT)


def fetch_omdb_api(payload):
    """Fetch data from the OMDB API."""
    payload["apikey"] = OMDB_API_KEY
    return retrieve_data_from_api(OMDB_BASE_URL, payload=payload)


def fetch_api_ninjas(payload, endpoint):
    """Fetch data from the API Ninjas."""
    payload["apikey"] = AN_API_KEY
    url = AN_BASE_URL + endpoint
    return retrieve_data_from_api(url, payload=payload, headers=AN_HEADERS)


def find_movies(search_string):
    """Return a list of movie objects for the given search string."""
    payload = {"s": search_string.lower()}
    response = fetch_omdb_api(payload)
    if response:
        return response.json().get("Search", [])
    return []


def fetch_movie_details(imdbID):
    """Return a movie object for the given imdbID."""
    payload = {"i": imdbID}
    response = fetch_omdb_api(payload)
    if response:
        return response.json()
    return False


# It seems that the flag emoji looks much nicer than the svg
# for display in a future html web page.
def get_country_flag_url(country_code):
    """Return the country flag url for the given country code."""
    endpoint = "countryflag"
    payload = {"country": country_code}
    response = fetch_api_ninjas(payload, endpoint=endpoint)
    if response:
        return response.json()["rectangle_image_url"]
    return False


def main():
    """Main function for testing when running the script under main."""
    pass


if __name__ == "__main__":
    main()
