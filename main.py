from simple_term_menu import TerminalMenu
import json
import numpy as np
import os

from src.user import User
from src.utils import getInteractiveMenuResponse, clear_terminal, saveFile, open_beer_data

ADD_NEW_USER = 'Add new user'

data = open_beer_data()

# assumes first keys in the data are names of users
user_names = list(data.keys()) + [ADD_NEW_USER]
name_menu = TerminalMenu(user_names)
user_name = user_names[name_menu.show()]

user_data = {}
if user_name == ADD_NEW_USER:
    user_name = input('What is your name? ').strip()
else:
    user_data = data[user_name]

user = User(user_name, user_data)

modes = ['Rate a beer', 'Re-rate a beer', 'Add a new beer style', 'Just see the rankings', 'See ratings by style', 'See beer rankings by style']
mode = getInteractiveMenuResponse('Would you like to...',  modes)
clear_terminal()

if mode == 'Add a new beer style':
    user.interactiveAddNewStyle()
    data[user_name] = user.getUpdatedUserData()
    saveFile(data)

if mode == 'Rate a beer':
    user.interactiveRateNewBeer()
    data[user_name] = user.getUpdatedUserData()
    saveFile(data)

if mode == 'Just see the rankings':
    user.getBreweryRatings()

if mode == 'Re-rate a beer':
    user.interactiveRerateBeer()
    data[user_name] = user.getUpdatedUserData()
    saveFile(data)

if mode == 'See ratings by style':
    user.getStyleRatings()

if mode == 'See beer rankings by style':
    user.interactiveSeeRatingsForStyle()