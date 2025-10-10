import numpy as np

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
    
    def generateScaledScore(self, ratings_for_style, rating_threshold = 3):
        if len(ratings_for_style) < rating_threshold:
            self.scaled_rating = self.rating
            return self.scaled_rating
        
        style_mean = np.mean(ratings_for_style)
        style_std = np.std(ratings_for_style)

        self.scaled_rating = style_mean + 1.5 * ((self.rating - style_mean) / style_std)
        return self.scaled_rating
