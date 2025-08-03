import os
from dotenv import load_dotenv

print("🔥 ENV yükleniyor...")

# .env dosyasının yolunu elle belirle
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(BASE_DIR, ".env")

print("📂 ENV PATH:", ENV_PATH)

# .env dosyasını yükle
load_dotenv(dotenv_path=ENV_PATH)

# Ortam değişkenini al
DATABASE_URL = os.getenv("DATABASE_URL")
print("🧪 DATABASE_URL:", DATABASE_URL)

# SQLAlchemy için gerekli importlar
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Veritabanı bağlantısı
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# Model tanımlarında kullanılacak temel sınıf
Base = declarative_base()
