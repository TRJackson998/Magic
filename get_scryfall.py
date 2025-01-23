"""
Get Scryfall Data
=================
Use Scryfall's api to pull a json file containing every card object on Scryfall in English
"""

import requests

# Define the URL for the file you want to download
url = "https://api.scryfall.com/bulk-data"

# Make the GET request to the API
response = requests.get(url, timeout=60 * 5)

if response.status_code == 200:
    # Parse the JSON response to find the file's download URI
    data = response.json()
    for bulk_data in data.get("data", []):
        if bulk_data["type"] == "default_cards":  # Change this type based on what you need
            file_url = bulk_data["download_uri"]
            file_response = requests.get(file_url, timeout=60 * 5)
            if file_response.status_code == 200:
                # Save the file to your local directory
                with open("default_cards.json", "wb") as file:
                    file.write(file_response.content)
                print("File downloaded successfully as 'default_cards.json'")
            else:
                print(f"Failed to download the file. Status code: {file_response.status_code}")
            break
else:
    print(f"Failed to fetch bulk data. Status code: {response.status_code}")
