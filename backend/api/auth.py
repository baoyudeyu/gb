from fastapi import APIRouter, HTTPException
from models.user import UserCreate, UserLogin, UserResetPassword, UserService

router = APIRouter(prefix="/api/auth", tags=["认证"])

@router.post("/register")
async def register(user_data: UserCreate):
    """用户注册"""
    result = UserService.create_user(user_data)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    
    return {"message": result["message"]}

@router.post("/login")
async def login(login_data: UserLogin):
    """用户登录"""
    result = UserService.login_user(login_data)
    
    if not result["success"]:
        raise HTTPException(status_code=401, detail=result["message"])
    
    return {
        "message": result["message"],
        "user": result["user"]
    }

@router.post("/reset-password")
async def reset_password(reset_data: UserResetPassword):
    """重置密码"""
    result = UserService.reset_password(reset_data)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    
    return {"message": result["message"]}

@router.get("/test")
async def test_connection():
    """测试API连接"""
    return {"message": "API连接正常", "status": "success"} 