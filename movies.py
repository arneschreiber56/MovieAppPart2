"""
Codio Project: My Movies Database – Extended CLI Application

This module implements a menu-driven command-line application for
managing a personal movie database as a MasterSchool project.

The application supports full CRUD functionality (Create, Read,
Update, Delete) as well as analytical and visualization features.
Each movie is represented as a sqlite3 database entry containing the following
attributes:

    - title (text(str)): The movie title
    - rating (real(float)): The user-defined rating (1–10)
    - year (integer(int)): The release year

Features
--------
- List all stored movies
- Add new movies
- Delete existing movies
- Update movie ratings
- Display statistical insights (average, median, best, worst)
- Select a random movie
- Search movies (including fuzzy matching)
- Sort movies by rating
- Generate and save a histogram of ratings

"""
import movie_storage_sql as storage
import os
import requests
import sys

import difflib
from dotenv import load_dotenv
import random
import statistics

import matplotlib.pyplot as plt
from rich.console import Console
from rich.panel import Panel

load_dotenv()

console = Console()  # fits nicer in snake_case


URL = os.getenv("URL")
API_KEY = os.getenv("API_KEY")


def print_messages():
    messages = {
        "continue": "\n[dim]Press enter to continue[/dim]",
        "exit": "[bold red]Exiting My Movies Database... Goodbye![/bold red]",
        "similar_movie": "[green]Similar movies found: [/green]",
        "input_name": "\nEnter movie name: ",
        "input_rating": "Enter new movie rating (1-10): ",
        "input_year": "Enter release year: ",
        "input_histo_name": "\n[green]Please enter the filename for the "
                            "histogram: [/green]",
        "error_db": "[red]Could not process Database correctly![/red]",
        "no_movies_error": "[red]No movies in the DB available![/red]",
        "error_no_movie": "[red]Could not find your movie in the DB![/red]",
        "error_no_sim_movie": "[red]No similar movies found.[/red]",
        "error_movie_exists": "[red]Movie already exists![/red]",
        "error_not_valid": "[red]Your entry is not valid![/red]",
        "error_rating": "[red]Rating must be between 1 and 10![/red]",
        "error_get_response": "[red]Unexpected response from API-request[/red]",
        "error_valid_year": "[red] No valid year available![/red]",
        "error_valid_rating": "[red] No valid rating available![/red]"
    }
    return messages


def start_screen():
    """
    Displays the application start screen and menu options.

    Returns:
        str: The user's menu selection as a string.
    """
    console.print(
        Panel(
            "[bold_magenta]My Movies Database[/bold_magenta]",
            expand=False,
            border_style="magenta",
        )
    )
    menu = (
        "[cyan]0. Exit\n"
        "1. List movies\n"
        "2. Add movie\n"
        "3. Delete movie\n"
        "4. Update movie\n"
        "5. Stats\n"
        "6. Random movie\n"
        "7. Search movie\n"
        "8. Movies sorted by rating\n"
        "9. Draw histogram of rankings[/cyan]"
    )
    console.print(
        Panel(
            menu,
            title="[bold cyan]Menu[bold cyan]",
            expand=False,
            border_style="cyan"
        )
    )
    choice = console.input(
        "[bold bright_cyan]Enter choice (0-9): [/bold bright_cyan]"
    )
    return choice


def movie_db_function_list():
    """
    Displays all movies stored in the database.

    Returns:
        None
    """
    movies = storage.list_movies()
    if movies:
        console.print(f"\n[cornsilk1]{len(movies)} movies in total[/cornsilk1]")
        for movie, attributes in movies.items():
            console.print(
                f"[cornsilk1]{movie}: "
                f"{attributes['rating']} ({attributes['year']})[cornsilk1]"
            )
    else:
        console.print(print_messages()["no_movies_error"])
    console.input(print_messages()["continue"])


def check_rating(rating):
    """Checks if the rating is valid."""
    if 1 <= rating <= 10:
        return True
    return False


