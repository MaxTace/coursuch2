from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import ForeignKey

from sqlalchemy.orm import relationship

from db import Base


class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    director = Column(String, nullable=False)
    actors = Column(Text)
    country = Column(String)
    release_year = Column(Integer)
    age_rating = Column(Integer)
    description = Column(Text)
    dubbing_languages = Column(Text)
    price = Column(Integer, nullable=False)
    category_id = Column(Integer,ForeignKey("categories.id"))
    movie_code = Column(String,unique=True,nullable=False)
    previous_movie_id = Column(Integer,ForeignKey("movies.id"),nullable=True)
    category = relationship("Category")
    copies = relationship( "MovieCopy",back_populates="movie")
    previous_movie = relationship("Movie", remote_side=[id], foreign_keys=[previous_movie_id])