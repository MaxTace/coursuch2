from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Float
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey

from sqlalchemy.orm import relationship

from datetime import datetime

from db import Base


class Rental(Base):
    __tablename__ = "rentals"

    id = Column(Integer, primary_key=True, index=True)

    customer_id = Column(Integer, ForeignKey("customers.id"))
    inventory_id = Column(Integer, ForeignKey("movie_copies.inventory_code"))

    issue_date = Column(DateTime, default=datetime.utcnow)
    planned_return_date = Column(DateTime)
    actual_return_date = Column(DateTime, nullable=True)

    rental_days = Column(Integer)

    rental_price = Column(Float)
    deposit = Column(Float)
    penalty = Column(Float, default=0)
    total_price = Column(Float)

    customer = relationship("Customer")
    movie_copy = relationship("MovieCopy")