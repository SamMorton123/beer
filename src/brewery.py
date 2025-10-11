from src.beer import Beer
import numpy as np

class Brewery:
    def __init__(self, name, beers_data = []):
        self.name = name
        self.beers = [Beer(beer_obj) for beer_obj in beers_data]

        self.score = None
    
    def __str__(self):
        return self.name
    
    def __repr__(self):
        return self.name

    def getRatingString(self):
        return f'{self.name}: {self.score}'
    
    def addNewBeer(self, name, style_name, rating):
        self.beers.append(Beer({
            'name': name,
            'style': style_name,
            'brewery': self.name,
            'rating': rating,
        }))

    def generateScore(self, ratings_lists_by_style, rating_threshold = 2):
        """
        ratings_lists_by_style - { style_name: [...float ratings for each of the beers tagged to that style] }
        """

        if len(self.beers) < rating_threshold:
            self.score = None
            return self.score

        mean_style_ratings = {style: np.mean(ratings_lists_by_style[style]) for style in ratings_lists_by_style if len(ratings_lists_by_style[style]) > 0}

        numerator = 0
        denominator = 0
        for beer in self.beers:
            beer.generateScaledScore(ratings_lists_by_style[beer.style_name])

            weighted_score_from_beer = beer.scaled_rating * mean_style_ratings[beer.style_name]
            numerator += weighted_score_from_beer
            denominator += mean_style_ratings[beer.style_name]
        
        self.score = round(numerator / denominator, 2)
        return self.score

    def toJsonObject(self):
        return [beer.toJsonObject() for beer in self.beers]