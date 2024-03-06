import os
from typing import List

from sources.logic.problem import Problem
from sources.logic.tsp_reader import TSPFileReader


class TSPProblem(Problem):

    def __init__(self):
        self.tsp = TSPFileReader(os.getenv("PROBLEM_PATH"))
        self.tsp.read()

    def solve(self, solution: List[int]) -> float:
        return self.tsp.path_distance(solution)