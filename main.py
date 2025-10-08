from simple_term_menu import TerminalMenu
import json
import numpy as np
import os

from src.user import User
from src.utils import getInteractiveMenuResponse, clear_terminal

ADD_NEW_USER = 'Add new user'

def getBreweriesList(data):
    if 'breweries' in data:
        return list(data['breweries'].keys())
    
    return []

def getBreweryBeerList(bdata, name):
    if 'breweries' not in bdata:
        return []
    
    brewery_data = bdata['breweries'][name]
    return list(set([d['name'] for d in brewery_data]))

def rateBeer(user_data):
    styles = user_data['styles'] if 'styles' in user_data else []
    breweries = getBreweriesList(user_data) + ['Add a new brewery']

    name = input('What is the name of your beer? ').strip()
    clear_terminal()
    
    print('What brewery is it from?')
    breweries_menu = TerminalMenu(breweries)
    brewery_name = breweries[breweries_menu.show()]
    if brewery_name == 'Add a new brewery':
        brewery_name = input('Enter your new brewery: ').strip()
        clear_terminal()

    print("Select your beer's style from the dropdown below:")
    styles_menu = TerminalMenu(styles)
    style = styles[styles_menu.show()]
    clear_terminal()

    rating = float(input('Rate your beer (out of 10): ').strip())
    clear_terminal()

    return {
        'name': name,
        'brewery': brewery_name,
        'style': style,
        'rating': rating
    }

def rerateBeer(user_data):
    breweries = getBreweriesList(user_data)
    if len(breweries) == 0:
        return None
    print('Which brewery is the beer from?')
    breweries_menu = TerminalMenu(breweries)
    brewery_name = breweries[breweries_menu.show()]
    clear_terminal()

    print('Which beer was it?')
    beers = getBreweryBeerList(user_data, brewery_name)
    beers_menu = TerminalMenu(beers)
    beer_name = beers[beers_menu.show()]
    clear_terminal()

    rating = float(input('Rate your beer (out of 10): ').strip())
    clear_terminal()

    brewery_beer_objs = user_data['breweries'][brewery_name]
    brew_obj = None
    for bo in brewery_beer_objs:
        if bo['name'] == beer_name:
            brew_obj = bo
            break

    if brew_obj is None:
        return None
    
    new_beer_obj = { 'name': beer_name, 'style': brew_obj['style'], 'brewery': brewery_name, 'rating': rating }
    user_data['breweries'][brewery_name].append(new_beer_obj)
    return user_data

def getBreweryScore(ratings):
    if (len(ratings)) < 2:
        return None
    
    numerator = sum([d['beer_rating'] * d['style_mean_rating'] for d in ratings])
    denominator = sum([d['style_mean_rating'] for d in ratings])

    return round(numerator / denominator, 2)

def getRatingsListsByStyle(brewery_data):
    styles = {}
    for brewery in brewery_data:
        for beer in brewery_data[brewery]:
            style = beer['style']
            name = beer['name']
            rating = beer['rating']
            brewery = beer['brewery']
            if style in styles:
                if (brewery, name) in styles[style]:
                    styles[style][(brewery, name)].append(rating)
                else:
                    styles[style][(brewery, name)] = [rating]
            else:
                styles[style] = { (brewery, name): [rating] }
    
    style_ratings = {}
    for style in styles:
        if len(styles[style]) == 0:
            continue

        ratings_for_this_style = []
        for tup in styles[style]:
            specific_beer_rating = np.mean(styles[style][tup])
            ratings_for_this_style.append(specific_beer_rating)
        
        style_ratings[style] = ratings_for_this_style
    
    return style_ratings

def getScaledRatingForStyle(style_ratings, given_rating):
    if len(style_ratings) < 3:
        return given_rating

    mean = np.mean(style_ratings)
    std = np.std(style_ratings)
    
    scaled_rating = mean + 1.5 * ((given_rating - mean) / std)
    return scaled_rating

