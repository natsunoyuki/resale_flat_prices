# Not all towns are created equal. Some towns have seen an appreciation in 
# prices, while others have not.
# Some towns have stable prices, while others have fluctuating prices.

# We should account for the temporal drift in the resale prices. Perhaps one 
# way to do this is to fit a simple regression model to model the increase in 
# the median value of resale_price against time.

# We break down the data according to their town values. For each town, we 
# train a 4th order least squares linear regression model to model the temporal
# shift in the median value of resale_price. For now we skip splitting the data 
# into train and test datasets due to the lack of data, although this should 
# not be a problem due to the low order of the polynomials involved, and the 
# relative smoothness in the changes in resale_price.

import numpy as np
import pandas as pd

# Relative imports.
from . import statistics
from . import h3_statistics
from . import linear_regression

def adjust_resale_price_by_location(df, 
                                    median_prices = None, 
                                    price_column = "resale_price", 
                                    start_year_month = None,
                                    next_month = False,
                                    vander_order = 4,
                                    model = "least_squares", 
                                    which = "town",
                                    kwargs = {}):
    """
    Adjust the resale price per town to account for temporal changes.
    This is to ensure that all historical data are "updated" to the 
    latest prices.
    Inputs
        df: DataFrame
        median_prices: DataFrame
        price_column: string
        start_year_month: datetime (optional)
        next_month: bool (optional)
        vander_order: int (optinal)
        model: string (optional)
        which: string (optional)
        kwargs: dict (optional)
    Outputs
        new_df: DataFrame
        temporal_models: dict
    """
    temporal_models = {}
    
    # If median_prices is not provided, perform the require computations.
    if median_prices is None and which == "town":
        # Get median prices aggregated by "town".
        median_prices = statistics.get_monthly_median_price(df, 
                                                            "year_month", 
                                                            price_column, 
                                                            which)
    elif median_prices is None and which == "h3":
        # Or get the median prices aggregated by "h3".
        k = kwargs.get("k_ring_distance", 1)
        median_prices = h3_statistics.get_all_k_ring_monthly_median_price(df, 
                                                                          "year_month",
                                                                          price_column,
                                                                          k_ring_distance = k,
                                                                          h3_column_name = which)
    
    # Obtain the start year in the DataFrame. This is an int e.g. 2015.
    #start_year = df["year"].min()
    
    # This on the other hand is a datetime object.
    if start_year_month is None:
        start_year_month = df["year_month"].min()
        
    if next_month == True:
        # Next month.
        end_year_month = df["year_month"].max() + pd.DateOffset(months = 1)
    else:
        # Current month.
        end_year_month = df["year_month"].max()
    
    # Build a different linear regression model to update the historical prices 
    # for each location.
    for location in sorted(df[which].unique()):
        d, G, m = build_price_adjustment_model(median_prices = median_prices, 
                                               price_column = price_column,
                                               location = location, 
                                               start_year_month = start_year_month, 
                                               which = which,
                                               vander_order = vander_order, 
                                               model = model)
        
        temporal_models[location] = {}
        temporal_models[location]["model"] = m.copy()
        temporal_models[location]["G"] = G.copy()
        temporal_models[location]["d"] = d.copy()
        temporal_models[location]["r2"] = linear_regression.r2(d[price_column].values, G, m)
        temporal_models[location]["N"] = len(median_prices[median_prices[which] == location]) 
        
    # For each monthly resale price, calculate the required adjustment factor.
    new_df = []
    for location in sorted(temporal_models.keys()):
        tmp_df = add_price_adjustment_factor(df = df, 
                                             temporal_models = temporal_models, 
                                             location = location,
                                             start_year_month = start_year_month, 
                                             end_year_month = end_year_month,
                                             vander_order = vander_order, 
                                             which = which)
        new_df.append(tmp_df)
        
    # This is the more efficient method of concatenating DataFrames...    
    new_df = pd.concat(new_df, ignore_index = True)
    
    # Use the adjustment factor to calculate the adjusted resale price.
    new_df["{}_adj".format(price_column)] = new_df[price_column] * new_df["adj_factor"]
    new_df["{}_adj".format(price_column)] = new_df["{}_adj".format(price_column)].astype(int)

    return new_df, temporal_models

