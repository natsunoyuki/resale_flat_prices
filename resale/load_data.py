# Load processed resale flat price data.

import os
import pandas as pd

# Fixed constants indicating the raw data stored on GitHub.
DATA_DIR = "https://github.com/natsunoyuki/resale-flat-prices/blob/main/processed%20data/"
DATA_FILE = "consolidated-resale-flat-prices.csv.zip"
SUFFIX = "?raw=true"

# Fixed constants for data on local disk.
CURR_PATH = os.path.dirname(__file__)
LOCAL_DATA_DIR = os.path.join(CURR_PATH, "../processed data/")

def load_data(online = True, data_dir = DATA_DIR, data_file = DATA_FILE, suffix = SUFFIX,
              local_data_dir = LOCAL_DATA_DIR):
    """
    Loads pre-processed data from GitHub or local disk.
    Inputs
        data_dir, data_file, suffix, local_data_dir: string
    Outputs
        data: DataFrame
    """
    if online == True:
        try:
            # Try to load from GitHub.
            print("Downloading data from GitHub...")
            data = pd.read_csv(data_dir + data_file + suffix, compression = "zip")
        except:
            # If not load from local disk.
            print("Error downloading data from GitHub!")
            data = load_local_data(LOCAL_DATA_DIR + DATA_FILE, "zip")
    else:
        data = load_local_data(LOCAL_DATA_DIR + DATA_FILE, "zip")
        
    print("Downloaded data shape: {}.".format(data.shape))
    
    # Extract the resale year, month.
    data["year"] = data["month"].apply(year_from_month)
    data["mth"] = data["month"].apply(mth_from_month)
    
    # Format the resale year and month to yyyymm integer format.
    data["year_month"] = pd.to_datetime(data["month"])
    return data

def from_year(df, year = 2015):
    """
    Use data from a specified year. Extremely old data is probably not useful.
    Inputs
        df: DataFrame
        year: int
    Outputs
        df: DataFrame
    """
    return df[df["year"] >= year]

def load_local_data(data_dir = LOCAL_DATA_DIR + DATA_FILE, compression = "zip"):
    """
    Loads the data locally from disk.
    Inputs
        data_dir, compression: string
    Outputs
        df: DataFrame
    """
    print("Loading data from disk...")
    return pd.read_csv(data_dir, compression = compression)

def month_formatter(x):
    # Converts 2017-01 to 201701 int format.
    return int(x[:4]) * 100 + int(x[5:])

def year_from_month(x):
    # Converts 2017-01 to 2017 int format.
    return int(x[:4])

def mth_from_month(x):
    # Converts 2017-01 to 1 int format.
    return int(x[5:])
