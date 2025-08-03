from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..schemas.migraine_entry import MigraineEntryCreate, MigraineEntryResponse
from ..crud import migraine_entry as crud
from ..dependencies.auth import get_db, get_current_user
from ..models.user import User
from typing import List
from ..schemas.ml_prediction import MLPredictionRequest, MLPredictionResponse, GeminiRecommendationRequest
from ..services.ml_migraine_predictor import ml_service
from ..services import enhanced_öneri_motoru

router = APIRouter(tags=["migraine"])


@router.post("/", response_model=MigraineEntryResponse)
def create_migraine_entry(
    entry: MigraineEntryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    print("current_user:", current_user, type(current_user))
    print("current_user.id:", getattr(current_user, "id", None), type(getattr(current_user, "id", None)))
    user_id = getattr(current_user, "id", None)
    if user_id is None:
        raise HTTPException(status_code=401, detail="User id is None")
    if not isinstance(user_id, int):
        user_id = int(user_id)
    return crud.create_entry(db=db, user_id=user_id, entry=entry)


@router.get("/", response_model=List[MigraineEntryResponse])
def read_user_entries(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    print("current_user:", current_user, type(current_user))
    print("current_user.id:", getattr(current_user, "id", None), type(getattr(current_user, "id", None)))
    user_id = getattr(current_user, "id", None)
    if user_id is None:
        raise HTTPException(status_code=401, detail="User id is None")
    if not isinstance(user_id, int):
        user_id = int(user_id)
    return crud.get_entries_by_user(db=db, user_id=user_id)

@router.get("/{entry_id}", response_model=MigraineEntryResponse)
def read_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    print("current_user:", current_user, type(current_user))
    print("current_user.id:", getattr(current_user, "id", None), type(getattr(current_user, "id", None)))
    user_id = getattr(current_user, "id", None)
    if user_id is None:
        raise HTTPException(status_code=401, detail="User id is None")
    if not isinstance(user_id, int):
        user_id = int(user_id)
    entry = crud.get_entry_by_id(db, user_id, entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    return entry

@router.put("/{entry_id}", response_model=MigraineEntryResponse)
def update_entry(
    entry_id: int,
    entry: MigraineEntryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    print("current_user:", current_user, type(current_user))
    print("current_user.id:", getattr(current_user, "id", None), type(getattr(current_user, "id", None)))
    user_id = getattr(current_user, "id", None)
    if user_id is None:
        raise HTTPException(status_code=401, detail="User id is None")
    if not isinstance(user_id, int):
        user_id = int(user_id)
    updated = crud.update_entry(db, user_id, entry_id, entry)
    if not updated:
        raise HTTPException(status_code=404, detail="Entry not found")
    return updated

@router.delete("/{entry_id}", response_model=MigraineEntryResponse)
def delete_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    print("current_user:", current_user, type(current_user))
    print("current_user.id:", getattr(current_user, "id", None), type(getattr(current_user, "id", None)))
    user_id = getattr(current_user, "id", None)
    if user_id is None:
        raise HTTPException(status_code=401, detail="User id is None")
    if not isinstance(user_id, int):
        user_id = int(user_id)
    deleted = crud.delete_entry(db, user_id, entry_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Entry not found")
    return deleted

@router.get("/recent/", response_model=List[MigraineEntryResponse])
def get_recent_entries(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    print("current_user:", current_user, type(current_user))
    print("current_user.id:", getattr(current_user, "id", None), type(getattr(current_user, "id", None)))
    user_id = getattr(current_user, "id", None)
    if user_id is None:
        raise HTTPException(status_code=401, detail="User id is None")
    if not isinstance(user_id, int):
        user_id = int(user_id)
    return crud.get_recent_entries(db, user_id, days)

@router.get("/summary/")
def get_entries_summary(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    print("current_user:", current_user, type(current_user))
    print("current_user.id:", getattr(current_user, "id", None), type(getattr(current_user, "id", None)))
    user_id = getattr(current_user, "id", None)
    if user_id is None:
        raise HTTPException(status_code=401, detail="User id is None")
    if not isinstance(user_id, int):
        user_id = int(user_id)
    entries = crud.get_recent_entries(db, user_id, days)
    return crud.get_entries_summary(entries)
@router.post("/predict-ml-risk", response_model=MLPredictionResponse)
def predict_migraine_risk_ml(
    prediction_data: MLPredictionRequest,
    current_user: User = Depends(get_current_user)
):
    """ML modeli ile migrain riski tahmini"""
    try:
        # Pydantic model'i dict'e çevir
        entry_data = prediction_data.model_dump()
        
        # ML servisini kullanarak tahmin yap
        prediction_result = ml_service.predict_migraine_risk(entry_data)
        
        if prediction_result['success']:
            return MLPredictionResponse(
                success=True,
                risk_score=prediction_result['risk_score'],
                risk_level=prediction_result['risk_level'],
                confidence=prediction_result['confidence'],
                probability_distribution=prediction_result['probability_distribution']
            )
        else:
            return MLPredictionResponse(
                success=False,
                risk_score=0,
                risk_level='unknown',
                confidence=0.0,
                probability_distribution={},
                error=prediction_result.get('error', 'Tahmin yapılamadı')
            )
            
    except Exception as e:
        return MLPredictionResponse(
            success=False,
            risk_score=0,
            risk_level='unknown',
            confidence=0.0,
            probability_distribution={},
            error=f'Sunucu hatası: {str(e)}'
        )

@router.post("/get-ml-recommendations")
def get_ml_enhanced_recommendations(
    recommendation_request: GeminiRecommendationRequest,
    current_user: User = Depends(get_current_user)
):
    """ML tahmin sonuçlarına göre Gemini önerileri"""
    try:
        # ML context'i hazırla
        ml_context = recommendation_request.model_dump()
        
        # Gemini'den gelişmiş öneriler al
        recommendations = enhanced_öneri_motoru.get_ml_enhanced_recommendations(ml_context)
        
        return {
            "success": True,
            "recommendations": recommendations
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f'Öneri alma hatası: {str(e)}',
            "recommendations": []
        }

@router.post("/train-model")
def train_ml_model(
    current_user: User = Depends(get_current_user)
):
    """ML modelini eğit (admin için)"""
    try:
        import subprocess
        import os
        
        # ML model eğitim scriptini çalıştır
        result = subprocess.run(
            ['python', 'ml_models/migren_ml_model.py'],
            cwd=os.getcwd(),
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            # Modeli yeniden yükle
            ml_service.load_model()
            
            return {
                "success": True,
                "message": "Model başarıyla eğitildi ve yüklendi"
            }
        else:
            return {
                "success": False,
                "message": f"Model eğitimi başarısız: {result.stderr}"
            }
            
    except Exception as e:
        return {
            "success": False,
            "message": f"Eğitim hatası: {str(e)}"
        }