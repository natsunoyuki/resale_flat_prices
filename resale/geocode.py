# Geocode the addresses to geographical coordinates.

import json
import geopy
import numpy as np
import os
import time

# Relative imports.
from . import load_data, clean_data, onemapclient

# Fixed constants indicating the location of the geocoded address json file.
CURR_PATH = os.path.dirname(__file__)
DIR = os.path.join(CURR_PATH, "../processed data/")
GEOCODED_ADDRESSES = "geocoded_addresses.json"

# Main function to create a json file of geocoded addresses in Singapore.
def geocode_address():
    # 1. Load raw data, and extract all unique addresses in the data.
    # We will only geocode the unique addresses in order to not waste resources.
    df = load_data.load_data()
    address = get_unique_address(df)
    print("Unique addresses loaded from data: {}.".format(len(address)))
    
    # 2. Load existing geocoded addresses. We will add to this pool of geocoded addresses.
    address_dict = load_geocoded_addresses_json(dir = DIR, json_file = GEOCODED_ADDRESSES)
    print("Geocoded addresses loaded from json: {}.".format(len(address_dict)))
    
    # 3. Find if there are any un-geocoded addresses in address not in the json file.
    to_do = find_missing_addresses(address, address_dict)
    print("Missing addresses: {}.".format(len(to_do)))
    
    # 4. Geocode the missing addresses, and update the current dictionary of geocoded addresses.
    if len(to_do) > 0:
        Client = onemapclient.get_onemapclient()
        address_dict, failures = onemap_geocode(to_do, address_dict, Client, 200)
    
    # 5. Save the updated dictionary to json.
    if len(to_do) > 0:
        store_geocoded_addresses_json(address_dict, GEOCODED_ADDRESSES)
    
    # 6. Handle failed geocoding - OneMap does not always work!
    
    return

def get_unique_address(df):
    """
    Get all unique addresses in the raw data DataFrame.
    Inputs
        df: DataFrame
    Outputs
        address: array
    """
    df = clean_data.clean_street_name(df)
    df = clean_data.make_address(df)
    return df["address"].unique()

def load_geocoded_addresses_json(dir = DIR, json_file = GEOCODED_ADDRESSES):
    """
    Load the json file containing the geocoded addresses.
    Inputs
        dir, json_file: string
    Outputs
        address_dict: dict
    """
    if json_file in os.listdir(dir):
        with open(dir + json_file) as fp:
            address_dict = json.load(fp)
        print("Geocoded addresses: {}.".format(len(address_dict)))
    else:
        address_dict = {}
    return address_dict
    
def store_geocoded_addresses_json(address_dict, dir = DIR, json_file = GEOCODED_ADDRESSES):
    """
    Store the geocoded addresses to a json file on disk.
    Inputs
        address_dict: dict
    """
    with open(dir + json_file, "w") as fp:
        json.dump(address_dict, fp)

def find_missing_addresses(address, address_dict):
    """
    Find addresses missing in the geocoded addresses from the json file.
    Inputs
        address_batch: list
        address_dict: dict
    Outputs
        to_do: list
    """
    to_do = []
    for k in address:
        if k not in address_dict.keys():
            to_do.append(k)

    to_do = sorted(to_do)
    print("Missing addresses: {}.".format(len(to_do)))
    return to_do
    
# Use OneMapSg to geocode addresses.
def onemap_geocode(address, address_dict, Client, batch_size = 200, verbose = False):
    """
    Geocode all addresses in a batch iteratively with OneMapSg.
    Inputs
        address_batch: list
        address_dict: dict
        Client: OneMapClient
    Outputs
        address_dict: dict
        failures: list
    """
    # As OneMapSg has a limit of 250 queries per minute, we use a batch_size in order
    # to limit our resource use.
    if batch_size > 250:
        batch_size = 250
       
    # Keep track of all failed geocodes.
    failures = []

    # Iterate through all batches, ensuring that each batch remains within usage limits.
    n_batches = int(np.ceil(len(address) / batch_size))
    for n in range(n_batches):
        start_time = time.time() # Start time of each batch.
        
        address_batch = address[n*batch_size:(n+1)*batch_size]
        address_dict, failures = _onemap_geocode(address_batch, address_dict, failures, Client, batch_size)
        
        # If the time elapsed per batch < 1 minute, wait until 1 minute has elapsed!
        end_time = time.time() # End time of each batch.
        time_elapsed = end_time - start_time # Time elapsed. 250 queries per 1 minute!
        if time_elapsed <= 60:
            time.sleep(60 - time_elapsed)
            
        if verbose == True:
            print("{}/{} batches complete. Time elapsed: {:.2f}s.".format(n+1, n_batches, time_elapsed))
    
    return address_dict, failures

def _onemap_geocode(address_batch, address_dict, failures, Client, batch_size = 200):
    """
    Geocode all addresses in a batch iteratively with OneMapSg.
    Inputs
        address_batch: list
        address_dict: dict
        failures: list
        Client: OneMapClient
    Outputs
        address_dict: dict
        failures: list
    """
    for i in range(len(address_batch)):
        results = Client.search(address_batch[i])
            
        # If the geocoding is successful, save the results. If not, track the failed geocodes!
        # In general, 
        if len(results["results"]) > 0:
            address_dict[address_batch[i]] = {}
            address_dict[address_batch[i]]["latitude"] = results["results"][0]["LATITUDE"]
            address_dict[address_batch[i]]["longitude"] = results["results"][0]["LONGITUDE"]
            address_dict[address_batch[i]]["address"] = results["results"][0]["ADDRESS"]
        else:
            failures.append(address_batch[i])
            
    return address_dict, failures

# Use GeoPy to geocode addresses.
def nominatim_geocode(address_to_geocode, address_dict, user_agent = "resale_flat_price_nominatim"):
    """
    Through GeoPy use Nominatim's free geocoder to geocode.
    Nominatim has a strict limit of 1 query per second!
    Inputs
        address_to_geocode: string
        address_dict: dict
    Outputs
        address_dict: dict
    """
    nominatim_geocoder = geopy.Nominatim(user_agent = user_agent)
    try:
        gcd = nominatim_geocoder.geocode(address_to_geocode)
    except:
        print("Nominatim geocoding not successful!")
        gcd = None
        
    if gcd is not None:
        address_dict[address_to_geocode] = {}
        address_dict[address_to_geocode]["latitude"] = gcd.latitude
        address_dict[address_to_geocode]["longitude"] = gcd.longitude
        address_dict[address_to_geocode]["address"] = gcd.address
        
    return address_dict
