from pydantic import BaseModel
from typing import Dict, Any, Optional, List

class MLPredictionRequest(BaseModel):
    sleep_duration: float
    stress_level: int
    water_intake: float
    screen_time: float
    mood: str
    bright_light: bool
    irregular_meals: bool
    weather_change: bool

class MLPredictionResponse(BaseModel):
    success: bool
    risk_score: int
    risk_level: str
    confidence: float
    probability_distribution: Dict[str, float]
    error: Optional[str] = None

class GeminiRecommendationRequest(BaseModel):
    ml_prediction: Dict[str, Any]
    user_data: Dict[str, Any]

class GeminiRecommendationResponse(BaseModel):
    success: bool
    recommendations: List[str]
    error: Optional[str] = None