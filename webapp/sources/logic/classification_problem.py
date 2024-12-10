import os
import pandas as pd
from sklearn.metrics import f1_score
from typing import Dict

from sources.logic.problem import Problem

class ClassificationProblem(Problem):

    def __init__(self):
        self.ground_truth = pd.read_csv(os.getenv("PROBLEM_PATH"))

    def solve(self, solution: Dict) -> float:
        pred_df = pd.DataFrame.from_dict(solution, orient='index').transpose()
        join_df = pred_df.set_index('nid').join(self.ground_truth.set_index('nid'), lsuffix='_pred', rsuffix='_real')
        return f1_score(join_df.y_real, join_df.y_pred, average='micro')        
