# OneMapSg

# OneMap geospatial data services provided by the Singapore government.
# https://www.onemap.gov.sg/docs/
# Requires an account and password to access.

# Usage Limits
# Please note that we have set a maximum of 250 calls per min.
# If you wish to increase your limit, contact onemap@sla.gov.sg

# Deprecations
# Please note that we have made a minor text fix, changing the word “LONGTITUDE” to “LONGITUDE”.
# We will be deprecating response field of “LONGTITUDE” for “LONGITUDE” in due course.
# This exercise will impact 3 API services (Search & Reverse-Geocoding).

import os
import json

try:
    from onemapsg import OneMapClient
except:
    print("onemapsg not found... Geocoding using OneMapClient will not run!")
    print("https://pypi.org/project/onemapsg/")

# Fixed constants indicating the location of the credentials.
CURR_PATH = os.path.dirname(__file__)
PATH = os.path.join(CURR_PATH, "../OneMap2-Authentication-Module_for_MacOS/authentication_module/")
FILE_NAME = "credentials.txt"

with open(PATH + FILE_NAME) as f:
    credentials = json.load(f)
    
USER_NAME = credentials["email"]
PASSWORD = credentials["password"]

def get_onemapclient(user_name = USER_NAME, password = PASSWORD):
    """
    Creates a OneMapSg Client.
    Inputs
        user_name, password: string
    Outputs
        Client: OneMapClient
    """
    try:
        Client = OneMapClient(user_name, password)
    except:
        print("OneMapClient not created successfully...")
        Client = None
        
    return Client
