import os
import google.generativeai as genai
from dotenv import load_dotenv
from typing import Dict, Any, List

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def generate_ml_enhanced_prompt(ml_context: Dict[str, Any]) -> str:
    """ML tahmin sonuçlarını da içeren geliştirilmiş prompt"""
    
    ml_pred = ml_context.get("ml_prediction", {})
    user_data = ml_context.get("user_data", {})
    
    risk_score = ml_pred.get("risk_score", 0)
    risk_level = ml_pred.get("risk_level", "Bilinmeyen")
    
    return f"""
🤖 GELIŞMIŞ MİGRAİN RİSK ANALİZİ

**ML Model Tahmini:**
- Risk Skoru: {risk_score}/9
- Risk Seviyesi: {risk_level}

**Kullanıcı Verileri:**
- Uyku Süresi: {user_data.get('sleep_duration', 0)} saat
- Stres Seviyesi: {user_data.get('stress_level', 0)}/10
- Su Tüketimi: {user_data.get('water_intake', 0)} litre
- Ekran Süresi: {user_data.get('screen_time', 0)} saat
- Ruh Hali: {user_data.get('mood', 'Bilinmeyen')}
- Parlak Işık: {'Evet' if user_data.get('bright_light') else 'Hayır'}
- Düzensiz Beslenme: {'Evet' if user_data.get('irregular_meals') else 'Hayır'}
- Hava Değişimi: {'Evet' if user_data.get('weather_change') else 'Hayır'}

Bu gelişmiş ML analizi sonuçlarına göre:

1. **Acil Öneriler** (bugün yapılacaklar)
2. **Kısa Vadeli Öneriler** (bu hafta)
3. **Uzun Vadeli Öneriler** (bu ay)

{f"⚠️ YÜKSEK RİSK: Doktor konsültasyonu önerilir!" if risk_score >= 7 else ""}

Her öneriyi kısa, net ve uygulanabilir şekilde ver. Emoji kullanabilirsin.
"""

def get_ml_enhanced_recommendations(ml_context: Dict[str, Any]) -> List[str]:
    """ML destekli gelişmiş öneriler"""
    try:
        prompt = generate_ml_enhanced_prompt(ml_context)
        model = genai.GenerativeModel("models/gemini-1.5-flash")
        response = model.generate_content(prompt)
        
        suggestions = response.text.strip().split("\n")
        return [s.strip("-• ") for s in suggestions if s.strip()]
        
    except Exception as e:
        print(f"Gemini hatası: {e}")
        return [
            "⚠️ AI önerileri şu anda alınamıyor.",
            "Temel öneriler: Bol su için, düzenli uyuyun, stresi azaltın."
        ]

# Mevcut fonksiyonları da koru (geriye uyumluluk için)
def generate_prompt(analysis: dict) -> str:
    """Mevcut basit analiz için prompt"""
    avg = analysis.get("averages", {})
    trigger = analysis.get("primary_trigger", "bilinmiyor")

    return f"""
Son 30 günlük migren günlüğü verileri:

- Ortalama uyku süresi: {avg.get('sleep_duration', 0):.1f} saat
- Ortalama stres seviyesi: {avg.get('stress_level', 0):.1f}/10
- Ortalama su tüketimi: {avg.get('water_intake', 0):.1f} litre
- Ortalama ekran süresi: {avg.get('screen_time', 0):.1f} saat
- En sık tetikleyici: {trigger}

Bu verileri dikkate alarak 2-3 kısa yaşam tarzı önerisi ver. Emoji kullanabilirsin.
"""

def get_gemini_recommendations(analysis: dict) -> List[str]:
    """Mevcut basit analiz için öneriler"""
    prompt = generate_prompt(analysis)
    model = genai.GenerativeModel("models/gemini-1.5-flash")
    response = model.generate_content(prompt)  
    suggestions = response.text.strip().split("\n")
    return [s.strip("-• ") for s in suggestions if s.strip()]