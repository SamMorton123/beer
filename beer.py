from simple_term_menu import TerminalMenu
import json
import numpy as np
import os

ADD_NEW_USER = 'Add new user'

def addNewStyle(user, data):
    styles = data['styles'] if 'styles' in data else []
    adding_styles = True
    while adding_styles:
        new_style = input('Enter your new style name: ').strip()
        if new_style not in styles:
            styles.append(new_style)
        print('Would you like to add another?')
        options = ['Yes', 'No']
        menu = TerminalMenu(options)
        if options[menu.show()] == 'No':
            adding_styles = False
    
    print('\n\nYour style list is now:')
    for style in styles:
        print(f'- {style}')
    
    return styles

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

def getRating(ratings):
    if (len(ratings)) < 2:
        return None

    avg = np.mean(ratings)
    num_over_threshold = 0
    for r in ratings:
        if r > 9.5: num_over_threshold += 1
    return round(avg + (num_over_threshold * 0.2), 2)

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

def getBreweryRatings(bdata):
    ratings = []
    unrated = []
    for b in bdata:
        brew_ratings = getBreweryRatingsPerBeer(bdata[b])
        brewery_rating = getRating(brew_ratings)
        if (brewery_rating is None):
            unrated.append((b, 'unrated'))
        else:
            ratings.append((b, brewery_rating))
    
    return sorted(ratings, key = lambda b: b[1], reverse = True) + unrated

def saveFile(data):
    f = open('data/beer_data.json', 'w')
    json.dump(data, f)
    f.close()

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

f = open('data/beer_data.json')
data = json.load(f)
f.close()

# assumes first keys in the data are names of users
user_names = list(data.keys()) + [ADD_NEW_USER]
name_menu = TerminalMenu(user_names)
user = user_names[name_menu.show()]

user_data = {}
if user == ADD_NEW_USER:
    user = input('What is your name? ').strip()
else:
    user_data = data[user]

# Allow the user to enter add a style mode or add a rating mode
print('\n\nWould you like to...')
modes = ['Rate a beer', 'Re-rate a beer', 'Add a new beer style', 'Just see the rankings']
modes_menu = TerminalMenu(modes)
mode = modes[modes_menu.show()]

clear_terminal()
if mode == 'Add a new beer style':
    styles = addNewStyle(user, user_data)
    user_data['styles'] = styles
    data[user] = user_data

    saveFile(data)

if mode == 'Rate a beer':
    user_beer_data = user_data['breweries'] if 'breweries' in user_data else {}
    beer = rateBeer(user_data)
    
    if beer['brewery'] in user_beer_data:
        user_beer_data[beer['brewery']].append(beer)
    else:
        user_beer_data[beer['brewery']] = [beer]
    
    print('Your beer ratings are now:')
    ratings = getBreweryRatings(user_beer_data)
    for brewery in ratings:
        print(f'{brewery[0]} - {brewery[1]}')

    user_data['breweries'] = user_beer_data
    data[user] = user_data
    saveFile(data)

if mode == 'Just see the rankings':
    user_beer_data = user_data['breweries'] if 'breweries' in user_data else {}
    print('Your ratings:')
    ratings = getBreweryRatings(user_beer_data)
    for i in range(len(ratings)):
        print(f'{i + 1}. {ratings[i][0]} - {ratings[i][1]}')

if mode == 'Re-rate a beer':
    new_user_data = rerateBeer(user_data)
    data[user] = new_user_data
    saveFile(data)

    ratings = getBreweryRatings(new_user_data['breweries'])
    for brewery in ratings:
        print(f'{brewery[0]} - {brewery[1]}')

# if mode == 'See ratings by style:'