def check_double_titles(title):
    """Checks if the movie title is a double title.

    Returns:
        bool: True if double, else False.
        """
    movies = storage.list_movies()
    if movies:
        for movie in movies.keys():
            if movie.lower() == title.lower():
                return True
    return False


def get_api_response(search_title):
    """Sends an api request to OMDb API to request for movie information
    returns a dictionary with movie information or error content, else None. """
    data = {
        "t": search_title,
        "apikey": API_KEY
    }
    try:
        response = requests.get(URL, params=data, timeout= 10)
    except requests.exceptions.RequestException as e:
        return None, str(e)
    if response.status_code == 200:
        return response.json(), None
    else:
        return None, None


def movie_db_function_add():
    """CLI wrapper to add a movie with user input."""
    while True:
        search_title = console.input(print_messages()["input_name"]).strip()
        if not search_title:
            console.print(print_messages()["error_not_valid"])
            console.input(print_messages()["continue"])
            return
        elif check_double_titles(search_title):
            console.print(print_messages()["error_movie_exists"])
        else:
            break

    movie_info, error_message = get_api_response(search_title)

    if error_message:
        console.print(f"[red]{error_message}[/red]")
        console.input(print_messages()["continue"])
        return
    if not movie_info or movie_info.get("Title") == "N/A":
        console.print(print_messages()["error_get_response"])
        console.input(print_messages()["continue"])
        return
    if movie_info.get("Response") == "False":
        console.print(f"[red]{movie_info.get('Error')}[/red]")
        console.input(print_messages()["continue"])
        return

    title = movie_info.get("Title")
    if movie_info.get("Year").isdigit():
        year = int(movie_info.get("Year"))
    else:
        console.print(print_messages()["error_valid_year"])
        console.input(print_messages()["continue"])
        return
    rating = None
    for r in movie_info.get("Ratings", []): #Returns empty list if no "Ratings"
        if r["Source"] == "Internet Movie Database":
            rating = float(r["Value"].split("/")[0])
            break
    if not rating:
        console.print(print_messages()["error_valid_rating"])
        console.input(print_messages()["continue"])
        return
    poster_url = movie_info.get("Poster")

    storage.add_movie(title, year, rating, poster_url)
    console.input(print_messages()["continue"])


def movie_db_function_del():
    """CLI wrapper to delete a movie."""
    while True:
        title = console.input(print_messages()["input_name"]).strip()
        if title:
            break
        else:
            console.print(print_messages()["error_not_valid"])
            console.input(print_messages()["continue"])
            return
    storage.delete_movie(title)
    console.input(print_messages()["continue"])


def movie_db_function_update():
    """CLI wrapper to update a movie rating."""

    title = console.input(print_messages()["input_name"]).strip()
    if not title:
        console.print(print_messages()["error_not_valid"])
        console.input(print_messages()["continue"])

    while True:
        try:
            new_rating = float(console.input(print_messages()["input_rating"]))
            if 1 <= new_rating <= 10:
                break
            console.print(print_messages()["error_rating"])
        except ValueError:
            console.print(print_messages()["error_not_valid"])

    storage.update_movie(title, new_rating)
    console.input(print_messages()["continue"])


def sort_movies_logic(movies_list):
    """Return movies sorted by rating descending and title ascending."""
    sorted_to_ratings = sorted(
        movies_list,
        key=lambda m: (-m[2], m[0]) # m[2] = rating, m[0] = title
    )
    return sorted_to_ratings


def create_movie_list_of_tuples(movies):
    """Gets a dictionary (keys = titles) of dictionaries (data: year and rating)
    and transformed it in a list of tuples with one tuple for each movie:
    ("title", "year", "rating")
    """
    return [
        (title, data["year"], data["rating"])
        for title, data in movies.items()
    ]


def best_worst_movie_logic(sorted_movies):
    """creates two lists, one for the movies with the shared highest rating and
    one for the movies with the shared lowest rating"""
    highest_rating = sorted_movies[0][2]
    lowest_rating = sorted_movies[-1][2]

    best_movies = [m for m in sorted_movies if m[2] == highest_rating]
    worst_movies = [m for m in sorted_movies if m[2] == lowest_rating]

    return best_movies, worst_movies


