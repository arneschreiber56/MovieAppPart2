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


def add_movie_logic(title, rating, year, movies):
    """Add a new movie to the list. Returns updated movies list."""
    if 1 <= rating <= 10:
        movies.append({"title": title, "rating": rating, "year": year})
    return movies


def movie_db_function_add(movies):
    """CLI wrapper to add a movie with user input."""
    title = input("\nEnter new movie name: ")
    rating = float(input("Enter new movie rating(0-10): "))
    year = int(input("Enter release year: "))
    movies = add_movie_logic(title, rating, year, movies)
    console.input("\n[dim]Press enter to continue[/dim]")
    return movies


def delete_movie_logic(title, movies):
    """Delete a movie by title. Returns updated movies list and success flag."""
    for movie in movies:
        if movie["title"] == title:
            movies.remove(movie)
            return movies, True
    return movies, False


def movie_db_function_del(movies):
    """CLI wrapper to delete a movie."""
    title = input("\nEnter movie name to delete: ")
    movies, success = delete_movie_logic(title, movies)
    if success:
        print(f"Movie {title} successfully deleted")
    else:
        print(f"Movie {title} doesn't exist!")
    console.input("\n[dim]Press enter to continue[/dim]")
    return movies


def update_movie_logic(title, new_rating, movies):
    """Update the rating of a movie. Returns updated movies list
    and success flag."""
    for movie in movies:
        if movie["title"] == title:
            if 1 <= new_rating <= 10:
                movie["rating"] = new_rating
                return movies, True
            return movies, False
    return movies, None  # Movie not found


def movie_db_function_update(movies):
    """CLI wrapper to update a movie rating."""
    title = input("\nEnter movie name: ")
    new_rating = float(input("Enter new movie rating (1-10): "))
    movies, success = update_movie_logic(title, new_rating, movies)
    if success:
        print(f"Movie {title} successfully updated")
    elif not success:
        print(f"Rating {new_rating} is invalid")
    else:
        print(f"Movie {title} doesn't exist!")
    console.input("\n[dim]Press enter to continue[/dim]")
    return movies


def sort_movies_logic(movies):
    """Return movies sorted by rating descending and title ascending."""
    sorted_to_ratings = sorted(
        movies,
        key=lambda m: (-m["rating"], m["title"])
    )
    return sorted_to_ratings


def stats_logic(movies):
    """Compute average, median, best and worst movies. Gets sorted movie list
    from sort_movies_logic()"""
    ratings = [movie["rating"] for movie in movies]
    avg = statistics.mean(ratings)
    med = statistics.median(ratings)

    sorted_movies = sort_movies_logic(movies)
    best_movies = []
    worst_movies = []
    for movie in sorted_movies:
        if movie["rating"] == sorted_movies[0]["rating"]:
            best_movies.append(movie)
        elif movie["rating"] == sorted_movies[-1]["rating"]:
            worst_movies.append(movie)

    return avg, med, best_movies, worst_movies


def movie_db_function_stats(movies):
    """CLI wrapper to display stats."""
    avg, med, best, worst = stats_logic(movies)
    print(f"Average rating: {avg:.2f}")
    print(f"Median rating: {med}")
    for movie in best:
        print(f"Best movie: {movie['title']}, {movie['rating']}")
    for movie in worst:
        print(f"Worst movie: {movie['title']}, {movie['rating']}")
    console.input("\n[dim]Press enter to continue[/dim]")


def get_random_logic(movies):
    """Select a random movie dictionary from the list of movies
    and returns it."""
    random_movie = random.choice(movies)
    return random_movie


def movie_db_function_random(movies):
    """
    Displays a random movie from the database selected by random_logic().

    Args:
        movies (list[dict]): The movie database.

    Returns:
        None
    """
    random_movie = get_random_logic(movies)
    print(
        f"\nYour movie for tonight: {random_movie['title']}, "
        f"it's rated {random_movie['rating']} ({random_movie['year']})"
    )
    console.input("\n[dim]Press enter to continue[/dim]")


def search_movie_logic(what_to_search, movies):
    """
    Search for movies by partial title match and fuzzy similarity.

    Args:
        search_term (str): The term to search for.
        movies (list[dict]): The movie database.

    Returns:
        tuple:
            - list[dict]: Exact/partial matches
            - list[str]: Similar movie titles (fuzzy matches)
    """
    what_to_search = what_to_search.lower()
    # Normal partial match
    exact_matches = [
        movie for movie in movies
        if what_to_search in movie["title"].lower()
    ]
    if exact_matches:
        return exact_matches, []
    # Fuzzy matching
    movie_titles = [movie["title"] for movie in movies]
    close_matches = difflib.get_close_matches(
        what_to_search,
        movie_titles,
        n=3,
        cutoff=0.4
    )

    return [], close_matches


def movie_db_function_search(movies):
    """
    CLI wrapper for searching movies.
    """
    what_to_search = input("\nEnter part of movie name: ")
    exact_matches, close_matches = search_movie_logic(what_to_search, movies)

    if exact_matches:
        for movie in exact_matches:
            print(f"{movie['title']}, {movie['rating']} ({movie['year']})")
    else:
        print("\nMovie not found!")
        if close_matches:
            print("Similar movies found:")
            for similar_name in close_matches:
                for movie in movies:
                    if movie["title"] == similar_name:
                        print(
                            f"  - {movie['title']}, "
                            f"{movie['rating']} "
                            f"({movie['year']})"
                        )
        else:
            print("No similar movies found.")
    console.input("\n[dim]Press enter to continue[/dim]")


def movie_db_function_sort(movies):
    """
    Displays all movies sorted by rating in descending order and
    alphabetically by title as a secondary criterion. Gets sorted
    movie list from sort_movies_logic().

    Args:
        movies (list[dict]): The movie database.

    Returns:
        None
    """
    sorted_to_ratings = sort_movies_logic(movies)
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
