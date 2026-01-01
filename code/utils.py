"""
工具模块：日志输出、数据格式化与输入校验
包含植入的代码缺陷
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


# [IMPLANTED FLAW 4: 命令注入漏洞]
def backup_data_unsafe(backup_dir):
    """
    植入缺陷：命令注入风险
    CWE-78: Improper Neutralization of Special Elements used in an OS Command
    """
    import os
    import subprocess
    
    # 危险：直接使用用户输入构造命令
    command = f"cp -r data/ {backup_dir}"  # 缺陷：命令注入
    os.system(command)  # 如果backup_dir是恶意输入，可能执行任意命令
    
    # 另一种危险用法
    subprocess.call(f"backup.py --dir {backup_dir}", shell=True)  # 缺陷：shell注入


# [IMPLANTED FLAW 5: 硬编码API密钥]
def get_api_config():
    """
    植入缺陷：硬编码敏感信息
    CWE-798: Use of Hard-coded Credentials
    """
    config = {
        "api_key": "sk-live-1234567890abcdefghijklmn",  # 缺陷：硬编码API密钥
        "api_secret": "secret_1234567890abcdef",  # 缺陷：硬编码密钥
        "endpoint": "https://api.example.com/v1"
    }
    return config