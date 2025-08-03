import os
import joblib
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class MLMigrainePredictionService:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.model_loaded = False
        self.model_path = Path("ml_models/models")
        self.load_model()
    
    def load_model(self):
        """Eğitilmiş modeli ve scaler'ı yükle"""
        try:
            model_file = self.model_path / "trained_migraine_model.pkl"
            scaler_file = self.model_path / "trained_scaler.pkl"
            
            if model_file.exists() and scaler_file.exists():
                self.model = joblib.load(model_file)
                self.scaler = joblib.load(scaler_file)
                self.model_loaded = True
                logger.info("✅ ML modeli başarıyla yüklendi")
            else:
                logger.warning("⚠️ Eğitilmiş model bulunamadı. Önce modeli eğitin.")
                
        except Exception as e:
            logger.error(f"❌ Model yükleme hatası: {e}")
            self.model_loaded = False
    
    def safe_feature_engineering(self, df):
        """Feature engineering işlemleri - orijinal ML kodunuzla aynı"""
        df_eng = df.copy()
        
        # 1. Interaction features
        df_eng['stres_uyku_ratio'] = df_eng['Stres_Seviyesi'] / (df_eng['Uyku_Saati'] + 0.1)
        df_eng['ekran_su_ratio'] = df_eng['Ekran_Suresi_Saat'] / (df_eng['Su_Tuketimi_L'] + 0.1)
        df_eng['ruh_hali_uyku'] = df_eng['Ruh_Hali'] * df_eng['Uyku_Saati']
        
        # 2. Risk kategorileri
        df_eng['uyku_kategori'] = pd.cut(df_eng['Uyku_Saati'], 
                                        bins=[0, 6, 8, 12], 
                                        labels=[2, 1, 0]).astype(int)
        
        df_eng['stres_kategori'] = pd.cut(df_eng['Stres_Seviyesi'], 
                                         bins=[0, 3, 7, 10], 
                                         labels=[0, 1, 2]).astype(int)
        
        # 3. Composite risk scores
        df_eng['lifestyle_risk'] = (
            (df_eng['Stres_Seviyesi'] / 10) * 0.3 +
            ((10 - df_eng['Uyku_Saati']) / 10) * 0.2 +
            (df_eng['Ekran_Suresi_Saat'] / 16) * 0.2 +
            ((5 - df_eng['Su_Tuketimi_L']) / 5) * 0.15 +
            ((5 - df_eng['Ruh_Hali']) / 5) * 0.15
        )
        
        # 4. Boolean features'ı sayısal yap
        df_eng['Parlak_Isik'] = df_eng['Parlak_Isik'].astype(int)
        df_eng['Beslenme_Duzensizligi'] = df_eng['Beslenme_Duzensizligi'].astype(int)
        df_eng['Hava_Degisimi'] = df_eng['Hava_Degisimi'].astype(int)
        
        return df_eng
    
    def convert_mood_to_numeric(self, mood: str) -> int:
        """Mood string'ini sayıya çevir"""
        mood_map = {"Kötü": 1, "Orta": 3, "İyi": 5}
        return mood_map.get(mood, 3)
    
    def predict_migraine_risk(self, entry_data: Dict[str, Any]) -> Dict[str, Any]:
        """Migrain riskini tahmin et - FastAPI schema'sına uygun"""
        
        if not self.model_loaded:
            return {
                'success': False,
                'error': 'Model yüklenmedi. Lütfen önce modeli eğitin.',
                'risk_score': 0,
                'risk_level': 'unknown'
            }
        
        try:
            # FastAPI schema'sından ML formatına çevir
            mood_numeric = self.convert_mood_to_numeric(entry_data.get('mood', 'Orta'))
            
            # ML modeli için veri formatı
            input_df = pd.DataFrame([{
                'Uyku_Saati': entry_data.get('sleep_duration', 7),
                'Stres_Seviyesi': entry_data.get('stress_level', 5),
                'Su_Tuketimi_L': entry_data.get('water_intake', 2),
                'Ekran_Suresi_Saat': entry_data.get('screen_time', 8),
                'Ruh_Hali': mood_numeric,
                'Parlak_Isik': entry_data.get('bright_light', False),
                'Beslenme_Duzensizligi': entry_data.get('irregular_meals', False),
                'Hava_Degisimi': entry_data.get('weather_change', False)
            }])
            
            # Feature engineering
            processed_df = self.safe_feature_engineering(input_df)
            
            # Scaling
            scaled_features = self.scaler.transform(processed_df)
            
            # Tahmin
            prediction = self.model.predict(scaled_features)[0]
            probability = self.model.predict_proba(scaled_features)[0]
            
            # Risk seviyesi belirleme
            risk_levels = {
                0: 'Çok Düşük', 1: 'Düşük', 2: 'Düşük-Orta', 
                3: 'Orta', 4: 'Orta-Yüksek', 5: 'Yüksek',
                6: 'Çok Yüksek', 7: 'Kritik', 8: 'Kritik+', 9: 'Maksimum'
            }
            
            return {
                'success': True,
                'risk_score': int(prediction),
                'risk_level': risk_levels.get(prediction, 'Bilinmeyen'),
                'confidence': float(max(probability)),
                'probability_distribution': {
                    str(i): float(prob) for i, prob in enumerate(probability)
                },
                'gemini_context': self._prepare_gemini_context(prediction, risk_levels.get(prediction, 'Bilinmeyen'), entry_data)
            }
            
        except Exception as e:
            logger.error(f"ML Tahmin hatası: {e}")
            return {
                'success': False,
                'error': str(e),
                'risk_score': 0,
                'risk_level': 'unknown'
            }
    
    def _prepare_gemini_context(self, risk_score: int, risk_level: str, entry_data: Dict) -> Dict:
        """Gemini API için context hazırla - mevcut öneri_motoru formatına uygun"""
        return {
            'ml_prediction': {
                'risk_score': risk_score,
                'risk_level': risk_level
            },
            'user_data': {
                'sleep_duration': entry_data.get('sleep_duration', 7),
                'stress_level': entry_data.get('stress_level', 5),
                'water_intake': entry_data.get('water_intake', 2),
                'screen_time': entry_data.get('screen_time', 8),
                'mood': entry_data.get('mood', 'Orta'),
                'bright_light': entry_data.get('bright_light', False),
                'irregular_meals': entry_data.get('irregular_meals', False),
                'weather_change': entry_data.get('weather_change', False)
            }
        }

# Global servis instance
ml_service = MLMigrainePredictionService()