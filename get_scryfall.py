"""
Get Scryfall Data
=================
Use Scryfall's api to pull a json file containing every card object on Scryfall in English
"""

from enum import Enum
import requests


# Define an Enum for the type options
class BulkDataType(Enum):
    ORACLE = "oracle_cards"
    DEFAULT = "default_cards"
    UNIQUE = "unique_artwork"
    ALL = "all_cards"
    RULINGS = "rulings"


def main(data_type: BulkDataType):
    url = "https://api.scryfall.com/bulk-data"

    # Fetch bulk data info
    response = requests.get(url, timeout=60 * 5)
    if response.status_code == 200:
        data = response.json()
        for bulk_data in data.get("data", []):
            if bulk_data["type"] == data_type.value:
                file_url = bulk_data["download_uri"]
                file_response = requests.get(file_url, timeout=60 * 5)
                if file_response.status_code == 200:
                    file_name = f"{data_type.value}.json"
                    with open(file_name, "wb") as file:
                        file.write(file_response.content)
                    print(f"File downloaded successfully as '{file_name}'")
                else:
                    print(f"Failed to download the file. Status code: {file_response.status_code}")
                return
        print(f"Data type '{data_type.value}' not found.")
    else:
        print(f"Failed to fetch bulk data. Status code: {response.status_code}")


if __name__ == "__main__":
    main(BulkDataType.DEFAULT)
