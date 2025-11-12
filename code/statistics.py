"""
统计与可视化模块：负责数据统计和图表生成
"""

import matplotlib.pyplot as plt
import matplotlib
from datetime import datetime
from .database import get_connection
from .utils import log, format_currency

# 修复中文显示问题
try:
    # 方法1: 使用系统中文字体
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
    matplotlib.rcParams['font.family'] = 'sans-serif'
except:
    # 方法2: 如果上面方法失败，使用以下备选方案
    try:
        import matplotlib.font_manager as fm
        # 查找系统中可用的中文字体
        chinese_fonts = [f.name for f in fm.fontManager.ttflist if 'SimHei' in f.name or 'Microsoft' in f.name or 'YaHei' in f.name]
        if chinese_fonts:
            plt.rcParams['font.sans-serif'] = chinese_fonts
            plt.rcParams['axes.unicode_minus'] = False
    except:
        log("警告：中文字体配置失败，图表可能无法正常显示中文", "WARNING")


class Statistics:
    """统计计算类"""
    
    def __init__(self):
        self.period = "month"
    
    def get_expense_by_category(self, year=None, month=None):
        """按分类统计支出（用于饼图）"""
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        # 构建时间条件
        where_conditions = ["r.type = 'expense'"]
        params = []
        
        if year and month:
            where_conditions.append("YEAR(r.date) = %s AND MONTH(r.date) = %s")
            params.extend([year, month])
        elif year:
            where_conditions.append("YEAR(r.date) = %s")
            params.append(year)
        
        where_clause = " AND ".join(where_conditions)
        
        query = f"""
            SELECT 
                COALESCE(c.name, '未分类') as category, 
                SUM(r.amount) as total
            FROM records r
            LEFT JOIN categories c ON r.category_id = c.id
            WHERE {where_clause}
            GROUP BY c.name
            HAVING total > 0
            ORDER BY total DESC
        """
        
        cursor.execute(query, params)
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return result
    
    def get_expense_trend(self, year=None):
        """获取支出趋势（用于折线图）"""
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT 
                YEAR(r.date) as year,
                MONTH(r.date) as month,
                SUM(r.amount) as monthly_expense
            FROM records r
            WHERE r.type = 'expense'
            GROUP BY YEAR(r.date), MONTH(r.date)
            ORDER BY year, month
        """
        
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return result
    
    def get_income_vs_expense(self, year=None, month=None):
        """获取收入支出对比"""
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        where_conditions = []
        params = []
        
        if year and month:
            where_conditions.append("YEAR(date) = %s AND MONTH(date) = %s")
            params.extend([year, month])
        elif year:
            where_conditions.append("YEAR(date) = %s")
            params.append(year)
        
        where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
        
        query = f"""
            SELECT 
                type,
                SUM(amount) as total
            FROM records 
            WHERE {where_clause}
            GROUP BY type
        """
        
        cursor.execute(query, params)
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return result


class Chart:
    """图表生成类"""
    
    @staticmethod
    def generate_pie_chart(category_data, title="支出分类比例"):
        """生成饼状图"""
        if not category_data:
            log("暂无支出数据生成饼图", "WARNING")
            return False
        
        categories = [item['category'] for item in category_data]
        amounts = [float(item['total']) for item in category_data]
        total = sum(amounts)
        
        plt.figure(figsize=(10, 8))
        
        # 使用更简单的百分比显示，避免中文问题
        wedges, texts, autotexts = plt.pie(
            amounts, 
            labels=categories, 
            autopct=lambda p: f'{p:.1f}%',  # 简化显示，只显示百分比
            startangle=90, 
            textprops={'fontsize': 10}
        )
        
        # 设置标题（尝试修复中文显示）
        try:
            plt.title(f'{title}\n总支出: {format_currency(total)}', fontsize=14, fontweight='bold')
        except:
            plt.title(f'Expense Distribution\nTotal: {format_currency(total)}', fontsize=14, fontweight='bold')
        
        plt.axis('equal')
        plt.tight_layout()
        plt.show()
        return True
    
    @staticmethod
    def generate_line_chart(trend_data, title="月度支出趋势"):
        """生成折线图"""
        if not trend_data:
            log("暂无趋势数据生成折线图", "WARNING")
            return False
        
        # 格式化月份标签
        months = [f"{item['year']}-{item['month']:02d}" for item in trend_data]
        expenses = [float(item['monthly_expense']) for item in trend_data]
        
        plt.figure(figsize=(12, 6))
        plt.plot(months, expenses, marker='o', linewidth=2, markersize=6, color='#FF6B6B')
        
        # 设置标题和标签（处理中文显示）
        try:
            plt.title(title, fontsize=14, fontweight='bold')
            plt.xlabel('月份', fontsize=12)
            plt.ylabel('支出金额 (元)', fontsize=12)
        except:
            plt.title('Monthly Expense Trend', fontsize=14, fontweight='bold')
            plt.xlabel('Month', fontsize=12)
            plt.ylabel('Expense Amount (¥)', fontsize=12)
            
        plt.xticks(rotation=45)
        plt.grid(True, linestyle='--', alpha=0.7)
        
        # 在点上标注数值（使用英文避免中文问题）
        for i, (month, expense) in enumerate(zip(months, expenses)):
            plt.annotate(f'¥{expense:.0f}', (month, expense), 
                        textcoords="offset points", xytext=(0,10), ha='center', fontsize=9)
        
        plt.tight_layout()
        plt.show()
        return True
    
    @staticmethod
    def generate_income_expense_chart(comparison_data, title="收入支出对比"):
        """生成收入支出对比图"""
        if not comparison_data:
            log("暂无对比数据生成图表", "WARNING")
            return False
        
        # 使用英文标签避免中文显示问题
        type_mapping = {'income': 'Income', 'expense': 'Expense'}
        types = [type_mapping.get(item['type'], item['type']) for item in comparison_data]
        amounts = [float(item['total']) for item in comparison_data]
        colors = ['#4CAF50' if t == 'Income' else '#FF6B6B' for t in types]
        
        plt.figure(figsize=(8, 6))
        bars = plt.bar(types, amounts, color=colors, alpha=0.8)
        
        # 设置标题（处理中文显示）
        try:
            plt.title(title, fontsize=14, fontweight='bold')
            plt.ylabel('金额 (元)', fontsize=12)
        except:
            plt.title('Income vs Expense', fontsize=14, fontweight='bold')
            plt.ylabel('Amount (¥)', fontsize=12)
        
        # 在柱子上标注数值
        for bar, amount in zip(bars, amounts):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(amounts)*0.01,
                    f'¥{amount:.0f}', ha='center', va='bottom', fontsize=11)
        
        plt.tight_layout()
        plt.show()
        return True