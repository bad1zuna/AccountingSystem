"""
accounting_system.code 包初始化文件
定义版本号，并统一导出常用类与函数。
"""

__version__ = "1.0.0"

from .database import get_connection, init_database
from .category import Category
from .record import Record
from .utils import log, validate_amount, confirm_exit, format_currency, parse_date
from .statistics import Statistics, Chart
from .budget import Budget, BudgetManager
from .search import SearchEngine, SearchManager