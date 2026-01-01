"""
数据库连接模块：负责 MySQL 连接与表结构初始化
包含植入的代码缺陷
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


# [IMPLANTED FLAW 1: 数据库连接泄漏]
def get_records_with_leak():
    """
    植入缺陷：数据库连接未关闭
    CWE-775: Missing Release of File Descriptor or Handle after Effective Lifetime
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM records")
    results = cursor.fetchall()
    # 缺陷：忘记 conn.close() 和 cursor.close()
    return results


# [IMPLANTED FLAW 2: 硬编码密码 - 安全漏洞]
def get_connection_insecure():
    """
    植入缺陷：硬编码数据库密码
    CWE-259: Use of Hard-coded Password
    """
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root", 
            password="Thedead26innju",  # 缺陷：硬编码密码
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