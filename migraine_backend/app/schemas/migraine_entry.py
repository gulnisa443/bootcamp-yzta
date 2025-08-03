from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# 🔹 Giriş (kayıt oluşturma) için model
class MigraineEntryCreate(BaseModel):
    sleep_duration: float
    stress_level: int
    water_intake: float
    screen_time: float
    mood: str = Field(alias="ruhHali")
    bright_light: bool = Field(alias="isik")
    irregular_meals: bool = Field(alias="beslenme")
    weather_change: bool = Field(alias="hava")
    note: Optional[str] = None

    model_config = {
        "populate_by_name": True  # alias yerine field adıyla da alabil
    }

# 🔹 Yanıtta (okuma) kullanılan model
class MigraineEntryResponse(BaseModel):
    id: int
    user_id: int
    created_at: datetime
    sleep_duration: float
    stress_level: int
    water_intake: float
    screen_time: float
    ruhHali: str = Field(alias="mood")
    isik: bool = Field(alias="bright_light")
    beslenme: bool = Field(alias="irregular_meals")
    hava: bool = Field(alias="weather_change")
    note: Optional[str] = None

    model_config = {
        "populate_by_name": True,
        "from_attributes": True  # ORM objesinden dönüşü destekler
    }
