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