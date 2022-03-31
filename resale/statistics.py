# Calculate statistics such as the monthly mean resale price from data.

def get_monthly_median_price(df, date_column = "year_month", price_column = "resale_price", groupby_column = None):
    """
    Get monthly median price for the entire dataset.
    Inputs
        df: DataFrame
        date_column: string
        price_column: string
        groupby_column: string (optional)
    Outputs
        median_price: DataFrame
    """
    if groupby_column is None:
        want = [date_column, price_column]
        groupby_column = [date_column]
    else:
        want = [date_column, price_column, groupby_column]
        groupby_column = [date_column, groupby_column]
        
    median_price = df[want].groupby(groupby_column).median().reset_index()
    median_price = median_price.sort_values(date_column)
    median_price["N"] = len(df)
    return median_price

def get_monthly_mean_price(df, date_column = "year_month", price_column = "resale_price", groupby_column = None):
    """
    Get monthly mean price for the entire dataset.
    Inputs
        df: DataFrame
        date_column: string
        price_column: string
        groupby_column: string (optional)
    Outputs
        mean_price: DataFrame
    """
    if groupby_column is None:
        want = [date_column, price_column]
        groupby_column = [date_column]
    else:
        want = [date_column, price_column, groupby_column]
        groupby_column = [date_column, groupby_column]
    
    mean_price = df[want].groupby(groupby_column).mean().reset_index()
    mean_price = mean_price.sort_values(date_column)
    return mean_price

