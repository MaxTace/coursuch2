from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Date
from sqlalchemy import DateTime

from datetime import datetime, timezone

from db import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)

    full_name = Column(String, nullable=False)
    birth_date = Column(Date)

    phone = Column(String)
    email = Column(String)

    registration_date = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))