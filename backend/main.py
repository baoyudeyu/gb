from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.auth import router as auth_router
from config.database import init_database
import uvicorn

# 创建FastAPI应用
app = FastAPI(
    title="跟投系统后端API",
    description="跟投系统的后端API服务",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],  # Vue开发服务器地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth_router)

@app.on_event("startup")
async def startup_event():
    """应用启动时初始化数据库"""
    print("正在初始化数据库...")
    init_database()
    print("数据库初始化完成")

@app.get("/")
async def root():
    """根路径"""
    return {"message": "跟投系统后端API服务正在运行", "status": "success"}

@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "message": "服务运行正常"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 