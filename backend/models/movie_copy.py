from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import ForeignKey

from sqlalchemy.orm import relationship

from db import Base


class MovieCopy(Base):
    __tablename__ = "movie_copies"

    id = Column(Integer, primary_key=True, index=True)

    movie_id = Column(Integer, ForeignKey("movies.id"))
    
    inventory_code = Column(String, unique=True, nullable=False)
    media_type = Column(String)
    status = Column(String, default="available")

    movie = relationship("Movie", back_populates="copies")