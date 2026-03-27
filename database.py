from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, registry
from dotenv import load_dotenv
import os

# Carrega variáveis do .env
load_dotenv()

# Configuração MySQL 8 - lê do arquivo .env
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "mercearia")

engine = create_engine(
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
    pool_pre_ping=True,  # Verifica conexão antes de usar
    pool_recycle=3600,   # Recicla conexões a cada hora
    echo=False           # Mude para True para ver queries SQL
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# usando registry para melhor controle
mapper_registry = registry()
Base = mapper_registry.generate_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()