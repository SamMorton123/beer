import os
from simple_term_menu import TerminalMenu
import json

def getUserInput(prompt):
    return input(prompt).strip()

def getInteractiveMenuResponse(title, options):
    print(title)
    menu = TerminalMenu(options)
    return options[menu.show()]

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

def open_beer_data():
    try:
        f = open('data/beer_data.json')
        data = json.load(f)
        f.close()

        return data

    except:
        return {}

def saveFile(data):
    f = open('data/beer_data.json', 'w')
    json.dump(data, f)
    f.close()