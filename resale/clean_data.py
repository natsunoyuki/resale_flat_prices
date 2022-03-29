# Clean and perform feature engineering on the loaded resale price DataFrame.

from datetime import datetime
import numpy as np
import pandas as pd

# Relative imports.
from . import geocode

# Fixed constants.
CURRENT_YEAR = datetime.today().year

# Main cleaning function.
def clean_data(df):
    # Prepare the cleaned versions of the features. New columns are added to the DataFrame.
    
    # 1. Get "price_per_sqm" from "resale_price" and "floor_area_sqm".
    df = get_price_per_sqm(df)
    
    # 2. Categorize "town" numerically.
    df = clean_town(df)
    
    # 3. Clean up the abbreviations in "street_name".
    df = clean_street_name(df)
    
    # 4. Use "street_name" and "block" to make "address".
    df = make_address(df)
    
    # 5. Categorize "flat_type" numerically.
    df = clean_flat_type(df)
    
    # 6. Convert "storey_range" from string to numerical values.
    df = clean_storey_range(df)
    
    # 7. Categorize "flat_model" numerically.
    df = clean_flat_model(df)
    
    # 8. Normalize "floor_area_sqm".
    df = clean_floor_area_sqm(df)
    
    # 9. Get "age".
    df = get_age(df, CURRENT_YEAR)
    
    # 10. Obtain latitude and longitude, and normalize them.
    df = get_latitude_and_longitude(df)
    df = clean_latitude_and_longitude(df)
    return df
    
    
    
# Dependent functions for each feature are below.

# town
def town_cleaner(x):
    if x == "ANG MO KIO":
        x = 0
    elif x == "BEDOK":
        x = 1
    elif x == "BISHAN":
        x = 2
    elif x == "BUKIT BATOK":
        x = 3
    elif x == "BUKIT MERAH":
        x = 4
    elif x == "BUKIT PANJANG":
        x = 5
    elif x == "BUKIT TIMAH":
        x = 6
    elif x == "CENTRAL AREA":
        x = 7
    elif x == "CHOA CHU KANG":
        x = 8
    elif x == "CLEMENTI":
        x = 9
    elif x == "GEYLANG":
        x = 10
    elif x == "HOUGANG":
        x = 11
    elif x == "JURONG EAST":
        x = 12
    elif x == "JURONG WEST":
        x = 13
    elif x == "KALLANG/WHAMPOA":
        x = 14
    elif x == "LIM CHU KANG":
        x = 15
    elif x == "MARINE PARADE":
        x = 16
    elif x == "PASIR RIS":
        x = 17
    elif x == "PUNGGOL":
        x = 18
    elif x == "QUEENSTOWN":
        x = 19
    elif x == "SEMBAWANG":
        x = 20
    elif x == "SENGKANG":
        x = 21
    elif x == "SERANGOON":
        x = 22
    elif x == "TAMPINES":
        x = 23
    elif x == "TOA PAYOH":
        x = 24
    elif x == "WOODLANDS":
        x = 25
    elif x == "YISHUN":
        x = 26
    else:
        x = -999
    return x

def clean_town(df):
    df["town_cleaned"] = df["town"].apply(town_cleaner)
    return df

# street_name
def street_name_cleaner(x):
    """
    "street_name" is full of abbreviations which sometimes confuse geocoders.
    Replace those abbreviations with their proper forms.
    Inputs
        x: string
    Outputs
        x: string
    """
    if "NTH" in x and "NORTH" not in x:
        x = x.replace("NTH", "NORTH")
    if "STH" in x and "SOUTH" not in x:
        x = x.replace("STH", "SOUTH")
    if " DR" in x and "DRIVE" not in x:
        x = x.replace(" DR", " DRIVE")
    if " RD" in x and "ROAD" not in x:
        x = x.replace(" RD", " ROAD")
    if " ST" in x and "STREET" not in x:
        x = x.replace(" ST", " STREET")
    if " AVE" in x and "AVENUE" not in x:
        x = x.replace(" AVE", " AVENUE")
    if "CTRL" in x and "CENTRAL" not in x:
        x = x.replace("CTRL", "CENTRAL")
    if "CRES" in x and "CRESCENT" not in x:
        x = x.replace("CRES", "CRESCENT")
    if "PL " in x and "PLACE" not in x:
        x = x.replace("PL ", "PLACE ")
    if " PL" in x and "PLAINS" not in x and "PLAZA" not in x:
        x = x.replace(" PL", " PLACE")
    if "BT" in x and "BUKIT" not in x:
        x = x.replace("BT", "BUKIT")
    if "JLN" in x and "JALAN" not in x:
        x = x.replace("JLN", "JALAN")
    if "C'WEALTH" in x and "COMMONWEALTH" not in x:
        x = x.replace("C'WEALTH", "COMMONWEALTH")
    if " CL" in x and "CLOSE" not in x:
        x = x.replace("CL", "CLOSE")
    if "KG" in x and "KAMPONG" not in x:
        x = x.replace("KG", "KAMPONG")
    if "LOR " in x and "LORONG" not in x:
        x = x.replace("LOR ", "LORONG ")
    if "MKT" in x and "MARKET" not in x:
        x = x.replace("MKT", "MARKET")
    if "PK" in x and "PARK" not in x:
        x = x.replace("PK", "PARK")
    if "HTS" in x and "HEIGHTS" not in x:
        x = x.replace("HTS", "HEIGHTS")
    if "UPP " in x and "UPPER" not in x:
        x = x.replace("UPP", "UPPER")
    if "TG" in x and "TANJONG" not in x:
        x = x.replace("TG","TANJONG")
    if " TER" in x and "TERRACE" not in x:
        x = x.replace("TER","TERRACE")
    if "GDNS" in x and "GARDENS" not in x:
        x = x.replace("GDNS","GARDENS")
    if " CTR " in x and "CENTRE" not in x:
        x = x.replace(" CTR ", " CENTRE ")
    return x
    
