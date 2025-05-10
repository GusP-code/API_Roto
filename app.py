from fastapi import FastAPI
from config.settings import settings
from routes.api import router as api_router

app = FastAPI(
    title=settings.APP_NAME,
    #debug=settings.DEBUG
)

# Incluir routers
app.include_router(api_router)

@app.get("/")
async def root():
    return {"message": "Bienvenido a API Roto"}


