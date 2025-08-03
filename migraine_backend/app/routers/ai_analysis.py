from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..dependencies.auth import get_db, get_current_user
from ..models import user as user_model, migraine_entry as entry_model
from ..services import enhanced_öneri_motoru, ml_migraine_predictor

router = APIRouter(prefix="/analysis", tags=["AI Analysis"])

@router.get("/summary/")
def get_ai_summary(db: Session = Depends(get_db), current_user: user_model.User = Depends(get_current_user)):
    entries = db.query(entry_model.MigraineEntry).filter(entry_model.MigraineEntry.user_id == current_user.id).all()

    # En sık tetikleyiciyi hesapla
    trigger_counts = {
     "bright_light": sum(1 for e in entries if e.bright_light),
     "irregular_meals": sum(1 for e in entries if e.irregular_meals),
     "weather_change": sum(1 for e in entries if e.weather_change)
    }
    primary_trigger = max(trigger_counts, key=trigger_counts.get) if any(trigger_counts.values()) else None


    if not entries:
        return {
            "total_entries": 0,
            "recommendations": [],
            "entries_used": 0
        }

    # Son entry üzerinden tahmin yapıyoruz
    last_entry = entries[-1]
    entry_dict = {
        "sleep_duration": last_entry.sleep_duration,
        "stress_level": last_entry.stress_level,
        "water_intake": last_entry.water_intake,
        "screen_time": last_entry.screen_time,
        "mood": last_entry.mood,
        "bright_light": last_entry.bright_light,
        "irregular_meals": last_entry.irregular_meals,
        "weather_change": last_entry.weather_change,
    }

    ml_service = ml_migraine_predictor.ml_service
    prediction_result = ml_service.predict_migraine_risk(entry_dict)

    if not prediction_result.get("success"):
        return {
            "total_entries": len(entries),
            "recommendations": [],
            "error": prediction_result.get("error", "Tahmin yapılamadı")
        }

    recommendations = enhanced_öneri_motoru.get_ml_enhanced_recommendations(
        prediction_result["gemini_context"]
    )

    return {
        "total_entries": len(entries),
        "risk_score": prediction_result["risk_score"],
        "risk_level": prediction_result["risk_level"],
        "confidence": prediction_result["confidence"],
        "recommendations": recommendations,
        "primary_trigger": primary_trigger 
    }

