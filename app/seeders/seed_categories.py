"""Seed CATEGORY table with initial sport categories."""
import importlib
from pathlib import Path

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models.category import Category

models_path = Path("/app/app/models")
for file_path in sorted(models_path.rglob("*.py")):
    if file_path.name.startswith("__"):
        continue
    module_name = ".".join(file_path.relative_to(models_path).with_suffix("").parts)
    importlib.import_module(f"app.models.{module_name}")

CATEGORIES = [
    {"name": "Academia",       "description": "Instituciones enfocadas en enseñanza, entrenamiento técnico y formación de atletas."},
    {"name": "Básquet",        "description": "Espacios deportivos para básquet recreativo, entrenamiento profesional y torneos locales."},
    {"name": "Boxeo",          "description": "Gimnasios y arenas especializadas en entrenamiento técnico, amateur y profesional de boxeo."},
    {"name": "Cross Training", "description": "Instalaciones preparadas para entrenamiento funcional, circuitos de fuerza y acondicionamiento físico intensivo."},
    {"name": "Escalada",       "description": "Espacios especializados en muros de escalada, boulder y entrenamiento físico relacionado."},
    {"name": "Fitness",        "description": "Proyectos enfocados en actividad física integral, salud, entrenamiento personalizado y bienestar general."},
    {"name": "Fútbol",         "description": "Proyecto enfocado en el desarrollo de infraestructura, actividades y programas relacionados con la práctica y promoción del fútbol."},
    {"name": "Fútbol 5",       "description": "Proyecto destinado a la construcción, mejora o gestión de canchas e instalaciones para la práctica de fútbol 5 y actividades recreativas deportivas."},
    {"name": "Gimnasio",       "description": "Centros de musculación, fitness y entrenamiento físico orientados al bienestar y alto rendimiento."},
    {"name": "Gym",            "description": "Proyecto orientado al desarrollo y mejora de espacios destinados al entrenamiento físico, la salud y el bienestar de las personas."},
    {"name": "Hockey",         "description": "Proyectos relacionados con canchas de hockey, formación deportiva y eventos regionales."},
    {"name": "Indoor",         "description": "Instalaciones deportivas cubiertas diseñadas para operar durante todo el año independientemente del clima."},
    {"name": "MMA",            "description": "Centros orientados a artes marciales mixtas, entrenamiento físico y preparación competitiva."},
    {"name": "Multideporte",   "description": "Complejos que integran múltiples disciplinas deportivas dentro de un mismo predio."},
    {"name": "Pádel",          "description": "Centros deportivos especializados en pádel, con canchas indoor o outdoor, academias y organización de torneos."},
    {"name": "Parkour",        "description": "Instalaciones adaptadas para entrenamiento y práctica de parkour y freerunning."},
    {"name": "Rugby",          "description": "Infraestructura deportiva enfocada en entrenamiento, competencia y desarrollo de clubes de rugby."},
    {"name": "Skate",          "description": "Parques y pistas diseñadas para skateboarding, BMX y deportes urbanos."},
    {"name": "Tenis",          "description": "Clubes y espacios dedicados al entrenamiento, competencia y recreación vinculada al tenis profesional y amateur."},
]


def seed_categories():
    engine = create_engine(settings.SYNC_DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    try:
        count = 0
        for cat_data in CATEGORIES:
            existing = session.query(Category).filter_by(name=cat_data["name"]).first()
            if not existing:
                session.add(Category(**cat_data))
                count += 1
        session.commit()
        print(f"Seeded {count} new categories (total in list: {len(CATEGORIES)})")
    finally:
        session.close()
        engine.dispose()


if __name__ == "__main__":
    seed_categories()
