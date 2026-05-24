from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
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

    # —— 新增详细字段 ——
    climate = Column(Text, nullable=True)         # 气候
    festivals = Column(Text, nullable=True)       # 节日
    attractions = Column(Text, nullable=True)     # 著名景点
    history = Column(Text, nullable=True)         # 历史片段
    cuisine = Column(Text, nullable=True)         # 特色美食
    culture = Column(Text, nullable=True)         # 文化风俗
    population = Column(String, nullable=True)    # 人口
    area = Column(String, nullable=True)          # 国土面积
    timezone = Column(String, nullable=True)      # 时区
    religion = Column(String, nullable=True)      # 主要宗教
    politics = Column(Text, nullable=True)        # 政治体制与对外关系（以中国立场）

    cities = relationship(
        "City", back_populates="country",
        cascade="all, delete-orphan", lazy="selectin"
    )


class City(Base):
    __tablename__ = "cities"

    id = Column(Integer, primary_key=True, index=True)
    country_id = Column(Integer, ForeignKey("countries.id"), nullable=False, index=True)
    name = Column(String, nullable=False)        # 城市名（中文）
    name_en = Column(String, nullable=True)      # 英文名
    latitude = Column(String, nullable=False)    # 纬度
    longitude = Column(String, nullable=False)   # 经度
    is_capital = Column(Integer, default=0)      # 是否首都（1/0）
    description = Column(Text, nullable=True)    # 城市简介

    country = relationship("Country", back_populates="cities")
