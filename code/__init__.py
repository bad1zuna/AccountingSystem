"""
accounting_system.code 包初始化文件
定义版本号，并统一导出常用类与函数。
包含植入的缺陷函数导出
"""

__version__ = "1.0.0"

from .database import get_connection, init_database, get_records_with_leak, get_connection_insecure
from .category import Category
from .record import Record
from .utils import log, validate_amount, confirm_exit, format_currency, parse_date, backup_data_unsafe, get_api_config
from .statistics import Statistics, Chart
from .budget import Budget, BudgetManager
from .search import SearchEngine, SearchManager

# 导出缺陷函数
from .flawed_functions import (
    load_user_data_unsafe,
    read_config_file_leak, 
    update_balance_with_race,
    create_temp_file_unsafe,
    process_payment_silent_fail,
    hash_password_unsafe,
    read_user_file_unsafe,
    calculate_discount_unsafe,
    calculate_expression_unsafe
)