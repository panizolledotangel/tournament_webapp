from abc import ABC, abstractmethod


class Problem(ABC):
    
    @abstractmethod
    def solve(self, solution) -> float:
        pass