def clean_street_name(df):
    """
    "street_name" is full of abbreviations which sometimes confuse geocoders.
    Replace those abbreviations with their proper forms.
    Inputs
        df: DataFrame
    Outputs
        df: DataFrame
    """
    df["street_name_cleaned"] = df["street_name"].apply(street_name_cleaner)
    return df

# address
def make_address(df):
    """
    "address" is formed from "block" and "street_name_cleaned".
    Inputs
        df: DataFrame
    Outputs
        df: DataFrame
    """
    df["address"] = df["block"] + " " + df["street_name_cleaned"]
    return df

# flat_type
def flat_type_formatter(x):
    if x == "1 ROOM":
        res = 1/7
    elif x == "2 ROOM":
        res = 2/7
    elif x == "3 ROOM":
        res = 3/7
    elif x == "4 ROOM":
        res = 4/7
    elif x == "5 ROOM":
        res = 5/7
    elif x == "EXECUTIVE":
        res = 6/7
    elif x == "MULTI-GENERATION" or x == "MULTI GENERATION":
        res = 7/7
    else:
        res = -999999 # Error value.
    return res

def clean_flat_type(df):
    """
    Inputs
        df: DataFrame
    Outputs
        df: DataFrame
    """
    df["flat_type_num"] = df["flat_type"].apply(flat_type_formatter)
    return df
    
# storey_range
def storey_range_formatter(x, max_storey = 50):
    lower_storey = int(x[:2])
    upper_storey = int(x[-2:])
    group = (lower_storey + upper_storey) / 2
    return group / max_storey

def clean_storey_range(df):
    df["storey_range_num"] = df["storey_range"].apply(storey_range_formatter)
    return df

# flat_model
def flat_model_formatter(x):
    return x

def clean_flat_model(df):
    df["flat_model"] = df["flat_model"].apply(lambda x: x.upper())
    return df

# floor_area_sqm
def sqm_to_sqft(x):
    # Convert square metres to square feet.
    return x * 10.7639
    
def sqft_to_sqm(x):
    # Convert square feet to square metres.
    return x / 10.7639

def floor_area_scaler(x, xmin, xmax):
    return (np.log10(x) - np.log10(xmin)) / (np.log10(xmax) - np.log10(xmin))

def clean_floor_area_sqm(df):
    min_floor_area = df["floor_area_sqm"].min()
    max_floor_area = df["floor_area_sqm"].max()
    df["floor_area_norm"] = df["floor_area_sqm"].apply(floor_area_scaler, args = (min_floor_area, max_floor_area))
    return df

def get_price_per_sqm(df):
    """
    Instead of determining the price per flat, it might be a better idea to determine the price
    per square metre.
    """
    df["price_per_sqm"] = df["resale_price"] / df["floor_area_sqm"]
    df["price_per_sqm"] = df["price_per_sqm"].astype(int)
    return df

# lease_commence_date
def age_scaler(x, xmin, xmax):
    return (x - xmin) / (xmax - xmin)

def get_age(df, current_year = CURRENT_YEAR):
    df["age"] = current_year - df["lease_commence_date"]
    return df

def clean_lease_commence_date(df, current_year = CURRENT_YEAR):
    df = get_age(df, current_year)

    # Scale the age to [0, 1]
    min_age = df["age"].min()
    max_age = df["age"].max()

    df["age"] = df["age"].apply(age_scaler, args = (min_age, max_age))
    return df

# latitude and longitude
def get_latitude_and_longitude(df):
    """
    Use pre-geocoded addresses in "processed data/geocoded_addresses.json"
    to obtain the latitudes and longitudes for each address.
    """
    address_dict = geocode.load_geocoded_addresses_json("processed data/")
    
    if "address" not in df:
        if "street_name_cleaned" not in df:
            df = clean_street_name(df)
        df = make_address(df)
        
    df["latitude"] = df["address"].apply(lambda x: float(address_dict[x]["latitude"]))
    df["longitude"] = df["address"].apply(lambda x: float(address_dict[x]["longitude"]))
    
    return df

def latlon_scaler(x, xmin, xmax):
    return (x - xmin) / (xmax - xmin)

def clean_latitude_and_longitude(df):
    max_latitude = df["latitude"].max()
    min_latitude = df["latitude"].min()
    max_longitude = df["longitude"].max()
    min_longitude = df["longitude"].min()

    df["lat"] = df["latitude"].apply(latlon_scaler, args = (min_latitude, max_latitude))
    df["lon"] = df["longitude"].apply(latlon_scaler, args = (min_longitude, max_longitude))
    return df
