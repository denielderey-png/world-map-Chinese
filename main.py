import json
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from database import Base, engine, SessionLocal
from models import Country, City

app = FastAPI(title="Atlas Mundi")
Base.metadata.create_all(bind=engine)
templates = Jinja2Templates(directory="templates")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def country_to_dict(c: Country, with_cities: bool = False):
    data = {
        "id": c.id,
        "name": c.name,
        "capital": c.capital,
        "language": c.language,
        "currency": c.currency,
        "best_season": c.best_season or "",
        "description": c.description,
        "image_url": c.image_url or "",
        "climate": c.climate or "",
        "festivals": c.festivals or "",
        "attractions": c.attractions or "",
        "history": c.history or "",
        "cuisine": c.cuisine or "",
        "culture": c.culture or "",
        "population": c.population or "",
        "area": c.area or "",
        "timezone": c.timezone or "",
        "religion": c.religion or "",
        "politics": c.politics or "",
    }
    if with_cities:
        data["cities"] = [
            {
                "id": city.id,
                "name": city.name,
                "name_en": city.name_en or "",
                "latitude": float(city.latitude),
                "longitude": float(city.longitude),
                "is_capital": bool(city.is_capital),
                "description": city.description or "",
            }
            for city in c.cities
        ]
    return data


@app.get("/")
def home(request: Request, db: Session = Depends(get_db)):
    countries = db.query(Country).all()
    countries_json = json.dumps(
        [country_to_dict(c) for c in countries],
        ensure_ascii=False,
    )
    return templates.TemplateResponse(
        request, "index.html", {"countries_json": countries_json}
    )


@app.get("/api/countries")
def api_countries(db: Session = Depends(get_db)):
    return [country_to_dict(c) for c in db.query(Country).all()]


@app.get("/api/country/{country_id}")
def api_country(country_id: int, db: Session = Depends(get_db)):
    country = db.query(Country).filter(Country.id == country_id).first()
    if not country:
        raise HTTPException(status_code=404, detail="国家未找到")
    return country_to_dict(country, with_cities=True)


@app.get("/api/country/{country_id}/cities")
def api_cities(country_id: int, db: Session = Depends(get_db)):
    country = db.query(Country).filter(Country.id == country_id).first()
    if not country:
        raise HTTPException(status_code=404, detail="国家未找到")
    return [
        {
            "id": city.id,
            "name": city.name,
            "name_en": city.name_en or "",
            "latitude": float(city.latitude),
            "longitude": float(city.longitude),
            "is_capital": bool(city.is_capital),
            "description": city.description or "",
        }
        for city in country.cities
    ]
