from src.utils import getUserInput, getInteractiveMenuResponse, clear_terminal
from src.style import Style
from src.brewery import Brewery

class User:
    def __init__(self, name, data):
        self.name = name

        self.raw_data = data

        raw_breweries_data = self.raw_data['breweries'] if 'breweries' in self.raw_data else {}
        self.breweries = {
            brewery_name: Brewery(brewery_name, raw_breweries_data[brewery_name]) 
            for brewery_name in raw_breweries_data
        }
        
        raw_style_data = self.raw_data['styles'] if 'styles' in self.raw_data else []
        self.styles = { style: Style(style) for style in raw_style_data }
        self._syncStylesWithBreweries()

    def _syncStylesWithBreweries(self):
        for brewery_name in self.breweries:
            brewery = self.breweries[brewery_name]
            for beer in brewery.beers:
                if beer.style_name in self.styles:
                    self.styles[beer.style_name].tagged_beers.append(beer)

    def addNewStyle(self, style_name):
        if style_name not in self.styles:
            self.styles[style_name] = Style(style_name)
    
    def interactiveAddNewStyle(self, verbose = True):
        adding_styles = True
        while adding_styles:
            new_style = getUserInput('Enter your new style name: ')
            self.addNewStyle(new_style)
        
            user_response = getInteractiveMenuResponse('Would you like to add another?', ['Yes', 'No'])
            if user_response == 'No':
                adding_styles = False
    
        clear_terminal()
        if verbose:
            print('Your style list is now:')
            for style in self.styles:
                print(f'- {self.styles[style]}')
    
    def interactiveRateNewBeer(self, verbose = True):
        new_beer_name = getUserInput('What is the name of your beer? ')
        clear_terminal()

        brewery_lst = list(self.breweries.keys()) + ['Add new brewery']
        brewery_name = getInteractiveMenuResponse('What brewery is it from?', brewery_lst)

        style_name = getInteractiveMenuResponse("Select your beer's style from the dropdown below:", list(self.styles.keys()))
        clear_terminal()

        rating = float(getUserInput('Rate your beer out of 10 '))
        clear_terminal()

        self._save_new_beer(new_beer_name, brewery_name, style_name, rating)

    def _save_new_beer(self, name, brewery_name, style_name, rating):
        if brewery_name not in self.breweries:
            self.breweries[brewery_name] = Brewery(brewery_name)
        
        self.breweries[brewery_name].addNewBeer(name, style_name, rating)
        self._syncStylesWithBreweries()

    
    def getUpdatedUserData(self):
        self.raw_data['styles'] = [str(self.styles[style]) for style in self.styles]
        self.raw_data['breweries'] = {
            brewery_name: self.breweries[brewery_name].toJsonObject()
            for brewery_name in self.breweries
        }
        return self.raw_data
