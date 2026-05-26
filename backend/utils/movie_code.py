from models.movie import Movie
from models.category import Category


def generate_movie_code(db, category_id):

    category = db.query(Category).filter(
        Category.id == category_id
    ).first()

    movies_count = db.query(Movie).filter(
        Movie.category_id == category_id
    ).count()

    next_number = movies_count + 1

    return f"{category.code}-{next_number:03}"