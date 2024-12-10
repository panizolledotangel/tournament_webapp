import os
from datetime import datetime
from typing import List, Dict

from sources.logic.problem import Problem


class Ranking:

    OK_STATUS = 1
    ERROR_STATUS = -1
    PENDING = 0

    def __init__(self, contestants: List[str], problem: Problem, maximize: bool):
        self.problem = problem
        self.ranking = self._create_ranking(contestants)
        self.maximize = maximize
    
    def update(self, contestant: str, filename: str, result: Dict):
        try:
            score = self.problem.solve(result)
            self.ranking[contestant]["status"] = self.OK_STATUS
            self.ranking[contestant]["message"] = f"Submitted: {filename} on {datetime.now().strftime('%H:%M')}"
            self._update_score(contestant, score)
        except Exception as e:
            self.set_error(contestant, f"Error on {filename}: {e}")

    def set_error(self, contestant: str, error: str):
        self.ranking[contestant]["status"] = self.ERROR_STATUS
        self.ranking[contestant]["message"] = error

    def get_scores(self):
        return self.ranking
    
    def get_status(self, contestant: str):
        return self.ranking[contestant]["status"]
    
    def get_messages(self):
        return [{"name": c, "message": self.ranking[c]["message"]} for c in self.ranking.keys()]
    
    def _create_ranking(self, contestants: List[str]):
        return {c: {"best": int(os.environ["INITIAL_SCORE"]), "last": [int(os.environ["INITIAL_SCORE"])], "status": self.PENDING, "message": "No score submitted jet"} for c in contestants}
    
    def _update_score(self, contestant: str, score: float):
        if self.maximize:
            if score > self.ranking[contestant]["best"]:
                self.ranking[contestant]["best"] = score
        else:
            if score < self.ranking[contestant]["best"]:
                self.ranking[contestant]["best"] = score 
        
        self.ranking[contestant]["last"].append(score)
