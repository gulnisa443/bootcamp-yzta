from sqlalchemy.orm import Session
from ..models.migraine_entry import MigraineEntry
from ..schemas.migraine_entry import MigraineEntryCreate
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta


def create_entry(db: Session, user_id: int, entry: MigraineEntryCreate):
    db_entry = MigraineEntry(**entry.model_dump(by_alias=False), user_id=user_id)
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry


def get_entries_by_user(db: Session, user_id: int):
    return db.query(MigraineEntry).filter(MigraineEntry.user_id == user_id).all()


def get_entry_by_id(db: Session, user_id: int, entry_id: int) -> Optional[MigraineEntry]:
    return db.query(MigraineEntry).filter(MigraineEntry.user_id == user_id, MigraineEntry.id == entry_id).first()


def update_entry(db: Session, user_id: int, entry_id: int, entry: MigraineEntryCreate):
    db_entry = get_entry_by_id(db, user_id, entry_id)
    if not db_entry:
        return None
    for field, value in entry.dict().items():
        setattr(db_entry, field, value)
    db.commit()
    db.refresh(db_entry)
    return db_entry


def delete_entry(db: Session, user_id: int, entry_id: int):
    db_entry = get_entry_by_id(db, user_id, entry_id)
    if not db_entry:
        return None
    db.delete(db_entry)
    db.commit()
    return db_entry

def get_recent_entries(db: Session, user_id: int, days: int = 30):
    since_date = datetime.utcnow() - timedelta(days=days)
    return db.query(MigraineEntry).filter(
        MigraineEntry.user_id == user_id,
        MigraineEntry.created_at >= since_date
    ).all()

def get_entries_summary(entries: List[MigraineEntry]) -> Dict[str, Any]:
    if not entries:
        return {
            "message": "Henüz veri girişi yapılmamış.",
            "recommendations": ["Günlük giriş yapmaya başlayın"]
        }
    count = len(entries)
    avg = lambda field: sum(getattr(e, field) or 0 for e in entries) / count
    averages = {
        "stress_level": avg("stress_level"),
        "sleep_duration": avg("sleep_duration"),
        "water_intake": avg("water_intake"),
        "screen_time": avg("screen_time")
    }
    triggers = {
        "bright_light": sum(1 for e in entries if getattr(e, "bright_light", False)),
        "irregular_meals": sum(1 for e in entries if getattr(e, "irregular_meals", False)),
        "weather_change": sum(1 for e in entries if getattr(e, "weather_change", False))
    }
    # triggers sözlüğünde en yüksek değere sahip anahtarı bul
    primary_trigger = max(triggers, key=lambda k: triggers[k])
    recommendations = []
    if averages["stress_level"] > 7:
        recommendations.append("Stres yönetimi teknikleri uygulayın (meditasyon, nefes egzersizleri)")
    if averages["sleep_duration"] < 7:
        recommendations.append("Uyku sürenizi artırın (günde 7-9 saat)")
    if averages["water_intake"] < 2:
        recommendations.append("Su tüketiminizi artırın (günde en az 2 litre)")
    if averages["screen_time"] > 6:
        recommendations.append("Ekran sürenizi azaltın ve mavi ışık filtresi kullanın")
    trigger_names = {
        "bright_light": "parlak ışık",
        "irregular_meals": "düzensiz beslenme",
        "weather_change": "hava değişikliği"
    }
    if triggers[primary_trigger] > 0:
        recommendations.append(f"{trigger_names[primary_trigger]} tetikleyicisini kontrol altına alın")
    if not recommendations:
        recommendations.append("Mevcut düzeninizi koruyun")
    return {
        "averages": averages,
        "triggers": triggers,
        "primary_trigger": primary_trigger,
        "primary_trigger_count": triggers[primary_trigger],
        "recommendations": recommendations,
        "total_entries": count
    }
