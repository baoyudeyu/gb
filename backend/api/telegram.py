from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from models.telegram import TelegramLogin, TelegramVerify, TelegramService
from models.user import UserService
import asyncio

router = APIRouter(prefix="/api/telegram", tags=["Telegram"])
security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """获取当前用户信息（简化版本，实际应该验证JWT token）"""
    # 这里简化处理，实际应该验证JWT token
    # 暂时返回固定用户ID，后续需要完善JWT验证
    return {"user_id": 1, "username": "test_user"}

@router.post("/send_code")
async def send_verification_code(login_data: TelegramLogin):
    """发送Telegram验证码"""
    try:
        result = await TelegramService.send_verification_code(login_data)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        
        return {
            "message": result["message"],
            "phone_code_hash": result.get("phone_code_hash")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"发送验证码失败: {str(e)}")

@router.post("/verify_login")
async def verify_and_login(verify_data: TelegramVerify, current_user: dict = Depends(get_current_user)):
    """验证码登录"""
    try:
        result = await TelegramService.verify_and_login(verify_data, current_user["user_id"])
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        
        return {
            "message": result["message"],
            "account": result["account"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"登录失败: {str(e)}")

@router.get("/accounts")
async def get_telegram_accounts(current_user: dict = Depends(get_current_user)):
    """获取用户的Telegram账号列表"""
    try:
        accounts = TelegramService.get_user_telegram_accounts(current_user["user_id"])
        
        return {
            "accounts": accounts,
            "total": len(accounts)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取账号列表失败: {str(e)}")

@router.delete("/accounts/{account_id}")
async def delete_telegram_account(account_id: int, current_user: dict = Depends(get_current_user)):
    """删除Telegram账号"""
    try:
        result = TelegramService.delete_telegram_account(account_id, current_user["user_id"])
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        
        return {"message": result["message"]}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除账号失败: {str(e)}")

@router.post("/accounts/{account_id}/check_status")
async def check_account_status(account_id: int, current_user: dict = Depends(get_current_user)):
    """检查账号状态"""
    try:
        result = await TelegramService.check_account_status(account_id, current_user["user_id"])
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        
        return {"status": result["status"]}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"检查状态失败: {str(e)}")

@router.post("/refresh_accounts")
async def refresh_all_accounts(current_user: dict = Depends(get_current_user)):
    """刷新所有账号状态"""
    try:
        accounts = TelegramService.get_user_telegram_accounts(current_user["user_id"])
        
        # 异步检查所有账号状态
        tasks = []
        for account in accounts:
            task = TelegramService.check_account_status(account["id"], current_user["user_id"])
            tasks.append(task)
        
        if tasks:
            await asyncio.gather(*tasks)
        
        # 重新获取更新后的账号列表
        updated_accounts = TelegramService.get_user_telegram_accounts(current_user["user_id"])
        
        return {
            "message": "账号状态刷新完成",
            "accounts": updated_accounts,
            "total": len(updated_accounts)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"刷新账号状态失败: {str(e)}") 