from src.beer import Beer

class Brewery:
    def __init__(self, name, beers_data = []):
        self.name = name
        self.beers = [Beer(beer_obj) for beer_obj in beers_data]
    
    def __repr__(self):
        return self.name
    
    def addNewBeer(self, name, style_name, rating):
        self.beers.append(Beer({
            'name': name,
            'style': style_name,
            'brewery': self.name,
            'rating': rating,
        }))
    
    def toJsonObject(self):
        return [beer.toJsonObject() for beer in self.beers]