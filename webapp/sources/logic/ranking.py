import os
import pytz
from datetime import datetime
from typing import List, Dict

from sources.logic.problem import Problem


class Ranking:

    OK_STATUS = 1
    ERROR_STATUS = -1
    PENDING = 0

    def __init__(self, contestants: List[str], problem: Problem, maximize: bool):
        self.tz_info = pytz.timezone(os.environ["TIMEZONE"])
        self.problem = problem
        self.maximize = maximize
        self.ranking = self._create_ranking(contestants)
    
    def update(self, contestant: str, filename: str, result: Dict):
        try:
            score = self.problem.solve(result)
            self.ranking[contestant]["status"] = self.OK_STATUS
            self.ranking[contestant]["message"] = f"Submitted: {filename} on {datetime.now(self.tz_info).strftime('%H:%M')}"
            self._update_score(contestant, score)
        except Exception as e:
            self.set_error(contestant, f"Error on {filename}: {e}")

    def set_error(self, contestant: str, error: str):
        self.ranking[contestant]["status"] = self.ERROR_STATUS
        self.ranking[contestant]["message"] = error

    def get_scores(self):
        return self.ranking
    
    def load_scores(self, scores: Dict):
        self.ranking = scores
    
    def get_status(self, contestant: str):
        return self.ranking[contestant]["status"]
    
    def get_messages(self):
        return [{"name": c, "message": self.ranking[c]["message"]} for c in self.ranking.keys()]
    
    def get_scores_evolution(self):
        contestants = list(self.ranking.keys())
        data = {
            'contestants': contestants,
            'scores': [self.ranking[c]["last"] for c in contestants],
            'times': [self.ranking[c]["last_time"] for c in contestants]
        }
        return data
    
    def _create_ranking(self, contestants: List[str]):
        return {
            c: {
                "best": int(os.environ["INITIAL_SCORE"]), 
                "last": [int(os.environ["INITIAL_SCORE"])],
                "last_time": [datetime.now(self.tz_info).strftime('%H:%M')], 
                "status": self.PENDING, 
                "message": "No score submitted jet"
            } for c in contestants
        }
    
    def _update_score(self, contestant: str, score: float):
        if self.maximize:
            if score > self.ranking[contestant]["best"]:
                self.ranking[contestant]["best"] = score
        else:
            if score < self.ranking[contestant]["best"]:
                self.ranking[contestant]["best"] = score 
        
        self.ranking[contestant]["last"].append(score)
        self.ranking[contestant]["last_time"].append(datetime.now(self.tz_info).strftime('%H:%M'))
