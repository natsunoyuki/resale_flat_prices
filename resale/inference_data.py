# Make data for inference.

import numpy as np

from . import clean_data
from . import geocode
from . import model

# Fixed constants.
ADDRESS_DICT = geocode.load_geocoded_addresses_json()

# Functions to prepare inputs for inference.
def make_inference_data(address = None, latitude = None, longitude = None, flat_type = None, storey_range = None, age = None):
    if address is not None:
        latitude, longitude = address_to_latlon(address, ADDRESS_DICT)
    flat_type = clean_data.flat_type_formatter(flat_type)
    storey_range = clean_data.storey_range_formatter(storey_range)
    
    # If required convert from string to float.
    latitude = float(latitude)
    longitude = float(longitude)
    flat_type = float(flat_type)
    storey_range = float(storey_range)
    age = float(age)
    
    return np.array([[latitude, longitude, flat_type, storey_range, age]])
    
def address_to_latlon(address, address_dict = ADDRESS_DICT):
    """
    Using the pre-geocoded addresses stored in the json file, get the latitude and longitude
    of an address.
    Inputs
        address: string
    Outputs
        latitude, longitude
    """
    latlon = address_dict.get(address, None)
    
    return latlon["latitude"], latlon["longitude"]

