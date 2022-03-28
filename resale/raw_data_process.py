# Raw data originally downloaded from: https://data.gov.sg/dataset/
# The raw data can be downloaded using raw_data_dowload.py
# The raw data comes in several csv files. Combine those csv files into
# a single consolidated csv.zip file.

# By default, the consolidated zip file is stored under the path:
# "processed data/consolidated-resale-flat-prices.csv.zip",
# and the raw data under the path: "raw data/".

import os
import pandas as pd

# Fixed constants for processing the raw data.
CURR_PATH = os.path.dirname(__file__)
BASE_PATH = os.path.join(CURR_PATH, "../raw data/") # Relative file path.

# Fixed constants for saving the processed data.
OUT_FILE = os.path.join(CURR_PATH, "../processed data/consolidated-resale-flat-prices.csv.zip")

# Columns to keep from the raw data.
COLS_TO_KEEP = ["month", "town", "flat_type", "block", "street_name", "storey_range", "floor_area_sqm", "flat_model",
                "lease_commence_date", "resale_price"]

def process_raw_resale_flat_price_data(base_path = BASE_PATH, cols_to_keep = COLS_TO_KEEP):
    """
    Load and process the resale flat price raw data downloaded from
    https://data.gov.sg/dataset/resale-flat-prices into a single DataFrame.
    Inputs
        base_path: string
        cols_to_keep: list
    Outputs
        data: DataFrame
    """
    Data = []
    cols = []
    
    # Load resale price raw data scattered across several .csv files.
    # Those files all start with "resale-flat-prices" and end with "csv".
    for f in os.listdir(base_path):
        if f[:18] == "resale-flat-prices" and f[-3:] == "csv":
            print(f)
            path = base_path + f
            data = pd.read_csv(path)
            print("Loaded data shape: {}.".format(data.shape))
            #print("Loaded data columns: {}.".format(data.columns))
            Data.append(data)
            cols.append(data.columns)

    # Merge the resale flat price data into a single DataFrame.
    data = pd.DataFrame()
    for dat in Data:
        dat = dat[cols_to_keep]
        data = pd.concat([data, dat], axis = 0)
    
    return data
    
def data_to_csv(data, out_file = OUT_FILE, compression = "zip"):
    """
    Output processed data to disk
    Inputs
        data: DataFrame
        out_file, compression: string
    """
    data.to_csv(out_file, index = False, compression = compression)
    
if __name__ == "__main__":
    print("Loading and processing raw data .csv files...")
    data = process_raw_resale_flat_price_data(BASE_PATH, COLS_TO_KEEP)
    print("Final merged shape: {}.".format(data.shape))
    
    data_to_csv(data, OUT_FILE)
    print("Saved processed data to {}.".format(OUT_FILE))
