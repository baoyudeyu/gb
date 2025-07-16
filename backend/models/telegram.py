from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import os
import json
import asyncio
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError
from config.database import get_db_connection

class TelegramLogin(BaseModel):
    phone: str
    api_id: int
    api_hash: str

class TelegramVerify(BaseModel):
    phone: str
    verification_code: str
    api_id: int
    api_hash: str

class TelegramAccount(BaseModel):
    id: Optional[int] = None
    user_id: int
    phone: str
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    telegram_user_id: Optional[int] = None
    session_file: Optional[str] = None
    status: str = 'offline'
    last_active: Optional[datetime] = None
    created_at: Optional[datetime] = None

class TelegramService:
    """Telegram相关服务"""
    
    @staticmethod
    def init_telegram_table():
        """初始化telegram账号表"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS telegram_accounts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                phone VARCHAR(20) NOT NULL,
                username VARCHAR(50) NULL,
                first_name VARCHAR(100) NULL,
                last_name VARCHAR(100) NULL,
                telegram_user_id BIGINT NULL,
                session_file VARCHAR(255) NULL,
                status ENUM('online', 'offline', 'connecting') DEFAULT 'offline',
                last_active TIMESTAMP NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE KEY unique_user_phone (user_id, phone)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """
            
            cursor.execute(create_table_sql)
            conn.commit()
    
    @staticmethod
    async def send_verification_code(login_data: TelegramLogin) -> dict:
        """发送验证码"""
        try:
            # 创建session目录
            session_dir = "sessions"
            if not os.path.exists(session_dir):
                os.makedirs(session_dir)
            
            session_file = os.path.join(session_dir, f"{login_data.phone}.session")
            
            client = TelegramClient(session_file, login_data.api_id, login_data.api_hash)
            
            await client.connect()
            
            # 发送验证码
            sent_code = await client.send_code_request(login_data.phone)
            
            await client.disconnect()
            
            return {
                "success": True,
                "message": "验证码已发送",
                "phone_code_hash": sent_code.phone_code_hash
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"发送验证码失败: {str(e)}"
            }
    
    @staticmethod
    async def verify_and_login(verify_data: TelegramVerify, user_id: int) -> dict:
        """验证码登录"""
        try:
            session_dir = "sessions"
            session_file = os.path.join(session_dir, f"{verify_data.phone}.session")
            
            client = TelegramClient(session_file, verify_data.api_id, verify_data.api_hash)
            
            await client.connect()
            
            # 验证登录
            await client.sign_in(verify_data.phone, verify_data.verification_code)
            
            # 获取用户信息
            me = await client.get_me()
            
            # 保存到数据库
            telegram_account = {
                "user_id": user_id,
                "phone": verify_data.phone,
                "username": me.username,
                "first_name": me.first_name,
                "last_name": me.last_name,
                "telegram_user_id": me.id,
                "session_file": session_file,
                "status": "online"
            }
            
            account_id = TelegramService.save_telegram_account(telegram_account)
            
            await client.disconnect()
            
            return {
                "success": True,
                "message": "Telegram账号登录成功",
                "account": {
                    "id": account_id,
                    "phone": verify_data.phone,
                    "username": me.username,
                    "first_name": me.first_name,
                    "last_name": me.last_name,
                    "telegram_user_id": me.id,
                    "status": "online"
                }
            }
            
        except PhoneCodeInvalidError:
            return {
                "success": False,
                "message": "验证码无效"
            }
        except SessionPasswordNeededError:
            return {
                "success": False,
                "message": "需要两步验证密码"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"登录失败: {str(e)}"
            }
    
    @staticmethod
    def save_telegram_account(account_data: dict) -> int:
        """保存Telegram账号到数据库"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # 检查是否已存在
            cursor.execute(
                "SELECT id FROM telegram_accounts WHERE user_id = %s AND phone = %s",
                (account_data["user_id"], account_data["phone"])
            )
            existing = cursor.fetchone()
            
            if existing:
                # 更新现有记录
                cursor.execute("""
                    UPDATE telegram_accounts 
                    SET username = %s, first_name = %s, last_name = %s, 
                        telegram_user_id = %s, session_file = %s, status = %s,
                        last_active = CURRENT_TIMESTAMP
                    WHERE id = %s
                """, (
                    account_data["username"],
                    account_data["first_name"],
                    account_data["last_name"],
                    account_data["telegram_user_id"],
                    account_data["session_file"],
                    account_data["status"],
                    existing[0]
                ))
                conn.commit()
                return existing[0]
            else:
                # 插入新记录
                cursor.execute("""
                    INSERT INTO telegram_accounts 
                    (user_id, phone, username, first_name, last_name, telegram_user_id, session_file, status, last_active)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                """, (
                    account_data["user_id"],
                    account_data["phone"],
                    account_data["username"],
                    account_data["first_name"],
                    account_data["last_name"],
                    account_data["telegram_user_id"],
                    account_data["session_file"],
                    account_data["status"]
                ))
                conn.commit()
                return cursor.lastrowid
    
    @staticmethod
    def get_user_telegram_accounts(user_id: int) -> List[dict]:
        """获取用户的Telegram账号列表"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, phone, username, first_name, last_name, telegram_user_id, 
                       status, last_active, created_at
                FROM telegram_accounts 
                WHERE user_id = %s
                ORDER BY created_at DESC
            """, (user_id,))
            
            accounts = cursor.fetchall()
            
            result = []
            for account in accounts:
                result.append({
                    "id": account[0],
                    "phone": account[1],
                    "username": account[2],
                    "first_name": account[3],
                    "last_name": account[4],
                    "telegram_user_id": account[5],
                    "status": account[6],
                    "last_active": account[7].strftime("%Y-%m-%d %H:%M:%S") if account[7] else None,
                    "created_at": account[8].strftime("%Y-%m-%d %H:%M:%S") if account[8] else None
                })
            
            return result
    
    @staticmethod
    def delete_telegram_account(account_id: int, user_id: int) -> dict:
        """删除Telegram账号"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                # 获取session文件路径
                cursor.execute(
                    "SELECT session_file FROM telegram_accounts WHERE id = %s AND user_id = %s",
                    (account_id, user_id)
                )
                result = cursor.fetchone()
                
                if not result:
                    return {"success": False, "message": "账号不存在"}
                
                session_file = result[0]
                
                # 删除数据库记录
                cursor.execute(
                    "DELETE FROM telegram_accounts WHERE id = %s AND user_id = %s",
                    (account_id, user_id)
                )
                conn.commit()
                
                # 删除session文件
                if session_file and os.path.exists(session_file):
                    os.remove(session_file)
                
                return {"success": True, "message": "账号删除成功"}
                
        except Exception as e:
            return {"success": False, "message": f"删除失败: {str(e)}"}
    
    @staticmethod
    async def check_account_status(account_id: int, user_id: int) -> dict:
        """检查账号状态"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT session_file, phone, username 
                    FROM telegram_accounts 
                    WHERE id = %s AND user_id = %s
                """, (account_id, user_id))
                
                result = cursor.fetchone()
                if not result:
                    return {"success": False, "message": "账号不存在"}
                
                session_file, phone, username = result
                
                if not session_file or not os.path.exists(session_file):
                    # 更新状态为离线
                    cursor.execute(
                        "UPDATE telegram_accounts SET status = 'offline' WHERE id = %s",
                        (account_id,)
                    )
                    conn.commit()
                    return {"success": True, "status": "offline"}
                
                # 尝试连接检查状态
                client = TelegramClient(session_file, 0, "")  # 使用已有session
                await client.connect()
                
                if await client.is_user_authorized():
                    status = "online"
                    # 更新最后活跃时间
                    cursor.execute("""
                        UPDATE telegram_accounts 
                        SET status = %s, last_active = CURRENT_TIMESTAMP 
                        WHERE id = %s
                    """, (status, account_id))
                    conn.commit()
                else:
                    status = "offline"
                    cursor.execute(
                        "UPDATE telegram_accounts SET status = %s WHERE id = %s",
                        (status, account_id)
                    )
                    conn.commit()
                
                await client.disconnect()
                
                return {"success": True, "status": status}
                
        except Exception as e:
            return {"success": False, "message": f"检查状态失败: {str(e)}"} 