"""Data CRUD Layer for sqlite3 DB movie.db"""
from sqlalchemy import create_engine, text, exc

# Define the database URL
DB_URL = "sqlite:///movies.db"

# Create the engine
engine = create_engine(DB_URL, echo=True)

# Create the movies table if it does not exist
with engine.begin() as connection:
    connection.execute(text("""
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT UNIQUE NOT NULL,
            year INTEGER NOT NULL,
            rating REAL NOT NULL,
            poster TEXT
        )
    """))


def list_movies():
    """Retrieve all movies from the database."""
    try:
        with engine.connect() as connection:
            result = connection.execute(text(
                "SELECT title, year, rating, poster FROM movies")
            )
            movies = result.fetchall()
    except exc.SQLAlchemyError as e:
        print(f"Error: {e}")
        return None
    else:
        if len(movies) > 0:
            return {
                row[0]: {"year": row[1],
                         "rating": row[2],
                         "poster": row[3]}
                for row in movies}
        else:
            return None


def add_movie(title, year, rating, poster):
    """Add a new movie to the database."""
    with engine.begin() as connection:
        try:
            connection.execute(
                text(
                    "INSERT INTO movies (title, year, rating, poster) "
                    "VALUES (:title, :year, :rating, :poster)"),
                               {"title": title,
                                "year": year,
                                "rating": rating,
                                "poster": poster})
            print(f"Movie '{title}' added successfully.")
        except exc.SQLAlchemyError as e:
            print(f"Error: {e}")


def delete_movie(title):
    """Delete a movie from the database."""
    with engine.begin() as connection:
        try:
            result = connection.execute(
                text(
                    "DELETE FROM movies "
                    "WHERE title = :title"
                ), {"title": title}
            )
            if result.rowcount == 0:
                print("Movie not found!")
            else:
                print(f"Movie '{title}' successfully deleted")
        except exc.SQLAlchemyError as e:
            print(f"Error: {e}")


def update_movie(title, rating):
    """Update a movie's rating in the database."""
    with engine.begin() as connection:
        try:
            result = connection.execute(
                text(
                    "UPDATE movies "
                    "SET rating = :rating "
                    "WHERE title = :title"
                ), {"rating": rating,
                    "title": title}
            )
            if result.rowcount == 0:
                print("Movie not found!")
            else:
                print(f"Movie '{title}' successfully updated")
        except exc.SQLAlchemyError as e:
            print(f"Error: {e}")
