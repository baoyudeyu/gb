import pymysql
from contextlib import contextmanager

# 数据库配置
DATABASE_CONFIG = {
    'host': 'gz-cynosdbmysql-grp-jj6na063.sql.tencentcdb.com',
    'port': 21151,
    'user': 'zhibo',
    'password': '04By0302',
    'database': 'zhibo',
    'charset': 'utf8mb4'
}

@contextmanager
def get_db_connection():
    """获取数据库连接的上下文管理器"""
    connection = None
    try:
        connection = pymysql.connect(**DATABASE_CONFIG)
        yield connection
    except Exception as e:
        if connection:
            connection.rollback()
        raise e
    finally:
        if connection:
            connection.close()

def init_database():
    """初始化数据库表结构"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # 创建用户表
        create_users_table = """
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
        
        cursor.execute(create_users_table)
        conn.commit()
        print("数据库表初始化完成")

if __name__ == "__main__":
    init_database() 