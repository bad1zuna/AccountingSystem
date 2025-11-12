"""
数据库连接模块：负责 MySQL 连接与表结构初始化
"""

import mysql.connector
from mysql.connector import Error


def get_connection():
    """创建并返回数据库连接"""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Thedead26innju",
            database="accounting_system"
        )
        return connection
    except Error as e:
        print(f"数据库连接失败: {e}")
        return None


def init_database():
    """初始化数据库表结构"""
    conn = get_connection()
    if not conn:
        return

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            keywords TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS records (
            id INT AUTO_INCREMENT PRIMARY KEY,
            type ENUM('income', 'expense') NOT NULL,
            amount DECIMAL(10,2) NOT NULL,
            category_id INT,
            description VARCHAR(255),
            date DATE,
            FOREIGN KEY (category_id) REFERENCES categories(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS budgets (
            id INT AUTO_INCREMENT PRIMARY KEY,
            period ENUM('month','year') NOT NULL,
            amount DECIMAL(10,2),
            start_date DATE,
            end_date DATE
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ 数据库初始化完成！")
