import numpy as np
from scipy.optimize import linprog
from sklearn.metrics import r2_score

# Feature engineering functions.
def month_to_G(x, start_year = 2015):
    """
    Convert the date in "month" format to something which can be used in the linear inversion algorithm.
    """
    int_date = x.year * 100 + x.month
    year, month = np.divmod(int_date, 100)
    return (year - start_year) * 12 + month

def G_to_month(x, start_year = 2015):
    """
    Convert data from the linear inversion format back to the month format.
    """
    start_date = pd.to_datetime("{}-01-01".format(start_year))
    return start_date + pd.DateOffset(months = x - 1)

# Linear regression models.
def least_squares(G, d):
    """
    Linear least squares linear inversion.
    Inputs
        G: array
        d: array
    Outputs
        m: array
    """
    m = np.dot(np.linalg.inv(np.dot(G.T, G)), G.T)
    m = np.dot(m, d)
    return m

def l1_norm_inversion(G, d, sd = None):
    """
    Linear inversion using L1 norm error instead of mean squared error for
    over determined problems.
    The inversion problem is transformed into a linear programming problem
    and solved using the linprog() function from scipy.optimize.
    See Geophysical Data Analysis: Discrete Inverse Theory MATLAB Edition
    Third Edition by William Menke pages 153-157 for more details.
    
    Inputs
        G: np.array
        d: np.array
        sd: np.array
        
    Returns
        mest_l1: np.array
    """
    # If the std of the measurement d was not provided,
    # set it to 1.
    if sd is None:
        sd = np.ones(len(d))
    
    N, M = np.shape(G)
    L = 2 * M + 3 * N

    # 1. Create f containing the inverse data std:
    f = np.zeros(L)
    f[2*M:2*M+N] = 1 / sd

    # Make Aeq and beq for the equality constraints:
    Aeq = np.zeros([2*N, L])
    beq = np.zeros(2*N)
    
    Aeq[:N, :M] = G
    Aeq[:N, M:2*M] = -G
    Aeq[:N, 2*M:2*M+N] = -np.eye(N)
    Aeq[:N, 2*M+N:2*M+2*N] = np.eye(N)
    beq[:N] = d
    
    Aeq[N:2*N, :M] = G
    Aeq[N:2*N, M:2*M] = -G
    Aeq[N:2*N, 2*M:2*M+N] = np.eye(N)
    Aeq[N:2*N, 2*M+2*N:2*M+3*N] = -np.eye(N)
    beq[N:2*N] = d
    
    # Make A and b for the >=0 constraints:
    A = np.zeros([L+2*M, L])
    b = np.zeros(L+2*M)
    A[:L, :] = -np.eye(L)
    b[:L] = np.zeros(L)
    
    A[L:L+2*M] = np.eye(2*M, L)
    # For this example, we use the least squares solution
    # as the upper bound for the model parameters.
    mls = least_squares(G, d)
    mupperbound = 10 * np.max(np.abs(mls))
    b[L:L+2*M] = mupperbound
    
    res = linprog(f, A, b, Aeq, beq)
    
    # The output res = [m1, m2, alpha, x1, x2]. Extract m1 and m2
    # and calculate the model parameters using m = m1 - m2.
    mest_l1 = res['x'][:M] - res['x'][M:2*M]
    return mest_l1

# Metrics
def r2(d, G, m):
    return r2_score(d, np.dot(G, m))
