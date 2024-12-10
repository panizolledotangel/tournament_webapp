import os
from typing import Dict

from sources.logic.problem import Problem
from sources.logic.tsp_reader import TSPFileReader


class TSPProblem(Problem):

    def __init__(self):
        self.tsp = TSPFileReader(os.getenv("PROBLEM_PATH"))
        self.tsp.read()

    def solve(self, result: Dict) -> float:
        return self.tsp.path_distance(result["solution"])