import numpy as np
from itertools import product, pairwise
from typing import List


class TSPFileReader:

    HEADER = 0
    NODE_COORD_SECTION = 1

    def __init__(self, filename: str):
        self.filename = filename
        self.points = {}
        self.state = self.HEADER
        self.dist_matrix = None

    def read(self):
        """
        Read the file and store the points in a dictionary
        """
        with open(self.filename, 'r') as f:
            for line in f:
                if self.state == self.HEADER:
                    if line.startswith("NODE_COORD_SECTION"):
                        self.state = self.NODE_COORD_SECTION
                elif self.state == self.NODE_COORD_SECTION:
                    if not line.startswith("EOF"):
                        fields = line.split()
                        self.points[int(fields[0])-1] = (float(fields[1]), float(fields[2]))

        assert self.state == self.NODE_COORD_SECTION, "File format error"
        self._calculate_distance_matrix()

    def calculate_distance(self, i: int, j: int) -> float:
        """
        Calculate the distance between two points
        Args:
            i, j: the index of the points
        """
        assert self.state == self.NODE_COORD_SECTION, "Please read the file first"

        return ((self.points[i][0] - self.points[j][0])**2 + (self.points[i][1] - self.points[j][1])**2)**0.5

    def path_distance(self, path: List[int]) -> float:
        """
        Calculate the distance of a circular path. The last point will be connected to the first point
        Args:
            path: a list of points, the last point will be connected to the first point
        """
        assert self.state == self.NODE_COORD_SECTION, "Please read the file first"

        mask = np.array(list(pairwise(path + [path[0]])))
        return self.dist_matrix[mask[:,0], mask[:,1]].sum() 

    def n_points(self) -> int:
        """
        Return the number of points
        """
        assert self.state == self.NODE_COORD_SECTION, "Please read the file first"
        return len(self.points)

    def get_points_ids(self) -> List[int]:
        """
        Return the ids of the points
        """
        assert self.state == self.NODE_COORD_SECTION, "Please read the file first"
        return list(self.points.keys())
    
    def get_distance_matrix(self) -> np.array:  
        """
        Return the distance matrix
        """
        assert self.state == self.NODE_COORD_SECTION, "Please read the file first"
        return self.dist_matrix
    
    def _calculate_distance_matrix(self):
        """
        Calculate the distance matrix
        """
        self.dist_matrix = np.array([self.calculate_distance(i,j) for i,j in product(self.points.keys(), repeat=2)]).reshape(self.n_points(), self.n_points())