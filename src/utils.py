import os
from simple_term_menu import TerminalMenu

def getUserInput(prompt):
    return input(prompt).strip()

def getInteractiveMenuResponse(title, options):
    print(title)
    menu = TerminalMenu(options)
    return options[menu.show()]

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')