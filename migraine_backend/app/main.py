from fastapi import FastAPI
from fastapi.openapi.models import APIKey, APIKeyIn, SecuritySchemeType
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware


from .routers import migraine_entry
from .routers import auth
from .routers import user
from .routers import ai_analysis
from dotenv import load_dotenv
load_dotenv()


app = FastAPI()


# CORS middleware ekle
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Geliştirme için tüm originlere izin ver
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth")
app.include_router(user.router, tags=["users"])
app.include_router(migraine_entry.router, prefix="/entries", tags=["migraine"])
app.include_router(ai_analysis.router)

# ↓ Swagger arayüzüne Bearer Auth butonu ekleyen fonksiyon
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Migraine App API",
        version="0.1.0",
        description="Bu API ile kullanıcı kayıt, giriş ve daha fazlası yapılabilir.",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            openapi_schema["paths"][path][method]["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
