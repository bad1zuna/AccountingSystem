"""
工具模块：日志输出、数据格式化与输入校验
"""

from datetime import datetime
import sys


def log(message: str, level: str = "INFO"):
    """统一日志输出"""
    time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{time_str}] [{level.upper()}] {message}")


def validate_amount(amount_str: str) -> float:
    """校验金额输入是否合法"""
    try:
        value = float(amount_str)
        if value < 0:
            raise ValueError
        return value
    except ValueError:
        log("金额输入无效，请输入正数。", "ERROR")
        return None


def confirm_exit():
    """退出确认提示"""
    ans = input("是否确认退出？(y/n): ")
    if ans.lower() in ("y", "yes"):
        log("程序已退出，再见！", "INFO")
        sys.exit(0)


def format_currency(value: float) -> str:
    """货币格式化输出"""
    return f"¥{value:,.2f}"


def parse_date(date_str: str):
    """字符串转日期对象"""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        log("日期格式错误，应为 YYYY-MM-DD", "ERROR")
        return None
