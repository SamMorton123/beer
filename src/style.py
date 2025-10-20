import numpy as np

class Style:
    def __init__(self, name):
        self.name = name
        self.tagged_beers = []

    def __str__(self):
        return self.name
    
    def __repr__(self):
        return f'Name: {self.name}, Beers: {self.tagged_beers};'
    
    def getRating(self):
        ratings_lst = [beer.rating for beer in self.tagged_beers]
        return np.mean(ratings_lst)