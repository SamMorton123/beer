import numpy as np

from src.ratings import BeerRater

class Beer:
    def __init__(self, data):
        self.name = data['name']
        self.style_name = data['style']
        self.brewery_name = data['brewery']
        
        self.rating = data['rating']
        self.scaled_rating = None
    
    def __str__(self):
        return self.name
    
    def __repr__(self):
        return self.name

    def toJsonObject(self):
        return {
            'name': self.name,
            'brewery': self.brewery_name,
            'style': self.style_name,
            'rating': self.rating
        }
    
    def generateScaledScore(self, ratings_for_style, all_user_ratings = None):
        rater = BeerRater()
        self.scaled_rating = rater.scale(
            self.rating, 
            ratings_for_style, 
            all_user_ratings = all_user_ratings
        )
        
        return self.scaled_rating
