"""
Get Scryfall Data
=================
Use Scryfall's api to pull a json file containing card objects on Scryfall

File Types
----------
ORACLE
    A JSON file containing one Scryfall card object for each Oracle ID on Scryfall.
    The chosen sets for the cards are an attempt to return the most up-to-date 
    recognizable version of the card.
UNIQUE
    A JSON file of Scryfall card objects that together contain all unique artworks.
    The chosen cards promote the best image scans.
DEFAULT
    A JSON file containing every card object on Scryfall in English or the printed 
    language if the card is only available in one language.
ALL
    A JSON file containing every card object on Scryfall in every language.
RULINGS
    A JSON file containing all Rulings on Scryfall. Each ruling refers to cards via an `oracle_id`.

Reference https://scryfall.com/docs/api/bulk-data
"""

from enum import Enum
import requests


class BulkDataError(Exception):
    """Base class for exceptions related to bulk data."""

    def __init__(self, message: str):
        print(message)


class FetchDataError(BulkDataError):
    """Raised when fetching bulk data fails."""

    def __init__(self, status_code):
        super().__init__(f"Failed to fetch bulk data. Status code: {status_code}")


class DownloadError(BulkDataError):
    """Raised when downloading the file fails."""

    def __init__(self, status_code):
        super().__init__(f"Failed to download the file. Status code: {status_code}")


class DataTypeNotFoundError(BulkDataError):
    """Raised when the requested data type is not found."""

    def __init__(self, data_type):
        super().__init__(f"Data type '{data_type}' not found in bulk data.")


class BulkDataType(Enum):
    """
    Restrict the types of files that can be requested
    """

    ORACLE = "oracle_cards"
    UNIQUE = "unique_artwork"
    DEFAULT = "default_cards"
    ALL = "all_cards"
    RULINGS = "rulings"


def main(data_type: BulkDataType):
    """Pull the bulk data json file from Scryfall"""
    url = "https://api.scryfall.com/bulk-data"

    # Fetch bulk data info
    response = requests.get(url, timeout=60 * 5)
    if response.status_code != 200:
        raise FetchDataError(response.status_code)

    # Find the correct file type based on the param passed in
    data = response.json()
    file_url = None
    for bulk_data in data.get("data", []):
        if bulk_data["type"] == data_type.value:
            file_url = bulk_data["download_uri"]
            break
    if not file_url:
        raise DataTypeNotFoundError(data_type.value)

    # Pull the file itself
    file_response = requests.get(file_url, timeout=60 * 5)
    if file_response.status_code != 200:
        raise DownloadError(response.status_code)
    file_name = f"{data_type.value}_scryfall.json"
    with open(file_name, "wb") as file:
        file.write(file_response.content)
    print(f"File downloaded successfully as '{file_name}'")


if __name__ == "__main__":
    main(BulkDataType.DEFAULT)
