from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base

class MigraineEntry(Base):
    __tablename__ = "migraine_entries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    sleep_duration = Column(Float)
    stress_level = Column(Integer)
    water_intake = Column(Float)
    screen_time = Column(Float)
    mood = Column(String)

    bright_light = Column(Boolean, default=False)
    irregular_meals = Column(Boolean, default=False)
    weather_change = Column(Boolean, default=False)

    note = Column(String)

    user = relationship("User", back_populates="migraine_entries")
