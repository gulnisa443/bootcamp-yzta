import google.generativeai as genai
import os
from dotenv import load_dotenv

# .env dosyasındaki API anahtarını yükle
load_dotenv()

# Gemini API anahtarını yapılandır
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Kullanılabilir modelleri listele
models = genai.list_models()

# Model adlarını yazdır
for model in models:
    print(model.name)
