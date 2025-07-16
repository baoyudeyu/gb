from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import bcrypt
from config.database import get_db_connection

class UserCreate(BaseModel):
    username: str
    password: str
    confirm_password: str
    secret_phrase: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResetPassword(BaseModel):
    username: str
    secret_phrase: str
    new_password: str
    confirm_new_password: str

class UserResponse(BaseModel):
    id: int
    username: str
    created_at: datetime
    is_active: bool

class UserService:
    @staticmethod
    def hash_password(password: str) -> str:
        """加密密码"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """验证密码"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    @staticmethod
    def create_user(user_data: UserCreate) -> dict:
        """创建用户"""
        # 验证密码确认
        if user_data.password != user_data.confirm_password:
            return {"success": False, "message": "密码确认不一致"}
        
        # 密码长度验证
        if len(user_data.password) < 6:
            return {"success": False, "message": "密码长度不能少于6位"}
        
        # 用户名长度验证
        if len(user_data.username) < 3:
            return {"success": False, "message": "用户名长度不能少于3位"}
        
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                # 检查用户名是否已存在
                cursor.execute("SELECT id FROM users WHERE username = %s", (user_data.username,))
                if cursor.fetchone():
                    return {"success": False, "message": "用户名已存在"}
                
                # 创建用户
                password_hash = UserService.hash_password(user_data.password)
                secret_phrase_hash = UserService.hash_password(user_data.secret_phrase)
                
                cursor.execute(
                    "INSERT INTO users (username, password_hash, secret_phrase) VALUES (%s, %s, %s)",
                    (user_data.username, password_hash, secret_phrase_hash)
                )
                conn.commit()
                
                return {"success": True, "message": "注册成功"}
                
        except Exception as e:
            return {"success": False, "message": f"注册失败: {str(e)}"}
    
    @staticmethod
    def login_user(login_data: UserLogin) -> dict:
        """用户登录"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute(
                    "SELECT id, username, password_hash, is_active FROM users WHERE username = %s",
                    (login_data.username,)
                )
                user = cursor.fetchone()
                
                if not user:
                    return {"success": False, "message": "用户名不存在"}
                
                user_id, username, password_hash, is_active = user
                
                if not is_active:
                    return {"success": False, "message": "账号已被禁用"}
                
                if not UserService.verify_password(login_data.password, password_hash):
                    return {"success": False, "message": "密码错误"}
                
                return {
                    "success": True, 
                    "message": "登录成功",
                    "user": {
                        "id": user_id,
                        "username": username
                    }
                }
                
        except Exception as e:
            return {"success": False, "message": f"登录失败: {str(e)}"}
    
    @staticmethod
    def reset_password(reset_data: UserResetPassword) -> dict:
        """重置密码"""
        # 验证新密码确认
        if reset_data.new_password != reset_data.confirm_new_password:
            return {"success": False, "message": "新密码确认不一致"}
        
        # 密码长度验证
        if len(reset_data.new_password) < 6:
            return {"success": False, "message": "新密码长度不能少于6位"}
        
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute(
                    "SELECT id, secret_phrase FROM users WHERE username = %s",
                    (reset_data.username,)
                )
                user = cursor.fetchone()
                
                if not user:
                    return {"success": False, "message": "用户名不存在"}
                
                user_id, secret_phrase_hash = user
                
                if not UserService.verify_password(reset_data.secret_phrase, secret_phrase_hash):
                    return {"success": False, "message": "暗语错误"}
                
                # 更新密码
                new_password_hash = UserService.hash_password(reset_data.new_password)
                cursor.execute(
                    "UPDATE users SET password_hash = %s WHERE id = %s",
                    (new_password_hash, user_id)
                )
                conn.commit()
                
                return {"success": True, "message": "密码重置成功"}
                
        except Exception as e:
            return {"success": False, "message": f"密码重置失败: {str(e)}"} 