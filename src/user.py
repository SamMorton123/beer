from src.utils import getUserInput, getInteractiveMenuResponse, clear_terminal
from src.style import Style

class User:
    def __init__(self, name, data):
        self.name = name

        self.raw_data = data
        
        raw_style_data = self.raw_data['styles'] if 'styles' in self.raw_data else []
        self.styles = [Style(style) for style in raw_style_data]
        
        self.breweries = []

    def addNewStyle(self, style_name):
        if style_name not in self.styles:
            self.styles.append(Style(style_name))
    
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
                print(f'- {style}')
    
    def getUpdatedUserData(self):
        self.raw_data['styles'] = [str(style) for style in self.styles]
        return self.raw_data
