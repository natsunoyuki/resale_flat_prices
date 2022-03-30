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

def adjust_resale_price_per_town(df, median_prices = None, 
                                 price_column = "resale_price", 
                                 end_year = None,
                                 vander_order = 4,
                                 model = "least_squares", 
                                 which = "town"):
    """
    Adjust the resale price per town to account for temporal changes.
    This is to ensure that all historical data are "updated" to the 
    latest prices.
    Inputs
        df: DataFrame
        median_prices: DataFrame
        price_column: string
        end_year: int or string (optional)
        vander_order: int (optinal)
        model: string (optional)
        which: string (optional)
    Outputs
        new_df: DataFrame
        temporal_models: dict
    """
    temporal_models = {}
    
    if median_prices is None and which == "town":
        # Get median prices aggregated by "town".
        median_prices = statistics.get_monthly_median_price(df, 
                                                            "year_month", 
                                                            price_column, 
                                                            which)
    elif median_prices is None and which == "h3":
        # Or get the median prices aggregated by "h3".
        median_prices = h3_statistics.get_all_k_ring_monthly_median_price(df = df, 
                                                                          date_column = "year_month",
                                                                          price_column = price_column,
                                                                          k_ring_distance = 1,
                                                                          h3_column_name = which)
    
    start_year = df["year"].min()
    
    # Build a different linear regression model to update the historical prices 
    # for each location.
    for location in sorted(df[which].unique()):
        d, G, m = build_price_adjustment_models(median_prices = median_prices, 
                                                price_column = price_column,
                                                location = location, 
                                                start_year = start_year, 
                                                which = which,
                                                vander_order = vander_order, 
                                                model = model)
        
        temporal_models[location] = {}
        temporal_models[location]["model"] = m.copy()
        temporal_models[location]["G"] = G.copy()
        temporal_models[location]["d"] = d.copy()
        temporal_models[location]["r2"] = linear_regression.r2(d[price_column].values, G, m)
        
    # For each monthly resale price, calculate the required adjustment factor.
    new_df = []
    for location in sorted(temporal_models.keys()):
        tmp_df = add_price_adjustment_factor(df = df, 
                                             temporal_models = temporal_models, 
                                             location = location,
                                             start_year = start_year, 
                                             end_year = None,
                                             vander_order = vander_order, 
                                             which = which)
        new_df.append(tmp_df)
        
    new_df = pd.concat(new_df, ignore_index = True)
    
    # Use the adjustment factor to calculate the adjusted resale price.
    new_df["{}_adj".format(price_column)] = new_df[price_column] * new_df["adj_factor"]
    new_df["{}_adj".format(price_column)] = new_df["{}_adj".format(price_column)].astype(int)

    return new_df, temporal_models

# Price adjustment based on the median resale price.
def build_price_adjustment_models(median_prices, price_column, location, start_year, end_year = None,
                                  which = "town", vander_order = 4, model = "least_squares"):
    """
    Inputs
        median_prices: DataFrame
        price_column: string
        location: string
        start_year: int
        end_year: int or string (optional)
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
    
    d = median_prices[median_prices[which] == location]
        
    # Create linearly increasing months from "year_month".
    d = d.assign(months = d["year_month"].apply(linear_regression.month_to_G, 
                                                args = (start_year,)))

    # From empirical studies, a 4th order Vander matrix appears to provide the 
    # best inversion kernel. Note that a 4th order Vander matrix results in a 
    # 3rd order polynomial in the linear regression model.
    # We model the change in the resale price with respect to months.
    G = np.vander(d["months"].values, vander_order)
    m = adjustment_model(G, d[price_column].values)
    return d, G, m
   
def add_price_adjustment_factor(df, temporal_models, location, start_year, end_year = None,
                                vander_order = 4, which = "town"):
    """
    Adds a price adjustment factor column to df. The adjust resale price will 
    be the product between the original resale price and this factor.
    Inputs
        df: DataFrame
        temporal_models: dict
        location: string
        start_year: int
        end_year: int or string (optional)
        vander_order: int (optional)
        which: string (optional)
    Outputs
        tmp_df: DataFrame
    """
    tmp_df = df[df[which] == location]
    tmp_df = tmp_df.assign(adj_months = tmp_df["year_month"].apply(linear_regression.month_to_G, 
                                                                   args = (start_year,)))

    # start_index is the predictions for the original resale price. This is 
    # an array of time series values.
    start_index = np.dot(np.vander(tmp_df["adj_months"].values, vander_order), 
                         temporal_models[location]["model"])
    
    if end_year is None:
        max_month_value = temporal_models[location]["d"]["months"].max()
    elif end_year == "next month":
        max_month_value = temporal_models[location]["d"]["months"].max() + 1
    
    # end_index is the predictions for the max month resale price. This is a 
    # single value!
    end_index = np.dot(np.vander([max_month_value], vander_order), 
                       temporal_models[location]["model"])
    
    tmp_df["adj_factor"] = end_index / start_index
    
    return tmp_df
