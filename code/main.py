"""
程序主入口：控制台交互逻辑
"""

from code import (
    init_database,
    Category,
    Record,
    Statistics,
    Chart,
    Budget,
    BudgetManager,
    SearchEngine, 
    SearchManager, 
    log,
    validate_amount,
    confirm_exit,
    format_currency,
    parse_date
)

def show_statistics_menu():
    """显示统计菜单"""
    print("\n=== 统计与图表 ===")
    print("1. 查看分类支出饼图")
    print("2. 查看月度趋势折线图") 
    print("3. 查看收入支出对比")
    print("4. 返回主菜单")
    
    choice = input("请选择统计类型：").strip()
    stats = Statistics()
    
    if choice == "1":
        # 分类支出饼图
        year = input("请输入年份（留空为所有年份）：").strip()
        month = input("请输入月份（留空为所有月份）：").strip()
        
        year = int(year) if year else None
        month = int(month) if month else None
        
        data = stats.get_expense_by_category(year, month)
        if data:
            title = "支出分类比例"
            if year and month:
                title = f"{year}年{month}月{title}"
            elif year:
                title = f"{year}年{title}"
                
            Chart.generate_pie_chart(data, title)
        else:
            log("暂无支出数据", "WARNING")
            
    elif choice == "2":
        # 月度趋势折线图
        data = stats.get_expense_trend()
        if data:
            Chart.generate_line_chart(data, "月度支出趋势图")
        else:
            log("暂无趋势数据", "WARNING")
            
    elif choice == "3":
        # 收入支出对比
        year = input("请输入年份（留空为所有年份）：").strip()
        month = input("请输入月份（留空为所有月份）：").strip()
        
        year = int(year) if year else None
        month = int(month) if month else None
        
        data = stats.get_income_vs_expense(year, month)
        if data:
            title = "收入支出对比"
            if year and month:
                title = f"{year}年{month}月{title}"
            elif year:
                title = f"{year}年{title}"
                
            Chart.generate_income_expense_chart(data, title)
        else:
            log("暂无对比数据", "WARNING")
            
    elif choice == "4":
        return
    else:
        log("无效选项", "WARNING")

def show_budget_menu():
    """显示预算菜单"""
    print("\n=== 预算管理 ===")
    print("1. 设置预算")
    print("2. 查看预算状态")
    print("3. 返回主菜单")
    
    choice = input("请选择操作：").strip()
    
    if choice == "1":
        BudgetManager.setup_budget_interactive()
    elif choice == "2":
        BudgetManager.show_budget_status()
    elif choice == "3":
        return
    else:
        log("无效选项", "WARNING")
        
def show_search_menu():
    """显示查询菜单"""
    print("\n=== 记录查询 ===")
    print("1. 快速搜索（按关键字）")
    print("2. 多条件高级搜索")
    print("3. 按时间范围查询")
    print("4. 按分类查询") 
    print("5. 返回主菜单")
    
    choice = input("请选择查询方式：").strip()
    
    if choice == "1":
        # 快速搜索
        keyword = input("请输入搜索关键字：").strip()
        if keyword:
            results = SearchEngine.quick_search(keyword)
            SearchManager.show_search_results(results, f"关键字搜索: {keyword}")
        else:
            log("请输入搜索关键字", "WARNING")
            
    elif choice == "2":
        # 多条件高级搜索
        results = SearchEngine.search_by_multiple_criteria()
        SearchManager.show_search_results(results, "高级搜索结果")
            
    elif choice == "3":
        # 时间范围查询
        start_date = input("开始日期 (YYYY-MM-DD)：").strip()
        end_date = input("结束日期 (YYYY-MM-DD)：").strip()
        
        start = parse_date(start_date)
        end = parse_date(end_date)
        
        if start and end:
            results = SearchEngine.search_by_date_range(start, end)
            SearchManager.show_search_results(results, f"{start_date} 至 {end_date} 的记录")
        else:
            log("日期格式错误", "ERROR")
            
    elif choice == "4":
        # 分类查询
        from .category import Category
        categories = Category.get_all()
        if categories:
            print("\n可选分类：")
            for i, cat in enumerate(categories, 1):
                print(f"{i}. {cat['name']}")
                
            cat_choice = input("请选择分类编号：").strip()
            try:
                cat_index = int(cat_choice) - 1
                if 0 <= cat_index < len(categories):
                    category_name = categories[cat_index]['name']
                    results = SearchEngine.search_by_category(category_name)
                    SearchManager.show_search_results(results, f"{category_name} 分类记录")
                else:
                    log("无效的分类编号", "ERROR")
            except ValueError:
                log("请输入有效数字", "ERROR")
        else:
            log("暂无分类数据", "WARNING")
            
    elif choice == "5":
        return
    else:
        log("无效选项", "WARNING")

def main():
    log("=== 个人记账系统启动 ===")
    init_database()

    # 初始化分类（仅首次）
    if not Category.get_all():
        log("初始化分类中...")
        Category("餐饮", "星巴克,麦当劳,奶茶,饮食").save()
        Category("交通", "地铁,公交,打车").save()
        Category("购物", "淘宝,京东,超市").save()
        Category("娱乐", "电影,游戏,KTV").save()

    while True:
        print("\n=== 主菜单 ===")
        print("1. 添加收支记录")
        print("2. 查看所有记录") 
        print("3. 统计与图表")
        print("4. 记录查询")
        print("5. 预算管理")
        print("6. 退出")
        choice = input("请选择操作：").strip()

        if choice == "1":
            record_type = input("类型 (income/expense)：").strip().lower()
            if record_type not in ['income', 'expense']:
                log("类型必须是 income 或 expense", "ERROR")
                continue
                
            amount = None
            while amount is None:
                amount = validate_amount(input("金额："))

            description = input("描述：").strip()
            Record(record_type, amount, description).save()
            log("记录保存成功！", "SUCCESS")

        elif choice == "2":
            records = Record.get_all()
            print("\n=== 收支记录 ===")
            for r in records:
                log(
                    f"[{r['type']}] {r['description']} - "
                    f"{format_currency(r['amount'])} ({r['category']}) {r['date']}"
                )

        elif choice == "3":
            show_statistics_menu()
            
        elif choice == "4":
            show_search_menu()
            
        elif choice == "5": 
            show_budget_menu()
            
        elif choice == "6":
            confirm_exit()

        else:
            log("无效选项，请重试。", "WARNING")


if __name__ == "__main__":
    main()