def stats_logic(movies):
    """Compute average, median, the best and worst movies. Gets the sorted movie
    list from sort_movies_logic()"""
    # In the case of movies == None:
    if not movies:
        return None, None, [], []

    movies_list = create_movie_list_of_tuples(movies)

    ratings = [movie[2] for movie in movies_list]
    avg = statistics.mean(ratings)
    med = statistics.median(ratings)

    sorted_movies = sort_movies_logic(movies_list)

    best_movies, worst_movies = best_worst_movie_logic(sorted_movies)

    return avg, med, best_movies, worst_movies


def movie_db_function_stats():
    """CLI wrapper to display stats."""
    movies = storage.list_movies()
    avg, med, best, worst = stats_logic(movies)
    # Taking care of empty database return values from stats_logic():
    if avg is None:
        console.print(print_messages()["no_movies_error"])
        console.input(print_messages()["continue"])
        return
    console.print(f"[green]Average rating: {avg:.1f}[/green]")
    console.print(f"[green]Median rating: {med:.1f}[/green]")
    for movie in best:
        console.print(
            f"[green]Best movie: {movie[0]}, {movie[2]}[/green]"
        )
    for movie in worst:
        console.print(
            f"[green]Worst movie: {movie[0]}, {movie[2]}[/green]"
        )
    console.input(print_messages()["continue"])


def get_random_logic():
    """Select a random movie from the movie DB
    via list_movies() in movie_storage_sql.py and returns it as well as the
    movie dictionary."""
    movies = storage.list_movies()
    if not movies:
        return None
    random_movie = random.choice(list(movies.keys()))
    return movies, random_movie


def movie_db_function_random():
    """
    Displays a random movie from the database selected by random_logic().

    Returns:
        None
    """
    movies, random_movie = get_random_logic()
    if not random_movie:
        console.print(print_messages()["no_movies_error"])
    else:
        console.print(
            f"\n[green]Your movie for tonight: {random_movie}, "
            f"it's rated {movies[random_movie]['rating']} "
            f"({movies[random_movie]['year']})[/green]"
        )
    console.input(print_messages()["continue"])


def search_movie_logic(search_for, movies):
    """
    Search for movies by partial title match and fuzzy similarity.

    Args:
        search_for (str): The term to search for.
        movies (dict[dict]): Export of the movie database.

    Returns:
        tuple:
            - list[dict]: Exact/partial matches
            - list[str]: Similar movie titles (fuzzy matches)
    """
    titles = [movie for movie in movies.keys()]
    exact_matches = []
    for title in titles:
        if search_for.lower() in title.lower():
            exact_matches.append(title)
    if exact_matches:
        return exact_matches, []
    # Fuzzy matching
    close_matches = difflib.get_close_matches(
        search_for,
        titles,
        n=3,
        cutoff=0.4
    )
    return [], close_matches


def movie_db_function_search():
    """
    CLI wrapper for searching movies.
    """
    movies = storage.list_movies()
    while True:
        search_for = console.input(print_messages()["input_name"])
        if search_for:
            break
        else:
            console.print(print_messages()["error_not_valid"])
            console.input(print_messages()["continue"])
            return

    exact_matches, close_matches = search_movie_logic(search_for, movies)

    if exact_matches:
        for movie in exact_matches:
            console.print(
                f"[green]{movie}, "
                f"{movies[movie]['rating']} "
                f"({movies[movie]['year']})[/green]"
            )
    else:
        console.print(print_messages()["error_no_movie"])
        if close_matches:
            console.print(print_messages()["similar_movie"])
            for similar_name in close_matches:
                console.print(
                    f"[green] - {similar_name}, "
                    f"{movies[similar_name]['rating']} "
                    f"({movies[similar_name]['year']})[/green]"
                )
        else:
            console.print(print_messages()["error_no_sim_movie"])
    console.input(print_messages()["continue"])


