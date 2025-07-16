#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymysql
from config.database import get_db_connection

def fix_telegram_username_field():
    """修复telegram_username字段，添加默认值或允许NULL"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # 检查当前字段结构
            cursor.execute("DESCRIBE users")
            columns = cursor.fetchall()
            
            print("当前表结构:")
            for col in columns:
                print(f"  {col[0]}: {col[1]} {col[2]} {col[3]} {col[4]} {col[5]}")
            
            # 修改telegram_username字段，允许NULL或设置默认值
            print("\n修改telegram_username字段...")
            
            # 方案1：允许NULL
            alter_sql = "ALTER TABLE users MODIFY COLUMN telegram_username VARCHAR(50) NULL DEFAULT NULL"
            cursor.execute(alter_sql)
            conn.commit()
            print("telegram_username字段修改成功 - 允许NULL")
            
            # 再次检查表结构
            cursor.execute("DESCRIBE users")
            columns = cursor.fetchall()
            
            print("\n修改后的表结构:")
            for col in columns:
                print(f"  {col[0]}: {col[1]} {col[2]} {col[3]} {col[4]} {col[5]}")
                
    except Exception as e:
        print(f"修复失败: {e}")

if __name__ == "__main__":
    print("开始修复telegram_username字段...")
    fix_telegram_username_field()
    print("修复完成") 