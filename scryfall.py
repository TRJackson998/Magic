"""
Scryfall
=================
Use Scryfall's api to pull a json file containing card objects on Scryfall
and populate a database table with the data

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

import datetime
from enum import Enum
from pathlib import Path

import pandas as pd
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


def get_data(data_type: BulkDataType) -> str:
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
    file_name = f"{datetime.date.today():%Y%m%d}_{data_type.value}_scryfall.json"
    with open(file_name, "wb") as file:
        file.write(file_response.content)
    print(f"File downloaded successfully as '{file_name}'")

    return file_name


def flatten_list(color_list: list) -> str:
    """
    The 'color' row comes in as lists of lists
    In order to aggregate the df by name, flatten the 2d list
    and move the data to a string

    [['R', 'G', 'B'], ['R', 'G', 'B'], ['R', 'G', 'B']] -> "R, G, B"
    """
    if (isinstance(color_list, list) and not color_list) or (
        not isinstance(color_list, list) and pd.isna(color_list)
    ):  # empty list or pandas null
        return ""

    color_list = [
        str(element) for innerList in color_list for element in innerList if pd.notna(element)
    ]
    color_list = set(color_list)  # remove duplicates
    color_list = ", ".join(color_list)

    return color_list


def read_data(json: str) -> pd.DataFrame:
    """Read the json and then clean it up and make it usable"""
    df = pd.read_json(json)
    keep_cols = ["name", "set_name", "rarity", "colors", "cmc", "type_line"]
    df = df[keep_cols]
    df["colors"] = df["colors"].apply(flatten_list)
    df["cmc"] = df["cmc"].apply(lambda x: int(x) if pd.notna(x) else pd.NA)  # float -> int
    df = df.groupby("name").agg(set).reset_index()

    return df


def main(file: Path = None):
    """Driver function"""
    if not file or not file.exists():
        file = get_data(BulkDataType.DEFAULT)
    df = read_data(file)


if __name__ == "__main__":
    main(
        Path(__file__).parent.joinpath(
            f"{datetime.date.today():%Y%m%d}_default_cards_scryfall.json"
        )
    )