def movie_db_function_sort():
    """
    Displays all movies sorted by rating in descending order and
    alphabetically by title as a secondary criterion. Gets the sorted
    movie list from sort_movies_logic().

    Returns:
        None
    """
    movies = storage.list_movies()
    movies_list = create_movie_list_of_tuples(movies)
    sorted_to_ratings = sort_movies_logic(movies_list)
    for movie in sorted_to_ratings:
        console.print(
            f"[green]{movie[0]}: "
            f"{movie[2]} "
            f"({movie[1]})[/green]"
        )
    console.input(print_messages()["continue"])


def movie_db_function_histo():
    """
    Generates and saves a histogram visualization of movie ratings.

    Returns:
        None
    """
    movies = storage.list_movies()
    if not movies:
        console.print(print_messages()["no_movies_error"])
        console.input(print_messages()["continue"])
        return
    # Brauche hier eine Liste von allen Rankings
    all_rankings_list = [data["rating"] for data in movies.values()]
    # Erstellung Histogramm, skaliert automatisch den x-Achsenbereich,
    # erstellt 10 bins mit 1 Schrittweite
    set_binwidth = list(range(1, 12))
    plt.clf() # Clear current figure to avoid graphical overlay of figures
    plt.hist(all_rankings_list,
             bins=set_binwidth,
             edgecolor="black",
             color="red")
    plt.title("Movie Ranking Histogram")
    plt.xlabel("Ranking distribution")
    plt.ylabel("Frequency")
    # Dateinamen abfragen und das Histogram als .png in den
    # Projektspeicherplatz speichern
    while True:
        file_name = console.input(print_messages()["input_histo_name"])
        if file_name:
            break
        else:
            console.print(print_messages()["error_not_valid"])
    plt.savefig(f"{file_name}.png", dpi=150)
    console.input(print_messages()["continue"])


def generate_movie_grid_html():
    """creates the movie grid HTML snippet"""
    movie_dict = storage.list_movies()
    if not movie_dict:
        console.print(print_messages()["error_db"])
        console.input(print_messages()["continue"])
        return
    movie_grid_template = '''
    <li>
    <div class="movie">
    <img class="movie-poster" src="__poster-url__" title= "Movie poster" alt="No movie poster available">
    <div class="movie-title">__movie-title__</div>
    <div class="movie-year">__movie-year__</div>
    </div>
    </li>
    '''
    html_grid_snippet = ""
    if len(movie_dict) > 0:
        for title, data in movie_dict.items():
            movie_grid_item = movie_grid_template.replace(
                "__poster-url__", data.get("poster", "")
            )
            movie_grid_item = movie_grid_item.replace(
                "__movie-title__", title
            )
            movie_grid_item = movie_grid_item.replace(
                "__movie-year__", str(data["year"])
            )
            html_grid_snippet = html_grid_snippet + " " + movie_grid_item
        return html_grid_snippet
    else:
        return "<li><h3>No Movies in Database available<h3></li>"


def generate_webpage():
    """generates webpage by structuring the procedure of the index.html creation
    """
    pass


def movie_db_function_quit():
    """
    Terminates the application gracefully.

    Returns:
        None
    """
    console.print(print_messages()["exit"])
    sys.exit()


def get_functions_dictionary():
    """Returns functions_dictionary."""
    # Dictionary zum Speichern der Filmtitel und Ratings
    functions_dictionary = {
        "1": movie_db_function_list,
        "2": movie_db_function_add,
        "3": movie_db_function_del,
        "4": movie_db_function_update,
        "5": movie_db_function_stats,
        "6": movie_db_function_random,
        "7": movie_db_function_search,
        "8": movie_db_function_sort,
        "9": movie_db_function_histo,
        "0": movie_db_function_quit,
    }
    return functions_dictionary


def main():
    functions_dictionary = get_functions_dictionary()
    while True:
        choice = start_screen()
        if choice not in functions_dictionary:
            console.print(print_messages()["error_not_valid"])
            continue
        functions_dictionary[choice]()


if __name__ == "__main__":
    main()
