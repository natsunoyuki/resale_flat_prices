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
RPI_FILE = os.path.join(CURR_PATH, "../processed data/resale_price_index.csv.zip")

# Columns to keep from the raw data.
COLS_TO_KEEP = ["month", "town", "flat_type", "block", "street_name", 
                "storey_range", "floor_area_sqm", "flat_model",
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
    
def process_raw_resale_price_index_data(base_path = BASE_PATH):
    """
    Process and quarterly resale price index into monthly values.
    The original resale price index is given quarterly. We increase the resolution
    of the data to make it monthly.
    """
    file_name = "housing-and-development-board-resale-price-index-1q2009-100-quarterly.csv"
    rpi = pd.read_csv(os.path.join(base_path, file_name))
    rpi["quarter"] = pd.to_datetime(rpi["quarter"])
    
    start_year = rpi["quarter"].min().year
    start_month = rpi["quarter"].min().month
    end_year = rpi["quarter"].max().year
    end_month = rpi["quarter"].max().month + 2
    dr = make_monthly_date_range(start_year, start_month, end_year, end_month)
    
    rpi = pd.merge(left = dr, right = rpi, 
                   left_on = "year_month", right_on = "quarter", 
                   how = "left")
    
    rpi = rpi.drop(["quarter"], axis = 1).fillna(method = "ffill")
    
    return rpi

def data_to_csv(data, out_file, compression = "zip"):
    """
    Output processed data to disk
    Inputs
        data: DataFrame
        out_file, compression: string
    """
    data.to_csv(out_file, index = False, compression = compression)
    
def make_monthly_date_range(start_year = 1990, start_month = 1, 
                            end_year = 2021, end_month = 7, 
                            include_final_month = True, 
                            column_name = "year_month"):
    dr = []
    
    while (start_year != end_year) or (start_month != end_month):
        next_date = pd.to_datetime("{}-{}-01".format(str(start_year), str(start_month).zfill(2)))
        dr.append(next_date)
        
        start_month = start_month + 1
        if start_month > 12:
            start_month = 1
            start_year = start_year + 1
    
    if include_final_month == True:
        next_date = pd.to_datetime("{}-{}-01".format(str(start_year), str(start_month).zfill(2)))
        dr.append(next_date)

    return pd.DataFrame(dr, columns = [column_name])
    
if __name__ == "__main__":
    print("Loading and processing raw resale price data .csv files...")
    data = process_raw_resale_flat_price_data(BASE_PATH, COLS_TO_KEEP)
    print("Final resale price data shape: {}.".format(data.shape))
    
    data_to_csv(data, OUT_FILE)
    print("Saved processed resale price data to {}.".format(OUT_FILE))
    
    print("Loading and processing raw resale price indices...")
    resale_price_index = process_raw_resale_price_index_data(BASE_PATH)
    
    data_to_csv(resale_price_index, RPI_FILE)
    print("Saved processed resale price index data to {}.".format(RPI_FILE))