def getStyleRatings(brewery_data):
    styles_ratings_data = getRatingsListsByStyle(brewery_data)
    style_ratings = []
    for style in styles_ratings_data:
        ratings_for_this_style = styles_ratings_data[style]
        style_ratings.append((style, round(np.mean(ratings_for_this_style), 2), len(ratings_for_this_style)))
    
    return sorted(style_ratings, key=lambda tup: tup[1], reverse=True)

def getBreweryRatingsPerBeer(brewery_beer_data):
    beers = {}
    for beer in brewery_beer_data:
        name = beer['name']
        rating = beer['rating']

        if name in beers:
            beers[name].append(rating)
        else:
            beers[name] = [rating]
    
    return [np.mean(beers[b]) for b in beers]

def getScaledBreweryRatingsPerBeer(brewery_beer_data, style_ratings):
    beers = {}
    for beer in brewery_beer_data:
        name = beer['name']
        rating = beer['rating']
        style = beer['style']
        scaled_rating = getScaledRatingForStyle(style_ratings[style], rating)
        style_mean_rating = np.mean(style_ratings[style])

        if name in beers:
            beers[name]['ratings_array'].append(scaled_rating)
        else:
            beers[name] = { 'style_mean_rating': style_mean_rating, 'ratings_array': [scaled_rating] }
    
    return [{ 'beer_rating': np.mean(beers[b]['ratings_array']), 'style_mean_rating': beers[b]['style_mean_rating'] } for b in beers]

def getBreweryRatings(user_data):
    sdata = user_data['styles'] if 'styles' in user_data else [] 
    bdata = user_data['breweries'] if 'breweries' in user_data else {}

    style_ratings = getRatingsListsByStyle(bdata)

    ratings = []
    unrated = []
    for b in bdata:
        brew_ratings = getScaledBreweryRatingsPerBeer(bdata[b], style_ratings)
        brewery_rating = getBreweryScore(brew_ratings)
        if (brewery_rating is None):
            unrated.append((b, 'unrated'))
        else:
            ratings.append((b, brewery_rating))
    
    return sorted(ratings, key = lambda b: b[1], reverse = True) + unrated

def saveFile(data):
    f = open('data/beer_data.json', 'w')
    json.dump(data, f)
    f.close()

f = open('data/beer_data.json')
data = json.load(f)
f.close()

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

# modes = ['Rate a beer', 'Re-rate a beer', 'Add a new beer style', 'Just see the rankings', 'See ratings by style']
mode = getInteractiveMenuResponse('Would you like to...',  ['Add a new beer style', 'Rate a beer'])
clear_terminal()

if mode == 'Add a new beer style':
    user.interactiveAddNewStyle()
    data[user_name] = user.getUpdatedUserData()
    saveFile(data)

if mode == 'Rate a beer':
    user.interactiveRateNewBeer()
    data[user_name] = user.getUpdatedUserData()
    saveFile(data)

# if mode == 'Just see the rankings':
#     user_beer_data = user_data['breweries'] if 'breweries' in user_data else {}
#     print('Your ratings:')
#     ratings = getBreweryRatings(user_data)
#     for i in range(len(ratings)):
#         print(f'{i + 1}. {ratings[i][0]} - {ratings[i][1]}')

# if mode == 'Re-rate a beer':
#     new_user_data = rerateBeer(user_data)
#     data[user] = new_user_data
#     saveFile(data)

#     ratings = getBreweryRatings(new_user_data)
#     for brewery in ratings:
#         print(f'{brewery[0]} - {brewery[1]}')

# if mode == 'See ratings by style':
#     clear_terminal()
#     ratings = getStyleRatings(user_data['breweries'])
#     print('Rankings:')
#     thresh = 3
#     high_cardinality = [tup for tup in ratings if tup[2] >= thresh]
#     for i in range(len(high_cardinality)):
#         style, rating, count = high_cardinality[i]
#         print(f'{i + 1}. {style} - {rating} ({count})')
    
#     print('\n\nRankings for styles with too few ratings:')
#     low_cardinality = [tup for tup in ratings if tup[2] < thresh]
#     for i in range(len(low_cardinality)):
#         style, rating, count = low_cardinality[i]
#         print(f'{i + 1}. {style} - {rating} ({count})')