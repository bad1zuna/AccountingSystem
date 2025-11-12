"""
预算与提醒模块：负责预算设定和支出监控
"""

from datetime import datetime, timedelta
from .database import get_connection
from .utils import log, format_currency


class Budget:
    """预算管理类"""
    
    def __init__(self, period='month', amount=0, start_date=None, end_date=None):
        self.period = period  # 'month' 或 'year'
        self.amount = amount
        self.start_date = start_date or datetime.now().date()
        self.end_date = end_date or self._calculate_end_date()
    
    def _calculate_end_date(self):
        """计算预算结束日期"""
        if self.period == 'month':
            # 下个月的同一天
            next_month = self.start_date.replace(day=28) + timedelta(days=4)
            return next_month.replace(day=1) - timedelta(days=1)
        else:  # year
            return self.start_date.replace(month=12, day=31)
    
    def save(self):
        """保存预算设置"""
        conn = get_connection()
        cursor = conn.cursor()
        
        # 先检查是否已有同期的预算
        cursor.execute("""
            SELECT id FROM budgets 
            WHERE period = %s AND start_date = %s
        """, (self.period, self.start_date))
        
        existing = cursor.fetchone()
        
        if existing:
            # 更新现有预算
            cursor.execute("""
                UPDATE budgets 
                SET amount = %s, end_date = %s
                WHERE id = %s
            """, (self.amount, self.end_date, existing[0]))
        else:
            # 插入新预算
            cursor.execute("""
                INSERT INTO budgets (period, amount, start_date, end_date)
                VALUES (%s, %s, %s, %s)
            """, (self.period, self.amount, self.start_date, self.end_date))
        
        conn.commit()
        cursor.close()
        conn.close()
        return True
    
    @staticmethod
    def get_current_budget(period='month'):
        """获取当前周期的预算"""
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        today = datetime.now().date()
        
        cursor.execute("""
            SELECT * FROM budgets 
            WHERE period = %s AND start_date <= %s AND end_date >= %s
            ORDER BY start_date DESC 
            LIMIT 1
        """, (period, today, today))
        
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return result
    
    @staticmethod
    def get_all_budgets():
        """获取所有预算设置"""
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT * FROM budgets 
            ORDER BY start_date DESC
        """)
        
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return result
    
    @staticmethod
    def calculate_current_expense(period='month'):
        """计算当前周期的支出"""
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        today = datetime.now().date()
        budget = Budget.get_current_budget(period)
        
        if not budget:
            return 0
        
        if period == 'month':
            # 计算当月支出
            cursor.execute("""
                SELECT COALESCE(SUM(amount), 0) as total
                FROM records 
                WHERE type = 'expense' 
                AND date >= %s AND date <= %s
            """, (budget['start_date'], budget['end_date']))
        else:  # year
            # 计算当年支出
            cursor.execute("""
                SELECT COALESCE(SUM(amount), 0) as total
                FROM records 
                WHERE type = 'expense' 
                AND YEAR(date) = YEAR(%s)
            """, (today,))
        
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return float(result['total']) if result else 0
    
    @staticmethod
    def check_budget_alert(threshold=0.8):
        """检查预算提醒（threshold: 提醒阈值，默认80%）"""
        budget = Budget.get_current_budget('month')
        if not budget:
            return None
        
        current_expense = Budget.calculate_current_expense('month')
        budget_amount = float(budget['amount'])
        
        if budget_amount <= 0:
            return None
        
        expense_ratio = current_expense / budget_amount
        
        if expense_ratio >= 1.0:
            return {
                'type': 'exceeded',
                'message': f'⚠️ 预算已超支！当前支出 {format_currency(current_expense)}，预算 {format_currency(budget_amount)}',
                'ratio': expense_ratio
            }
        elif expense_ratio >= threshold:
            return {
                'type': 'warning',
                'message': f'⚠️ 预算提醒：当前支出已达预算的 {expense_ratio:.1%} ({format_currency(current_expense)} / {format_currency(budget_amount)})',
                'ratio': expense_ratio
            }
        
        return None


class BudgetManager:
    """预算管理器"""
    
    @staticmethod
    def setup_budget_interactive():
        """交互式设置预算"""
        print("\n=== 预算设置 ===")
        
        # 选择预算周期
        print("1. 月度预算")
        print("2. 年度预算")
        period_choice = input("请选择预算周期：").strip()
        
        period = 'month' if period_choice == '1' else 'year'
        period_name = "月度" if period == 'month' else "年度"
        
        # 输入预算金额
        while True:
            try:
                amount = float(input(f"请输入{period_name}预算金额：").strip())
                if amount <= 0:
                    log("预算金额必须大于0", "ERROR")
                    continue
                break
            except ValueError:
                log("请输入有效的数字", "ERROR")
        
        # 设置开始日期
        start_date_input = input("预算开始日期 (YYYY-MM-DD，留空使用今天)：").strip()
        if start_date_input:
            from .utils import parse_date
            start_date = parse_date(start_date_input)
            if not start_date:
                return False
        else:
            start_date = datetime.now().date()
        
        # 创建并保存预算
        budget = Budget(period, amount, start_date)
        if budget.save():
            log(f"{period_name}预算设置成功！", "SUCCESS")
            log(f"预算金额: {format_currency(amount)}", "INFO")
            log(f"预算周期: {start_date} 至 {budget.end_date}", "INFO")
            return True
        else:
            log("预算设置失败", "ERROR")
            return False
    
    @staticmethod
    def show_budget_status():
        """显示预算状态"""
        print("\n=== 预算状态 ===")
        
        # 月度预算状态
        monthly_budget = Budget.get_current_budget('month')
        monthly_expense = Budget.calculate_current_expense('month')
        
        if monthly_budget:
            budget_amount = float(monthly_budget['amount'])
            ratio = monthly_expense / budget_amount if budget_amount > 0 else 0
            
            print(f"📊 月度预算状态:")
            print(f"   预算金额: {format_currency(budget_amount)}")
            print(f"   当前支出: {format_currency(monthly_expense)}")
            print(f"   使用进度: {ratio:.1%}")
            
            if ratio >= 1.0:
                print("   ⚠️ 状态: 已超支")
            elif ratio >= 0.8:
                print("   ⚠️ 状态: 接近预算")
            else:
                print("   ✅ 状态: 正常")
        else:
            print("📊 月度预算: 未设置")
        
        # 检查并显示提醒
        alert = Budget.check_budget_alert()
        if alert:
            print(f"\n🔔 {alert['message']}")
        
        return monthly_budget is not None