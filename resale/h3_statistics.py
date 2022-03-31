# h3-py: Uber’s H3 Hexagonal Hierarchical Geospatial Indexing System in Python
# https://uber.github.io/h3-py/intro.html

import h3
import pandas as pd

def get_all_k_ring_monthly_median_price(df, date_column = "year_month", price_column = "resale_price",
                                        k_ring_distance = 1, h3_column_name = "h3"):
    """
    Gets the k-ring median price for all unique H3 indices in the DataFrame.
    Inputs
        df: DataFrame
        date_column: string (optional)
        price_column: string (optional)
        k_ring_distance: int (optional)
        h3_column_name: string (optional)
    Outputs
        median_price: DataFrame
    """
    h3_indices = df[h3_column_name].unique() # Get all unique H3 cell indices in df.
    h3_median_prices = []
    
    for i in range(len(h3_indices)):
        h3_median_price = get_k_ring_monthly_median_price(df, h3_indices[i], date_column, price_column,
                                                          k_ring_distance, h3_column_name)
        h3_median_price[h3_column_name] = h3_indices[i]
        h3_median_prices.append(h3_median_price)
        
    # This is the fast way of DataFrame concatenation.
    return pd.concat(h3_median_prices, ignore_index = True) 

def get_k_ring_monthly_median_price(df, h3_index, date_column = "year_month", price_column = "resale_price",
                                    k_ring_distance = 1, h3_column_name = "h3"):
    """
    Certain cells have very few (~2) rows of data. Instead of calculating the median for a single cell,
    calculate the median for a k-ring of 7 cells instead!
    Inputs
        df: DataFrame
        h3_index: string
        date_column: string (optional)
        price_column: string (optional)
        k_ring_distance: int (optional)
        h3_column_name: string (optional)
    Outputs
        median_price: DataFrame
    """
    # 1. Get the k_ring of cells within k_ring_distance around the cell of interest.
    k_ring_indices = sorted(list(h3.k_ring(h3_index, k = k_ring_distance)))
    
    # 2. Get all rows of data with H3 index in the list of k_ring cells obtained above.
    df = df[df[h3_column_name].isin(k_ring_indices)][[date_column, price_column]]
    
    # 3. Obtain the median price of all those rows of data.
    median_price = df.groupby([date_column]).median().reset_index()
    median_price = median_price.sort_values(date_column)
    median_price["N"] = len(df)
    return median_price



# The following H3 k_ring smoothing functions are taken from:
# https://github.com/uber/h3-py-notebooks/blob/master/notebooks/unified_data_layers.ipynb
def kring_smoothing(df, hex_col, metric_col, k):
    dfk = df[[hex_col]]
    dfk.index = dfk[hex_col]
    dfs =  (dfk[hex_col].apply(lambda x: pd.Series(list(h3.k_ring(x, k)))).stack()
                        .to_frame('hexk').reset_index(1, drop = True).reset_index()
                        .merge(df[[hex_col,metric_col]]).fillna(0)
                        .groupby(['hexk'])[[metric_col]].sum().divide((1 + 3 * k * (k + 1)))
                        .reset_index()
                        .rename(index = str, columns = {"hexk": hex_col}))
    dfs['lat'] = dfs[hex_col].apply(lambda x: h3.h3_to_geo(x)[0])
    dfs['lng'] = dfs[hex_col].apply(lambda x: h3.h3_to_geo(x)[1])
    return dfs

def weighted_kring_smoothing(df, hex_col, metric_col, coef):
    # normalize the coef
    a = []
    for k, coe in enumerate(coef):
        if k == 0:
            a.append(coe)
        else:
            a.append(k * 6 * coe)
    coef = [c / sum(a) for c in coef]
    
    # weighted smoothing
    df_agg = df[[hex_col]]
    df_agg['hexk'] = df_agg[hex_col]
    df_agg.set_index(hex_col,inplace=True)
    temp2 = [df_agg['hexk'].reset_index()]
    temp2[-1]['k'] = 0
    K=len(coef)-1
    for k in range(1,K+1):
        temp2.append((df_agg['hexk']
                     .apply(lambda x: pd.Series(list(h3.hex_ring(x,k)))).stack()
                     .to_frame('hexk').reset_index(1, drop=True).reset_index()
                ))
        temp2[-1]['k'] = k
    df_all = pd.concat(temp2).merge(df)
    df_all[metric_col] = df_all[metric_col]*df_all.k.apply(lambda x:coef[x])
    dfs = df_all.groupby('hexk')[[metric_col]].sum().reset_index().rename(index=str, columns={"hexk": hex_col})
    dfs['lat'] = dfs[hex_col].apply(lambda x: h3.h3_to_geo(x)[0])
    dfs['lng'] = dfs[hex_col].apply(lambda x: h3.h3_to_geo(x)[1])
    return dfs
