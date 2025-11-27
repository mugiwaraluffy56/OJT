import requests
import os

# The directory to save the license files
DATA_DIR = "data"

# A list of common SPDX license identifiers
# You can find more at https://spdx.org/licenses/
LICENSE_IDS = [
    "MIT",
    "Apache-2.0",
    "GPL-3.0-only",
    "GPL-2.0-only",
    "LGPL-3.0-only",
    "BSD-3-Clause",
    "BSD-2-Clause",
    "ISC",
    "MPL-2.0",
    "CC-BY-4.0",
]

def download_licenses():
    """
    Downloads the full text of the specified licenses from the SPDX GitHub repo.
    """
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    print("Starting download of license texts...")

    for license_id in LICENSE_IDS:
        url = f"https://raw.githubusercontent.com/spdx/license-list-data/master/text/{license_id}.txt"
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an exception for bad status codes

            filename = f"{license_id.lower()}.txt"
            filepath = os.path.join(DATA_DIR, filename)

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(response.text)
            
            print(f"Successfully downloaded and saved {license_id} to {filepath}")

        except requests.exceptions.RequestException as e:
            print(f"Error downloading {license_id}: {e}")

if __name__ == "__main__":
    download_licenses()
