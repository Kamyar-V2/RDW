from GPyOpt.methods import BayesianOptimization
import GPy
from platypus import Problem, Real, NSGAII, Solution

# Define your problem as a class inheriting from Problem
class MyOptimizationProblem(Problem):
    def __init__(self):
        # Initialize the problem with 4 decision variables and 2 objectives
        super(MyOptimizationProblem, self).__init__(4, 2)
        self.types[:] = [Real(0.1, 3.0), Real(1.0, 6.0), Real(0.01, 0.4), Real(0.01, 0.5)]

        self.directions[:] = [Problem.MINIMIZE, Problem.MINIMIZE]  # Assuming both objectives are to be minimized

    def evaluate(self, solution):
        #min_sigma, max_sigma, threshold, overlap = solution.variables
        min_sigma, max_sigma, threshold, overlap = solution.variables

        error = Error_count([min_sigma, max_sigma, threshold, overlap])
        quality = Quality_count([min_sigma, max_sigma, threshold, overlap])

        Ensure the objectives are returned as a list or array of two values
        solution.objectives[:] = [error, quality]

# Instantiate the problem
problem = MyOptimizationProblem()

# Solve the problem using the NSGA-II algorithm
algorithm_A = NSGAII(problem)

start_time = time.time()  
algorithm_A.run(10)  # Adjust the number of iterations as needed
end_time = time.time()  

duration = end_time - start_time
print(f"NSGA-II Algorithm run took {duration:.2f} seconds.")

# After the run, you can extract the Pareto-optimal solutions
for solution in algorithm_A.result:
    print(f"Objectives: {solution.objectives}, Parameters: {solution.variables}")


### Task specific optimization

class ImageOptimizationProblem(Problem):
    def __init__(self):
        super(ImageOptimizationProblem, self).__init__(3, 2)  # Changed from (1, 2) to (3, 2)
        # Define ranges for window_size, threshold, and a continuous representation of covariance_type
        self.types[:] = [Real(3, 128), Real(0.0, 1.0), Real(0, 3)]
        self.directions[:] = [Problem.MINIMIZE, Problem.MINIMIZE]

    def evaluate(self, solution):
        window_size = int(solution.variables[0])
        threshold = solution.variables[1]

        # Map continuous covariance variable to categorical
        covariance_index = int(solution.variables[2])
        covariance_types = ['full', 'tied', 'diag', 'spherical']
        covariance_type = covariance_types[covariance_index % len(covariance_types)]

        # Call the analyze_image function with the new variables
        normalized_amorphous_area, normalized_amorphous_perimeter = analyze_image(window_size, threshold, covariance_type)
        comp, perimeter = calculate_compactness(normalized_amorphous_perimeter, normalized_amorphous_area)


        # Ensure the objectives are returned as a list or array of two values
        solution.objectives[:] = [comp, normalized_amorphous_perimeter]

covariance_types = ['full', 'tied', 'diag', 'spherical']

problem = ImageOptimizationProblem()
algorithm = NSGAII(problem)
algorithm.run(10)  # Adjust the number of iterations as needed


for solution in algorithm.result:
    window_size = int(solution.variables[0])
    threshold = solution.variables[1]

    # Map the continuous variable for covariance_type back to the categorical value
    covariance_index = int(solution.variables[2])
    covariance_type = covariance_types[covariance_index % len(covariance_types)]

    # Print the best variables along with the objectives
    print(f"Window Size: {window_size}, Threshold: {threshold:.2f}, Covariance Type: {covariance_type}, "
          f"Compactness: {solution.objectives[0]:.2f}, Normalized Perimeter: {solution.objectives[1]:.2f}")