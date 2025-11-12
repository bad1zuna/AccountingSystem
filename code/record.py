"""
收支记录模块：负责记录收入与支出，支持自动分类
"""

from datetime import date
from .database import get_connection
from .category import Category


class Record:
    """表示一条收支记录"""

    def __init__(self, record_type, amount, description, date_value=None):
        self.type = record_type  # 'income' or 'expense'
        self.amount = amount
        self.description = description
        self.date = date_value or date.today()

    def _find_category(self):
        """根据描述自动匹配分类"""
        match = Category.find_by_keyword(self.description)
        return match["id"] if match else None

    def save(self):
        conn = get_connection()
        cursor = conn.cursor()
        category_id = self._find_category()
        cursor.execute(
            """
            INSERT INTO records (type, amount, category_id, description, date)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (self.type, self.amount, category_id, self.description, self.date)
        )
        conn.commit()
        cursor.close()
        conn.close()

    @staticmethod
    def get_all():
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT r.id, r.type, r.amount, c.name AS category, r.description, r.date
            FROM records r
            LEFT JOIN categories c ON r.category_id = c.id
            ORDER BY r.date DESC
        """)
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return result
    
    # 在 record.py 的 Record 类中添加以下方法

@staticmethod
def get_by_date_range(start_date, end_date):
    """按时间范围查询记录"""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT r.id, r.type, r.amount, c.name AS category, r.description, r.date
        FROM records r
        LEFT JOIN categories c ON r.category_id = c.id
        WHERE r.date BETWEEN %s AND %s
        ORDER BY r.date DESC
    """, (start_date, end_date))
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result

@staticmethod
def get_by_category(category_name):
    """按分类查询记录"""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT r.id, r.type, r.amount, c.name AS category, r.description, r.date
        FROM records r
        LEFT JOIN categories c ON r.category_id = c.id
        WHERE c.name = %s
        ORDER BY r.date DESC
    """, (category_name,))
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result

@staticmethod
def get_expenses_summary(period='month'):
    """获取支出汇总（用于统计）"""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    if period == 'month':
        query = """
            SELECT 
                DATE_FORMAT(date, '%Y-%m') as period,
                SUM(amount) as total_expense
            FROM records 
            WHERE type = 'expense'
            GROUP BY DATE_FORMAT(date, '%Y-%m')
            ORDER BY period
        """
    elif period == 'year':
        query = """
            SELECT 
                YEAR(date) as period,
                SUM(amount) as total_expense
            FROM records 
            WHERE type = 'expense'
            GROUP BY YEAR(date)
            ORDER BY period
        """
    
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result
