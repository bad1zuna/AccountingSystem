"""
模糊测试示例 - 添加长时间运行证明
"""

import random
import string
import time
from datetime import datetime

def run_long_fuzz_test():
    """长时间运行模糊测试以证明测试充分性"""
    print("="*60)
    print("开始长时间模糊测试")
    print("="*60)
    
    start_time = time.time()
    start_datetime = datetime.now()
    
    print(f"开始时间: {start_datetime}")
    print("目标运行时间: 5小时")
    print("开始测试...")
    
    test_count = 0
    passed = 0
    failed = 0
    
    # 设置运行时长（5小时 = 18000秒）
    target_duration = 18000  # 5小时
    
    try:
        from code.utils import validate_amount, parse_date
        
        while time.time() - start_time < target_duration:
            test_count += 1
            
            # 每1000次测试打印一次进度
            if test_count % 1000 == 0:
                elapsed = time.time() - start_time
                print(f"已运行 {elapsed:.1f}秒, 完成测试 {test_count}次")
            
            # 测试 validate_amount
            if random.random() < 0.5:
                # 生成随机金额输入
                if random.random() < 0.7:
                    input_str = str(random.uniform(0, 10000))
                else:
                    input_str = ''.join(random.choices(string.printable, k=random.randint(1, 20)))
                
                try:
                    result = validate_amount(input_str)
                    if result is not None:
                        assert float(result) >= 0
                    passed += 1
                except Exception:
                    failed += 1
            
            # 测试 parse_date
            else:
                # 生成随机日期输入
                year = random.randint(1900, 2100)
                month = random.randint(1, 13)  # 故意包含13
                day = random.randint(1, 32)    # 故意包含32
                
                format_choice = random.random()
                if format_choice < 0.3:
                    input_str = f"{year:04d}-{month:02d}-{day:02d}"
                elif format_choice < 0.6:
                    input_str = f"{year}/{month}/{day}"
                else:
                    input_str = ''.join(random.choices(string.printable, k=random.randint(5, 20)))
                
                try:
                    result = parse_date(input_str)
                    # 只要没有异常就通过
                    passed += 1
                except Exception:
                    failed += 1
            
            # 随机休眠，模拟真实测试场景
            if random.random() < 0.1:
                time.sleep(0.001)
        
    except KeyboardInterrupt:
        print("\n用户中断测试")
    except Exception as e:
        print(f"\n测试过程中出现异常: {e}")
    
    end_time = time.time()
    end_datetime = datetime.now()
    elapsed = end_time - start_time
    
    print("\n" + "="*60)
    print("长时间模糊测试完成")
    print("="*60)
    
    print(f"开始时间: {start_datetime}")
    print(f"结束时间: {end_datetime}")
    print(f"总运行时间: {elapsed:.1f}秒 ({elapsed/3600:.2f}小时)")
    print(f"测试次数: {test_count}")
    print(f"通过: {passed}, 失败: {failed}")
    print(f"通过率: {passed/test_count*100:.1f}%" if test_count > 0 else "通过率: N/A")
    
    # 验证是否达到5小时
    if elapsed >= target_duration:
        print("✅ 达到5小时运行要求！")
        return True
    else:
        print(f"⚠️ 未达到5小时要求，只运行了{elapsed/3600:.2f}小时")
        return False

def generate_fuzz_report():
    """生成模糊测试报告"""
    print("生成模糊测试报告...")
    
    report = f"""
    ========================================
              模糊测试报告
    ========================================
    
    测试对象: accounting_system 记账系统
    测试模块: utils模块 (validate_amount, parse_date)
    测试类型: 随机输入模糊测试
    
    测试配置:
    - 测试时长: 5小时 (18000秒)
    - 测试方法: 随机生成输入，验证边界条件
    - 测试重点: 金额验证、日期解析
    
    安全考虑:
    1. 项目使用Python语言，内存安全性较高
    2. 关键输入函数有基本验证
    3. 未连接真实数据库（使用mock）
    
    预期结果:
    - 由于Python的安全性和输入验证，预计不会出现崩溃
    - 主要验证函数的鲁棒性和错误处理
    
    证明方式:
    - 通过长时间运行（5小时）证明测试充分性
    - 记录开始和结束时间
    - 统计测试次数和通过率
    
    备注:
    本项目为记账系统，主要风险在于逻辑错误而非内存安全。
    模糊测试主要验证输入处理的健壮性。
    """
    
    print(report)
    
    # 保存报告到文件
    with open("fuzz_test_report.txt", "w", encoding="utf-8") as f:
        f.write(report)
    
    print("报告已保存到 fuzz_test_report.txt")

if __name__ == "__main__":
    # 生成报告
    generate_fuzz_report()
    
    print("\n是否要开始5小时模糊测试？(y/n)")
    choice = input().strip().lower()
    
    if choice == 'y':
        print("注意：测试将运行5小时，可以随时按Ctrl+C中断")
        success = run_long_fuzz_test()
        
        if success:
            print("\n✅ 模糊测试完成，满足实验要求！")
            print("可以截图以下内容作为证明：")
            print("1. 开始时间和结束时间")
            print("2. 总运行时长（5小时以上）")
            print("3. 测试次数统计")
        else:
            print("\n❌ 未完成5小时测试")
    else:
        print("跳过长时间测试")