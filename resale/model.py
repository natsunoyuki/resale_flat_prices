# Use Abominable Intelligence to predict resale flat prices.

from lightgbm import LGBMRegressor
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
import time

from . import clean_data

# Fixed constants for the training features and target to use.
#FEATURES = ["lat", "lon", "flat_type_num", "storey_range_num", "age"]
FEATURES = ["latitude", "longitude", "flat_type_num", "storey_range_num", "age"]
TARGET = "price_per_sqm_adj"

# Functions to scale the target variable.
def y_scaler(x, base = 10):
    """
    Scale the resale price.
    """
    if base == 10:
        x = np.log10(x)
    elif base == np.exp(1) or base == "e":
        x = np.log(x)
    return x

def y_descaler(y, base = 10):
    """
    De-scale the scaled resale price.
    """
    if base == "e" or base == np.exp(1):
        y = np.exp(y)
    elif base == 10:
        y = 10 ** y
    return y

# Functions to create X and y.
def make_Xy(df, features = FEATURES, target = TARGET, scale_y = False, base = 10):
    """
    Inputs
        df: DataFrame
        features: list
        target: string
        scale_y: bool
        base: int
    Outputs
        X: array
        y: array
    """
    X = df[features]
    
    if scale_y == True:
        y = df[target].apply(y_scaler, args = (base,))
    else:
        y = df[target]
        
    return X.values, y.values

# Functions to train the model and perform grid search cross validation if needed.
def train_model(X, y,
                grid_search = False,
                grid_search_params = {"n_estimators" : [100, 200, 300, 400, 500]},
                model = None, model_params = None,
                random_state = None):
    """
    Train a machine learning model to predict resale flat prices.
    Optional choice of performing a grid search to find the best performing model.
    
    Inputs
    Outputs
    """
    # Split into train and test sets.
    X_train, X_test, y_train, y_test = train_test_split(X, y, random_state = random_state)
    
    if grid_search == True:
        grid_search = grid_search_cv(X_train, y_train, grid_search_params, 5, random_state, True)
        
        # Use the best_estimator_ as the prediction model.
        model = grid_search.best_estimator_
    else:
        if model is None:
            model = lightgbm.LGBMRegressor(**model_params)
        
    
    
    return

def grid_search_cv(X, y, grid_search_params = {"n_estimators" : [100, 200, 300, 400, 500]},
                   cv = 5, random_state = None, time = True):
    """
    Use cross validated grid search to search for the best model parameters.
    
    To-do: improve this function to make it more generalized.
    
    Inputs
        X: array
        y: array
        grid_search_params: dict
        cv: int
        random_state: int
        time: bool
    Outputs
        grid_search: GridSearchCV
    """
    model = LGBMRegressor(num_leaves = 2 ** 5, max_depth = 5, objective = "huber", random_state = random_state)
    grid_search = GridSearchCV(model, param_grid = grid_search_params, cv = cv)
    
    if time == True:
        start_time = time.time()
    
    grid_search.fit(X, y)
    
    if time == True:
        print("Time elapsed for grid search cv: {:.2f} s.".format(time.time() - start_time))
        
    return grid_search

# Functions to evaluate the model.
def evaluate_model(model, X_train, X_test, y_train, y_test, base = 10):
    y_train_pred = model.predict(X_train)
    y_test_pred = model.predict(X_test)
    
    train_mae = mean_absolute_error(y_descaler(y_train, base), y_descaler(y_train_pred, base))
    test_mae = mean_absolute_error(y_descaler(y_test, base), y_descaler(y_test_pred, base))
    print("Train mae : {}, test mae : {}.".format(int(train_mae), int(test_mae)))

    train_mse = np.sqrt(mean_squared_error(y_descaler(y_train, base), y_descaler(y_train_pred, base)))
    test_mse = np.sqrt(mean_squared_error(y_descaler(y_test, base), y_descaler(y_test_pred, base)))
    print("Train rmse: {}, test rmse: {}.".format(int(train_mse), int(test_mse)))

    train_r2 = r2_score(y_train, y_train_pred)
    test_r2 = r2_score(y_test, y_test_pred)
    print("Test R2   : {:.3f}, test R2  : {:.3f}.".format(train_r2, test_r2))
