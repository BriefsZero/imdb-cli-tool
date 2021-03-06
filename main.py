from bs4 import BeautifulSoup
import requests
import json
import re
import sys

# Global variables for imdb and parser
base_url = 'https://www.imdb.com/'
parser = 'html.parser'
regex = "^[a-zA-Z]+(([\'\,\.\- ][a-zA-Z ])?[a-zA-Z]*)*$"


def get_response(base, query):
    return requests.get(base + query)


# Helper function that makes reversing cleaner
def reverse_list(my_list, bool):
    return reversed(my_list) if not bool else my_list


# Simple function that gets actor name
def get_actor_name():
    while True:
        user_input = input("\nHello, Please enter the Movie Stars Name: ")
        # user_input = "Tom Cruise"
        if re.search(regex, user_input):
            break
        else:
            print("Please enter a valid name.")
    # return input("\nHello, Please enter the Movie Stars Name: ")
    return user_input


def get_actors(actor_name):
    """ A function, given an name will scrap data from IMDB for a list of actors
    Input -> actor_name: string
    Return -> actor_list: list of tuples, (actor_name, url) """

    query = "find?q=" + actor_name.replace(" ", "+") + '&s=nm'

    response = get_response(base_url, query)
    # Parsing through the response data to grab a list of given actors for the actor name
    soup = BeautifulSoup(response.text, parser)

    try:
        results = soup.findAll("table", {"class": "findList"})[0]
    except IndexError as err:
        return []
    actors = results.findAll("td", {"class": "result_text"})

    # List comprehension which returns a list of tuples, in the form (Actor Name, URL for Actor)
    # Fun implementation however, extremely hard to read
    # actor_list = [(el[0].getText(), el[0]['href'])
    #               for actor in actors if (el := actor.findAll('a')) != 'NaN']
    actor_list = []
    for actor in actors:
        el = actor.findAll('a')[0]
        actor_list.append((el.getText(), el['href']))

    return actor_list


def get_specific_actor(actor_list):
    """ If get_actors returns a list of size > 1, this function is called to get a specific actor
    input -> actor_list: list of tuples, (actor_name, url)
    return -> tuple: (actor_name, url) """
    # Prints out the list of actors with a enumerated number
    [print((str(i) + "."), actor[0]) for i, actor in enumerate(actor_list, 1)]
    print("It seems your query has returned a couple of actors, which actor were you looking for? ")

    # Checks or errors from user input, will continue to prompt user until they enter a valid number
    while True:
        user_input = input("Please enter the number next to the actor above: ")
        try:
            user_input = int(user_input)
            indx = user_input - 1
            if indx >= len(actor_list):
                raise ValueError()
            break
        except ValueError as err:
            print("Please enter a valid number listed above")

    return actor_list[indx]


def get_movies(actor, reverse):
    """ This gets a list of the movies that an actor is involved with
    input -> actor: Tuple (actor_name, url), reverse: bool
    return -> movie_list: object { name: string, movies: list } """
    query = actor[1]
    actor_name = actor[0]
    response = get_response(base_url, query)

    # Once again parses through the given response, returning all the films given actor is in
    soup = BeautifulSoup(response.text, parser)
    results = soup.findAll("div", {"id": re.compile('actor-.*')})
    movies = []
    for movie in results:
        movies.append(movie.findAll("b"))
    movie_list = {"name": actor_name,
                  "movies": []
                  }

    for movie in reverse_list(movies, reverse):
        movie = movie[0].getText()
        movie_list["movies"].append(movie)
    return movie_list


def print_movies(movies):
    [print(movie) for movie in movies["movies"]]


def send_to_json(actor_name, movie_list):
    """Simple function to send the list of movies to a JSON file
    input -> actor_name: string, movie_list: object { name: string, movies: list }"""
    with open(actor_name.replace(" ", "_") + '_movies.json', 'w', encoding='utf-8') as f:
        json.dump(movie_list, f, ensure_ascii=False,
                  indent=4)


def handle_yes_no(question):
    """Helper function to deal with yes or no responses
    input -> question: string
    return -> bool"""
    while True:
        user_input = input(
            question)
        if user_input in ('yes', 'no', 'y', 'n'):
            return str_to_bool(user_input)
        else:
            print("That wasn't valid option, try again ...")


def str_to_bool(string):
    """Another helper function, the converts yes, y to true
    input -> string: string
    return -> bool"""
    return string in ('yes', 'y')


if __name__ == "__main__":
    print("IMDB Movie Star Search")
    print("**********************")
    actor_name = get_actor_name()
    actors = get_actors(actor_name)
    if len(actors) > 1:
        actor = get_specific_actor(actors)
    elif len(actors) == 1:
        actor = actors[0]
    else:
        print("This name you provided does not seem to be an actor")
        sys.exit("This script will now quit")
    actor_name = actor[0]

    print("\nAwesome, I will now list the movies %s is in" % actor_name)
    question = "By the way, would you like the movies listed in newest first? [y/n]: "
    user_input = handle_yes_no(question)

    movies = get_movies(actor, user_input)
    if len(movies["movies"]) > 0:
        print("\nThe movie\s that %s is in are:" % actor_name)
    else:
        print("This name you provided does not seem to be an actor")
        sys.exit("This script will now quit")
    print_movies(movies)
    question = "Would you like these movies published to a JSON document? [y/n]: "
    user_input = handle_yes_no(question)
    if user_input:
        send_to_json(actor_name, movies)
