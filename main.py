import json
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from database import Base, engine, SessionLocal
from models import Country

app = FastAPI(title="Atlas Mundi")
Base.metadata.create_all(bind=engine)
templates = Jinja2Templates(directory="templates")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def home(request: Request, db: Session = Depends(get_db)):
    countries = db.query(Country).all()
    countries_json = json.dumps(
        [
            {
                "id": c.id,
                "name": c.name,
                "capital": c.capital,
                "language": c.language,
                "currency": c.currency,
                "best_season": c.best_season or "",
                "description": c.description,
                "image_url": c.image_url or "",
            }
            for c in countries
        ],
        ensure_ascii=False,
    )
    return templates.TemplateResponse(
        request, "index.html", {"countries_json": countries_json}
    )


@app.get("/api/countries")
def api_countries(db: Session = Depends(get_db)):
    return db.query(Country).all()


@app.get("/api/country/{country_id}")
def api_country(country_id: int, db: Session = Depends(get_db)):
    country = db.query(Country).filter(Country.id == country_id).first()
    if not country:
        raise HTTPException(status_code=404, detail="Страна не найдена")
    return country
