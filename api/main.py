from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers import (
    auth_router, news_router, games_router,
    favorites_router, sources_router, users_router,
)

app = FastAPI(
    title="GameNews API",
    description="REST API с полным CRUD",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(news_router.router)
app.include_router(games_router.router)
app.include_router(favorites_router.router)
app.include_router(sources_router.router)
app.include_router(users_router.router)

@app.get("/")
def root():
    return {"name": "GameNews API", "docs": "/docs", "version": "2.0.0"}