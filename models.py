from sqlalchemy import Column, Integer, String, Text
from database import Base


class Country(Base):
    __tablename__ = "countries"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    capital = Column(String, nullable=False)
    language = Column(String, nullable=False)
    currency = Column(String, nullable=False)
    best_season = Column(String, nullable=True)
    description = Column(Text, nullable=False)
    image_url = Column(String, nullable=True)