def adjust_resale_price(df, 
                        median_prices = None, 
                        price_column = "resale_price", 
                        start_year_month = None,
                        next_month = False,
                        vander_order = 4,
                        model = "least_squares"):
    """
    Adjust the resale price per town to account for temporal changes.
    This is to ensure that all historical data are "updated" to the 
    latest prices.
    Inputs
        df: DataFrame
        median_prices: DataFrame
        price_column: string
        start_year_month: datetime (optional)
        next_month: bool (optional)
        vander_order: int (optinal)
        model: string (optional)
    Outputs
        new_df: DataFrame
        temporal_models: dict
    """
    
    # If median_prices is not provided, perform the require computations.
    if median_prices is None:
        # Get median prices without any aggregation.
        median_prices = statistics.get_monthly_median_price(df, "year_month", price_column)
    
    # Obtain the start year in the DataFrame. This is an int e.g. 2015.
    #start_year = df["year"].min()
    
    # This on the other hand is a datetime object.
    if start_year_month is None:
        start_year_month = df["year_month"].min()
        
    if next_month == True:
        # Next month.
        end_year_month = df["year_month"].max() + pd.DateOffset(months = 1)
    else:
        # Current month.
        end_year_month = df["year_month"].max()
    
    d, G, m = build_price_adjustment_model(median_prices, price_column, location = None, 
                                           start_year_month = start_year_month,
                                           which = None, vander_order = vander_order, 
                                           model = model)
    
    temporal_models = {}
    temporal_models["d"] = d.copy()
    temporal_models["G"] = G.copy()
    temporal_models["model"] = m.copy()
    
    tmp_df = add_price_adjustment_factor(df, temporal_models = None, location = None, 
                                         start_year_month = start_year_month, 
                                         end_year_month = end_year_month, 
                                         vander_order = vander_order, which = None)
    
    return tmp_df, temporal_models

# Price adjustment based on the median resale price.
def build_price_adjustment_model(median_prices, price_column, location, start_year_month, 
                                  which = "town", vander_order = 4, model = "least_squares"):
    """
    Inputs
        median_prices: DataFrame
        price_column: string
        location: string
        start_year_month: datetime
        which: string (optional)
        vander_order: int (optional)
        model: string (optional)
    Outputs
        d: array
        G: array
        m: array
    """
    ADJUSTMENT_MODELS = {"least_squares": linear_regression.least_squares,
                         "l1_norm_inversion": linear_regression.l1_norm_inversion}
                         
    adjustment_model = ADJUSTMENT_MODELS.get(model, linear_regression.least_squares)
    
    if which is None:
        # No location in data.
        d = median_prices.copy()
    else:
        # Extract the data for a particular location.
        d = median_prices[median_prices[which] == location]
        
    # Create linearly increasing months using "year_month", calculated from
    # the start date. Note that "year_month" is a datetime object.
    d = d.assign(months = d["year_month"].apply(linear_regression.month_to_G, 
                                                args = (start_year_month,)))

    # From empirical studies, a 4th order Vander matrix appears to provide the 
    # best inversion kernel. Note that a 4th order Vander matrix results in a 
    # 3rd order polynomial in the linear regression model.
    # We model the change in the resale price with respect to months.
    G = np.vander(d["months"].values, vander_order)
    m = adjustment_model(G, d[price_column].values)
    return d, G, m
   
def add_price_adjustment_factor(df, 
                                temporal_models, 
                                location, 
                                start_year_month, 
                                end_year_month,
                                vander_order = 4, 
                                which = "town"):
    """
    Adds a price adjustment factor column to df. The adjust resale price will 
    be the product between the original resale price and this factor.
    Inputs
        df: DataFrame
        temporal_models: dict
        location: string
        start_year_month: datetime
        end_year_month: datetime 
        vander_order: int (optional)
        which: string (optional)
    Outputs
        tmp_df: DataFrame
    """
    # Extract for a particular location.
    if which is None:
        tmp_df = df.copy()
        model = temporal_models["model"]
    else:
        tmp_df = df[df[which] == location]
        model = temporal_models[location]["model"]
    
    # Calculate the number of months from the start date to the sales date.
    months_from_start = tmp_df["year_month"].apply(linear_regression.month_to_G, 
                                                   args = (start_year_month,))
    
    # Less buggy way of adding a column of values to a DataFrame:
    tmp_df = tmp_df.assign(adj_months = months_from_start)
    
    # start_index is the predictions for the original resale price. This is 
    # an array of time series values.
    start_index = np.dot(np.vander(tmp_df["adj_months"].values, vander_order), model)
    
    target_month = linear_regression.month_to_G(end_year_month, start_year_month)
    
    #tmp_df["target_month"] = end_year_month
    tmp_df["target_month"] = target_month
    
    # end_index is the predictions of the resale price for the targeted month.
    # This targeted month is either the current month or the next month.
    end_index = np.dot(np.vander([target_month], vander_order), model)
    
    # By taking the ratio between the end_index and the start_index, we can
    # get an adjustment factor to be multiplied to the individual resale prices
    # to correct for the changes in time.
    tmp_df["adj_factor"] = end_index / start_index
    
    return tmp_df
