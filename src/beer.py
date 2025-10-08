class Beer:
    def __init__(self, data):
        self.name = data['name']
        self.style_name = data['style']
        self.rating = data['rating']
        self.brewery_name = data['brewery']
    
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