"""
Codio Project: My Movies Database – Extended CLI Application

This module implements a menu-driven command-line application for
managing a personal movie database as a MasterSchool project.

The application supports full CRUD functionality (Create, Read,
Update, Delete) as well as analytical and visualization features.
Each movie is represented as a dictionary containing the following
attributes:

    - title (str): The movie title
    - rating (float): The user-defined rating (1–10)
    - year (int): The release year

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

import difflib
import random
import statistics

import matplotlib.pyplot as plt
from rich.console import Console
from rich.panel import Panel


console = Console()  # fits nicer in snake_case


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
    console.print(Panel(
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


def movie_db_function_list(movies):
    """
    Displays all movies stored in the database.

    Args:
        movies (list[dict]): The movie database.

    Returns:
        None
    """
    print(f"\n{len(movies)} movies in total")
    for movie in movies:
        print(f"{movie['title']}: {movie['rating']} ({movie['year']})")
    console.input("\n[dim]Press enter to continue[/dim]")


def movie_db_function_add(movies):
    """
    Prompts the user to enter a new movie and appends it to the database.

    Args:
        movies (list[dict]): The movie database.

    Returns:
        list[dict]: The updated movie database.
    """
    new_movie_name = input("\nEnter new movie name: ")
    new_movie_rating_float = float(input("Enter new movie rating(0-10): "))
    new_movie_year = int(input("Enter release year: "))
    if 1 <= new_movie_rating_float <= 10:
        movies.append({
            "title": new_movie_name,
            "rating": new_movie_rating_float,
            "year": new_movie_year
        })
        console.input("\n[dim]Press enter to continue[/dim]")
        return movies
    else:
        print(f"Rating {new_movie_rating_float} is invalid")
        console.input("\n[dim]Press enter to continue[/dim]")
        return movies


def movie_db_function_del(movies):
    """
    Removes a movie from the database by its title.

    Args:
        movies (list[dict]): The movie database.

    Returns:
        list[dict]: The updated movie database.
    """
    movie_to_del = input("\nEnter movie name to delete: ")
    for movie in movies:
        if movie["title"] == movie_to_del:
            movies.remove(movie)
            print(f"Movie {movie_to_del} successfully deleted")
            return movies
    else:
        print(f"Movie {movie_to_del} doesn't exist!")
        return movies


def movie_db_function_update(movies):
    """
    Updates the rating of an existing movie in the database.

    Args:
        movies (list[dict]): The movie database.

    Returns:
        list[dict]: The updated movie database.
    """
    movie_to_update = input("\nEnter movie name: ")
    for movie in movies:
        if movie["title"] == movie_to_update:
            new_rating = float(input("Enter new movie rating (1-10): "))
            if 1 <= new_rating <= 10:
                movie["rating"] = new_rating
                print(f"Movie {movie_to_update} successfully updated")
                return movies
            else:
                print(f"Rating {new_rating} is invalid")
                return movies
    else:
        print(f"Movie {movie_to_update} doesn't exist!")
        return movies


def movie_db_function_stats(movies):
    """
    Calculates and displays statistical insights about the movie ratings,
    including average, median, highest-rated, and lowest-rated movies.

    Args:
        movies (list[dict]): The movie database.

    Returns:
        None
    """
    average_rating = statistics.mean(movie["rating"] for movie in movies)
    median_rating = statistics.median(movie["rating"] for movie in movies)
    print(f"Average rating: {average_rating:.2f}")
    print(f"Median rating: {median_rating}")
    sorted_to_ratings = sorted(
        movies,
        key=lambda m: (m["rating"], m["title"]),
        reverse=True
    )
    best_movie = sorted_to_ratings[0]
    worst_movie = sorted_to_ratings[-1]

    print(f"Best movie: {best_movie['title']}, {best_movie['rating']}")
    print(f"Worst movie: {worst_movie['title']}, {worst_movie['rating']}")
    console.input("\n[dim]Press enter to continue[/dim]")


def movie_db_function_random(movies):
    """
    Selects and displays a random movie from the database.

    Args:
        movies (list[dict]): The movie database.

    Returns:
        None
    """
    random_movie = random.choice(movies)
    print(
        f"\nYour movie for tonight: {random_movie['title']}, "
        f"it's rated {random_movie['rating']} ({random_movie['year']})"
    )
    console.input("\n[dim]Press enter to continue[/dim]")


def movie_db_function_search(movies):
    """
    Searches for a movie by partial title match. If no direct match is found,
    suggests similar titles using fuzzy matching.

    Args:
        movies (list[dict]): The movie database.

    Returns:
        None
    """
    # zum Fuzzy Matching
    what_to_search = input("\nEnter part of movie name: ").lower()
    # normale Suche
    found_any = False
    for movie in movies:
        if what_to_search in movie["title"].lower():
            print(f"{movie['title']}, {movie['rating']} ({movie['year']})")
            found_any = True
    if found_any:
        console.input("\n[dim]Press enter to continue[/dim]")
        return
    # nun zum Fuzzy Matching, falls die Normale suche nicht ergeben hat
    print("\nMovie not found!")
    # Mit der get_close_matches-Funktion von difflib ähnliche Einträge
    # in movielist finden und als Liste ausgeben
    # Fuzzy Matching vorbereiten mit einer Liste von Filmtiteln:
    movie_titles = [movie["title"] for movie in movies]
    close_matches = difflib.get_close_matches(
        what_to_search,
        movie_titles,
        # Anzahl der maximalen Ausgabe ähnlicher Filmnamen
        n=3,
        # Sensitivtät der Suche 0.1 → können total unterschiedlich sein,
        # 1 → Müssen exakt gleich sein
        cutoff=0.4
    )
    if close_matches:
        print("Similar movies found:")
        print(close_matches)
        for similar_name in close_matches:
            for movie in movies:
                if movie["title"] == similar_name:
                    print(f"  - {movie['title']}, "
                          f"{movie['rating']} "
                          f"({movie['year']})"
                          )
    else:
        print("No similar movies found.")
    console.input("\n[dim]Press enter to continue[/dim]")


def movie_db_function_sort(movies):
    """
    Displays all movies sorted by rating in descending order and
    alphabetically by title as a secondary criterion.

    Args:
        movies (list[dict]): The movie database.

    Returns:
        None
    """
    sorted_to_ratings = sorted(
        movies,
        key=lambda m: (-m["rating"], m["title"])
    )
    for movie in sorted_to_ratings:
        print(f"{movie['title']}: {movie['rating']} ({movie['year']})")
    console.input("\n[dim]Press enter to continue[/dim]")


def movie_db_function_histo(movies):
    """
    Generates and saves a histogram visualization of movie ratings.

    Args:
        movies (list[dict]): The movie database.

    Returns:
        None
    """
    # Brauche hier eine Liste von allen Rankings
    all_rankings_list = [movie["rating"] for movie in movies]
    # Erstellung Histogramm, skaliert automatisch den x-Achsenbereich,
    # erstellt 10 bins mit 1 Schrittweite
    set_binwidth = list(range(1, 10))
    plt.hist(all_rankings_list,
             bins=set_binwidth,
             edgecolor="black",
             color="red")
    plt.title("Movie Ranking Histogram")
    plt.xlabel("Ranking distribution")
    plt.ylabel("Frequency")
    # Dateinamen abfragen und das Histogram als .png in den
    # Projektspeicherplatz speichern
    file_name = input("\nPlease enter the filename for the histogram: ")
    plt.savefig(f"{file_name}.png", dpi=150)
    console.input("\n[dim]Press enter to continue[/dim]")


def movie_db_function_quit(_):
    """
    Terminates the application gracefully.

    Args:
        _ (list[dict]): Unused parameter to maintain consistent function
        signature.

    Returns:
        None
    """
    console.print("[bold red]Exiting My Movies Database... Goodbye![/bold red]")
    exit()


def main():
    # Dictionary zum Speichern der Filmtitel und Ratings
    movies = [
        {"title": "The Shawshank Redemption", "rating": 9.5, "year": 1994},
        {"title": "Pulp Fiction", "rating": 8.8, "year": 1994},
        {"title": "The Room", "rating": 3.6, "year": 2003},
        {"title": "The Godfather", "rating": 9.2, "year": 1972},
        {"title": "The Godfather: Part II", "rating": 9.0, "year": 1974},
        {"title": "The Dark Knight", "rating": 9.0, "year": 2008},
        {"title": "12 Angry Men", "rating": 8.9, "year": 1957},
        {"title": "Everything Everywhere All At Once", "rating": 8.9,
         "year": 2022},
        {"title": "Forrest Gump", "rating": 8.8, "year": 1994},
        {"title": "Star Wars: Episode V", "rating": 8.7, "year": 1980},
    ]
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
    while True:
        choice = start_screen()
        try:
            function_choice = functions_dictionary[choice]
            function_choice(movies)
        except KeyError:
            console.print("[red]Not a valid entry! Please choose again.[/red]")


if __name__ == "__main__":
    main()
