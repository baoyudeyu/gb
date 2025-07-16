#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymysql
from config.database import DATABASE_CONFIG, get_db_connection

def check_and_fix_database():
    """检查并修复数据库表结构"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # 检查表是否存在
            cursor.execute("SHOW TABLES LIKE 'users'")
            table_exists = cursor.fetchone()
            
            if not table_exists:
                print("用户表不存在，正在创建...")
                create_users_table(cursor, conn)
            else:
                print("用户表已存在，检查表结构...")
                check_table_structure(cursor, conn)
                
    except Exception as e:
        print(f"数据库操作失败: {e}")

def create_users_table(cursor, conn):
    """创建用户表"""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        secret_phrase VARCHAR(255) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        is_active BOOLEAN DEFAULT TRUE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """
    
    cursor.execute(create_table_sql)
    conn.commit()
    print("用户表创建成功")

def check_table_structure(cursor, conn):
    """检查表结构并修复缺失的字段"""
    # 获取当前表结构
    cursor.execute("DESCRIBE users")
    columns = cursor.fetchall()
    
    existing_columns = [col[0] for col in columns]
    print(f"现有字段: {existing_columns}")
    
    # 检查必需的字段
    required_columns = {
        'id': 'INT AUTO_INCREMENT PRIMARY KEY',
        'username': 'VARCHAR(50) UNIQUE NOT NULL',
        'password_hash': 'VARCHAR(255) NOT NULL',
        'secret_phrase': 'VARCHAR(255) NOT NULL',
        'created_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP',
        'updated_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP',
        'is_active': 'BOOLEAN DEFAULT TRUE'
    }
    
    # 添加缺失的字段
    for column_name, column_def in required_columns.items():
        if column_name not in existing_columns:
            print(f"添加缺失字段: {column_name}")
            if column_name == 'id':
                # 如果是主键，需要特殊处理
                continue
            else:
                alter_sql = f"ALTER TABLE users ADD COLUMN {column_name} {column_def}"
                cursor.execute(alter_sql)
                conn.commit()
                print(f"字段 {column_name} 添加成功")
    
    # 再次检查表结构
    cursor.execute("DESCRIBE users")
    columns = cursor.fetchall()
    print("修复后的表结构:")
    for col in columns:
        print(f"  {col[0]}: {col[1]}")

def test_database_connection():
    """测试数据库连接"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            print(f"数据库连接测试成功: {result}")
            return True
    except Exception as e:
        print(f"数据库连接测试失败: {e}")
        return False

if __name__ == "__main__":
    print("开始检查和修复数据库...")
    print(f"数据库配置: {DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/{DATABASE_CONFIG['database']}")
    
    if test_database_connection():
        check_and_fix_database()
        print("数据库检查和修复完成")
    else:
        print("数据库连接失败，请检查配置") 