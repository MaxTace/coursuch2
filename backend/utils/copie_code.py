from models.movie import Movie


def generate_inventory_number(
    db,
    movie_id,
    copy_number
):

    movie = db.query(Movie).filter(
        Movie.id == movie_id
    ).first()

    if not movie:
        raise Exception("Фильм не найден")

    return f"{movie.movie_code}-{copy_number:02}"