# Download raw data as zip files from: https://data.gov.sg/dataset/
# The downloaded raw data must be further processed before they can be
# used. The processing is performed in raw_data_process.py

import os
import requests
import zipfile

# Fixed constants for saving the downloaded raw data.
CURR_PATH = os.path.dirname(__file__)
SAVE_PATH = os.path.join(CURR_PATH, "../") # Relative file path.

# Urls to download from.
RESALE_FLAT_PRICES_URL = "https://data.gov.sg/dataset/7a339d20-3c57-4b11-a695-9348adfd7614/download"
HDB_PROPERTY_INFORMATION_URL = "https://data.gov.sg/dataset/9dd41b9c-b7d7-405b-88f8-61b9ca9ba224/download"
HDB_RESALE_PRICE_INDEX_URL = "https://data.gov.sg/dataset/ef430ec5-8f46-40cf-9fd9-f0257a954dc8/download"

# Directory to put raw data.
RAW_DATA_DIR = os.path.join(SAVE_PATH, "raw data/")

# .zip files to save to.
HDB_PROPERTY_INFORMATION_FILE_PATH = os.path.join(SAVE_PATH, "hdb-property-information.zip")
RESALE_FLAT_PRICES_FILE_PATH = os.path.join(SAVE_PATH, "resale-flat-prices.zip")
HDB_RESALE_PRICE_FILE_PATH = os.path.join(SAVE_PATH, "hdb-resale-price-index.zip")

def download_and_unzip(url, zip_file_path, raw_data_dir):
    """
    Download the original resale flat price data from https://data.gov.sg/dataset/resale-flat-prices
    Inputs
        url, zip_file_path, raw_data_dir: string
    """
    try:
        # Get response from URL.
        response = requests.get(url, allow_redirects = True)
        try:
            # Save response as a zip file locally.
            save_response_as_zip(response, zip_file_path)
            try:
                # Unzip the saved zip file.
                unzip(zip_file_path, raw_data_dir)
                # Delete the saved zip file after extracting its contents.
                os.remove(zip_file_path)
            except:
                print("Could not unzip the data to {}.".format(raw_data_dir))
        except:
            print("Could not save data to {}.".format(zip_file_path))
    except:
        print("Could not download data from {}.".format(url))
        
def save_response_as_zip(response, zip_file_path):
    """
    Save the request response as a zip file.
    Inputs
        response: Respose
        zip_file_path: string
    """
    with open(zip_file_path, "wb") as f:
        f.write(response.content)

def unzip(zip_file_path, unzip_file_path):
    """
    Unzip zip files.
    Inputs
        zip_file_path, unzip_file_path: string
    """
    with zipfile.ZipFile(zip_file_path, "r") as z:
        z.extractall(unzip_file_path)

if __name__ == "__main__":
    print("Downloading HDB resale flat price data from {}.".format(RESALE_FLAT_PRICES_URL))
    download_and_unzip(RESALE_FLAT_PRICES_URL, RESALE_FLAT_PRICES_FILE_PATH, RAW_DATA_DIR)
    
    print("Downloading HDB property information from {}.".format(HDB_PROPERTY_INFORMATION_URL))
    download_and_unzip(HDB_PROPERTY_INFORMATION_URL, HDB_PROPERTY_INFORMATION_FILE_PATH , RAW_DATA_DIR)

    print("Downloading HDB resale price index data from {}.".format(HDB_RESALE_PRICE_INDEX_URL))
    download_and_unzip(HDB_RESALE_PRICE_INDEX_URL, HDB_RESALE_PRICE_FILE_PATH , RAW_DATA_DIR)
