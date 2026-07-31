from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.database import engine, Base
from app.models import User, Dish, CookingRecord, CookingStep, AIConfig
from app.routers import auth, dishes, ai, cooking, users, settings, upload

app = FastAPI(title="御膳房 API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(dishes.router, prefix="/api")
app.include_router(ai.router, prefix="/api")
app.include_router(cooking.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(settings.router, prefix="/api")
app.include_router(upload.router, prefix="/api")

# 静态文件服务（上传的图片）
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"msg": "御膳房 API 运行中"}
