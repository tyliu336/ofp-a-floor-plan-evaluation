import numpy as np
from scipy.optimize import minimize

# 1. Setting up the data
# X is the matrix of aspect scores for 10 floor plans (10 rows, 5 columns:TD, EWR, SA, CAC,RG)
sample_ids = np.array([
    "1-3", "1-11", "1-21", "1-22", "1-34",
    "2-3", "2-9", "2-11", "2-27", "2-35"
])
X = np.array([
    [72, 18, 19, 6, 87], # Floor plan 1
    [16, 77, 81, 9, 100], # Floor plan 2
    [90, 62, 72, 60, 90], # Floor plan 3
    [0, 0, 44, 0, 67], # Floor plan 4
    [84, 100, 72, 10, 70], # Floor plan 5
    [0, 0, 94, 0, 87], # Floor plan 6
    [59, 92, 78, 13, 100], # Floor plan 7
    [66, 60, 88, 8, 85], # Floor plan 8
    [71, 97, 81, 45, 100], # Floor plan 9
    [54, 94, 66, 11, 0]  # Floor plan 10
])

# y is the vector of actual total scores given by real people for each floor plan
y = np.array([51.43, 48.11, 51.24, 49.15, 53.74, 37.67, 52.52, 48.56, 54.17, 53.51])

# Sample 2-27 was removed from the final fit because the image displayed in the
# survey did not match the image used for metric scoring.
keep_mask = sample_ids != "2-27"
X = X[keep_mask]
y = y[keep_mask]

# 2. Define the objective function: calculate the sum of squared errors
def objective_function(weights, X, y):
    # use the weights to calculate the predicted total scores for each floor plan
    predictions = np.dot(X, weights)
    # calculate the sum of squared errors between the predicted scores and the actual scores
    error = np.sum((y - predictions) ** 2)
    return error

# 3. Define the constraints and bounds for the optimisation problem
# Constraint 1: The sum of all weights equals 1 (i.e., sum(weights) - 1 = 0)
constraints = ({'type': 'eq', 'fun': lambda w: np.sum(w) - 1})

# Constraint 2: Each weight's value is between 0 and 1
bounds = tuple((0, 1) for _ in range(5))

# 4. set the initial guess for the weights (starting with equal weights for all aspects)
initial_weights = np.array([0.2, 0.2, 0.2, 0.2, 0.2])

# 5. Run the optimization using the SLSQP method
result = minimize(
    objective_function, 
    initial_weights, 
    args=(X, y), 
    method='SLSQP', 
    bounds=bounds, 
    constraints=constraints
)

# 6. print the results
if result.success:
    print("计算成功！找到的最优权重如下：")
    optimized_weights = result.x
    for i, weight in enumerate(optimized_weights):
        
        print(f"Aspect {i+1}: {weight*100:.2f}%")
else:
    print("Failed:", result.message)
