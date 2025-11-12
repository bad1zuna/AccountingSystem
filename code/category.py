"""
分类模块：支持用户自定义分类与关键字匹配
"""

from .database import get_connection


class Category:
    """表示消费分类，如 餐饮 / 交通 / 娱乐"""

    def __init__(self, name: str, keywords: str = ""):
        self.name = name
        self.keywords = keywords

    def save(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO categories (name, keywords) VALUES (%s, %s)",
            (self.name, self.keywords)
        )
        conn.commit()
        cursor.close()
        conn.close()

    @staticmethod
    def get_all():
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM categories")
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return result

    @staticmethod
    def find_by_keyword(word: str):
        """根据关键字匹配分类"""
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM categories")
        categories = cursor.fetchall()
        cursor.close()
        conn.close()

        for cat in categories:
            if cat["keywords"]:
                keywords = [k.strip() for k in cat["keywords"].split(",")]
                if any(word.lower() in kw.lower() for kw in keywords):
                    return cat
        return None
