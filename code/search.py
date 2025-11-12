"""
查询与检索模块：提供多条件记录查询功能
"""

from .database import get_connection
from .utils import log, format_currency, parse_date


class SearchEngine:
    """搜索引擎类"""
    
    @staticmethod
    def search_records(keyword=None, category=None, record_type=None, 
                      min_amount=None, max_amount=None, 
                      start_date=None, end_date=None, 
                      sort_by='date', sort_order='DESC'):
        """多条件搜索记录"""
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        # 构建查询条件
        where_conditions = []
        params = []
        
        # 关键字搜索（描述模糊匹配）
        if keyword:
            where_conditions.append("r.description LIKE %s")
            params.append(f"%{keyword}%")
        
        # 分类搜索
        if category:
            where_conditions.append("c.name = %s")
            params.append(category)
        
        # 类型搜索
        if record_type:
            where_conditions.append("r.type = %s")
            params.append(record_type)
        
        # 金额范围搜索
        if min_amount is not None:
            where_conditions.append("r.amount >= %s")
            params.append(min_amount)
        
        if max_amount is not None:
            where_conditions.append("r.amount <= %s")
            params.append(max_amount)
        
        # 时间范围搜索
        if start_date:
            where_conditions.append("r.date >= %s")
            params.append(start_date)
        
        if end_date:
            where_conditions.append("r.date <= %s")
            params.append(end_date)
        
        # 构建WHERE子句
        where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
        
        # 排序
        sort_mapping = {
            'date': 'r.date',
            'amount': 'r.amount', 
            'type': 'r.type',
            'category': 'c.name'
        }
        sort_field = sort_mapping.get(sort_by, 'r.date')
        sort_direction = 'DESC' if sort_order.upper() == 'DESC' else 'ASC'
        
        # 执行查询
        query = f"""
            SELECT 
                r.id, r.type, r.amount, 
                COALESCE(c.name, '未分类') as category,
                r.description, r.date
            FROM records r
            LEFT JOIN categories c ON r.category_id = c.id
            WHERE {where_clause}
            ORDER BY {sort_field} {sort_direction}
        """
        
        cursor.execute(query, params)
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return result
    
    @staticmethod
    def search_by_multiple_criteria():
        """交互式多条件搜索"""
        from .category import Category
        
        print("\n=== 多条件搜索 ===")
        print("请输入搜索条件（留空表示不限制）：")
        
        # 获取搜索条件
        keyword = input("关键字搜索：").strip() or None
        record_type = input("记录类型 (income/expense)：").strip() or None
        min_amount = input("最小金额：").strip() or None
        max_amount = input("最大金额：").strip() or None
        start_date = input("开始日期 (YYYY-MM-DD)：").strip() or None
        end_date = input("结束日期 (YYYY-MM-DD)：").strip() or None
        
        # 分类选择
        categories = Category.get_all()
        if categories:
            print("\n可选分类：")
            print("0. 不限制分类")
            for i, cat in enumerate(categories, 1):
                print(f"{i}. {cat['name']}")
            
            cat_choice = input("请选择分类编号：").strip()
            if cat_choice and cat_choice != '0':
                try:
                    cat_index = int(cat_choice) - 1
                    if 0 <= cat_index < len(categories):
                        category = categories[cat_index]['name']
                    else:
                        log("无效的分类编号", "ERROR")
                        return []
                except ValueError:
                    log("请输入有效数字", "ERROR")
                    return []
            else:
                category = None
        else:
            category = None
        
        # 转换数据类型
        try:
            min_amount = float(min_amount) if min_amount else None
            max_amount = float(max_amount) if max_amount else None
        except ValueError:
            log("金额格式错误", "ERROR")
            return []
        
        # 解析日期
        if start_date:
            start_date = parse_date(start_date)
            if not start_date:
                return []
        
        if end_date:
            end_date = parse_date(end_date)
            if not end_date:
                return []
        
        # 执行搜索
        results = SearchEngine.search_records(
            keyword=keyword,
            category=category,
            record_type=record_type,
            min_amount=min_amount,
            max_amount=max_amount,
            start_date=start_date,
            end_date=end_date
        )
        
        return results
    
    @staticmethod
    def quick_search(keyword):
        """快速搜索（按关键字）"""
        return SearchEngine.search_records(keyword=keyword)
    
    @staticmethod
    def search_by_date_range(start_date, end_date):
        """按时间范围搜索"""
        return SearchEngine.search_records(start_date=start_date, end_date=end_date)
    
    @staticmethod
    def search_by_category(category_name):
        """按分类搜索"""
        return SearchEngine.search_records(category=category_name)
    
    @staticmethod
    def search_expenses_over_amount(amount):
        """搜索超过指定金额的支出"""
        return SearchEngine.search_records(record_type='expense', min_amount=amount)


class SearchManager:
    """搜索管理器"""
    
    @staticmethod
    def show_search_results(results, title="搜索结果"):
        """显示搜索结果"""
        if not results:
            log("未找到匹配的记录", "INFO")
            return
        
        print(f"\n=== {title} ===")
        print(f"找到 {len(results)} 条记录")
        
        total_income = 0
        total_expense = 0
        
        for r in results:
            log(f"[{r['type']}] {r['description']} - {format_currency(r['amount'])} ({r['category']}) {r['date']}")
            
            if r['type'] == 'income':
                total_income += float(r['amount'])
            else:
                total_expense += float(r['amount'])
        
        # 显示统计信息
        if total_income > 0 or total_expense > 0:
            print(f"\n📊 统计信息:")
            print(f"   总收入: {format_currency(total_income)}")
            print(f"   总支出: {format_currency(total_expense)}")
            print(f"   净收入: {format_currency(total_income - total_expense)}")