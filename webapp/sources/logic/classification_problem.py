import pandas as pd
from sklearn.metrics import f1_score
from typing import Dict

from webapp.sources.logic.problem import Problem

class ClassificationProblem(Problem):

    def __init__(self, ground_truth):
        self.ground_truth = pd.read_csv(ground_truth)

    def solve(self, solution: Dict) -> float:
        pred_df = pd.DataFrame({
            'nid':solution['nid'],
            'y': solution['y']
        })
        join_df = pred_df.set_index('nid').join(self.ground_truth.set_index('nid'), lsuffix='_pred', rsuffix='_real')
        return f1_score(join_df.y_real, join_df.y_pred, average='micro')        
