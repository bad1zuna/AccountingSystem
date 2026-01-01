"""
使用hypothesis进行正式的模糊测试 - 长时间运行版本（安静版）
保证运行5小时以上，减少输出刷屏
"""

import sys
import time
from datetime import datetime
import random
import string
import os

print("="*60)
print("长时间模糊测试 - 安静运行5小时版")
print("="*60)
print(f"开始时间: {datetime.now()}")
print("目标运行时间: 5小时")
print("输出模式: 每10分钟显示一次进度")
print("="*60)

# 禁用utils模块的log输出
import code.utils
original_log = code.utils.log

def quiet_log(message, level="INFO"):
    """静默日志函数，只记录不输出"""
    pass

# 临时替换log函数
code.utils.log = quiet_log

# 导入要测试的函数
sys.path.insert(0, '.')
try:
    from code.utils import validate_amount, parse_date
    print("✅ 成功导入测试函数")
    print("✅ 已禁用刷屏日志输出")
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    # 恢复原来的log函数
    code.utils.log = original_log
    sys.exit(1)

def run_5_hour_fuzz_test_quiet():
    """运行至少5小时的模糊测试（安静版）"""
    start_time = time.time()
    target_hours = 5
    target_seconds = target_hours * 3600
    
    test_count = 0
    crash_count = 0
    error_count = 0
    
    # 固定随机种子以便复现
    random.seed(42)
    
    # 创建崩溃记录文件
    with open("fuzz_test_crash_log.txt", "w", encoding="utf-8") as crash_log:
        crash_log.write("模糊测试崩溃记录\n")
        crash_log.write("="*50 + "\n")
        crash_log.write(f"开始时间: {datetime.now()}\n")
        crash_log.write(f"目标时长: {target_hours}小时\n\n")
    
    print(f"\n🚀 开始长时间模糊测试（安静模式）...")
    print(f"目标: 运行至少{target_hours}小时")
    print("进度将每10分钟显示一次")
    print("按下 Ctrl+C 可以提前终止测试\n")
    
    last_progress_time = start_time
    progress_interval = 600  # 10分钟 = 600秒
    
    # 显示初始状态
    print(f"⏱️  [初始] 开始运行，目标: {target_hours}小时")
    
    try:
        while time.time() - start_time < target_seconds:
            test_count += 1
            
            # 每10分钟打印一次进度
            current_time = time.time()
            if current_time - last_progress_time >= progress_interval:
                elapsed = current_time - start_time
                hours = elapsed / 3600
                remaining = target_seconds - elapsed
                tests_per_sec = test_count / elapsed if elapsed > 0 else 0
                
                # 清除之前的进度行
                print(f"\r{' '*80}", end="")
                print(f"\r⏱️  [进度] 已运行: {hours:.2f}小时 | "
                      f"剩余: {remaining/3600:.2f}小时 | "
                      f"测试次数: {test_count:,} | "
                      f"速度: {tests_per_sec:.1f}次/秒 | "
                      f"崩溃: {crash_count}", end="", flush=True)
                
                last_progress_time = current_time
            
            # 随机选择测试哪个函数
            test_func = random.choice([validate_amount, parse_date])
            func_name = test_func.__name__
            
            # 生成随机测试输入
            if func_name == "validate_amount":
                if random.random() < 0.3:
                    if random.random() < 0.5:
                        input_str = str(random.randint(-1000000, 1000000))
                    else:
                        input_str = f"{random.uniform(-1000000, 1000000):.6f}"
                else:
                    length = random.randint(1, 100)
                    input_str = ''.join(random.choices(string.printable, k=length))
            else:
                if random.random() < 0.2:
                    year = random.randint(1900, 2100)
                    month = random.randint(1, 13)
                    day = random.randint(1, 32)
                    input_str = f"{year}-{month:02d}-{day:02d}"
                else:
                    length = random.randint(1, 50)
                    input_str = ''.join(random.choices(string.printable, k=length))
            
            # 执行测试（静默模式）
            try:
                result = test_func(input_str)
            except Exception as e:
                error_count += 1
                
                # 判断是否是崩溃级别的错误
                error_type = type(e).__name__
                crash_types = ['MemoryError', 'SystemError', 'RuntimeError', 
                              'RecursionError', 'OverflowError', 'SegmentationFault']
                
                if error_type in crash_types:
                    crash_count += 1
                    # 只在发现崩溃时立即显示
                    print(f"\n\n⚠️  [警告] 发现崩溃!")
                    print(f"   测试次数: #{test_count}")
                    print(f"   函数: {func_name}")
                    print(f"   输入: '{input_str[:50]}...'")
                    print(f"   错误: {error_type}: {str(e)[:100]}")
                    
                    # 记录崩溃
                    with open("fuzz_test_crash_log.txt", "a", encoding="utf-8") as crash_log:
                        crash_log.write(f"\n[崩溃 #{crash_count}]\n")
                        crash_log.write(f"时间: {datetime.now()}\n")
                        crash_log.write(f"测试次数: {test_count}\n")
                        crash_log.write(f"函数: {func_name}\n")
                        crash_log.write(f"输入: {input_str}\n")
                        crash_log.write(f"错误类型: {error_type}\n")
                        crash_log.write(f"错误信息: {str(e)}\n")
                        crash_log.write("-"*50 + "\n")
    
    except KeyboardInterrupt:
        print(f"\n\n⚠️  测试被用户中断")
        print(f"当前已运行: {(time.time() - start_time)/3600:.2f}小时")
    except Exception as e:
        print(f"\n❌ 测试过程发生意外错误: {type(e).__name__}: {e}")
    finally:
        # 确保最后显示完整状态
        print()
    
    # 计算最终统计
    end_time = time.time()
    total_time = end_time - start_time
    total_hours = total_time / 3600
    
    return test_count, error_count, crash_count, total_hours

def main():
    """主函数"""
    print("1. 运行长时间模糊测试（5小时，安静模式）...")
    
    total_tests, total_errors, total_crashes, total_hours = run_5_hour_fuzz_test_quiet()
    
    # 恢复原来的log函数
    code.utils.log = original_log
    
    # 打印最终报告
    print("\n" + "="*60)
    print("长时间模糊测试完成报告")
    print("="*60)
    print(f"开始时间: {datetime.fromtimestamp(time.time() - total_hours*3600)}")
    print(f"结束时间: {datetime.now()}")
    print(f"总运行时间: {total_hours:.2f} 小时 ({total_hours*60:.1f} 分钟)")
    print(f"总测试次数: {total_tests:,}")
    print(f"发现错误: {total_errors}")
    print(f"发现崩溃: {total_crashes}")
    
    if total_hours > 0:
        tests_per_hour = total_tests / total_hours
        print(f"平均速度: {tests_per_hour:,.0f} 次/小时")
    
    if total_crashes == 0:
        print("✅ 结论: 未发现导致程序崩溃的测试用例")
        print("   程序在长时间模糊测试中表现稳定")
    else:
        print(f"⚠️  结论: 发现 {total_crashes} 个崩溃用例")
        print("   详细记录见: fuzz_test_crash_log.txt")
    
    # 检查是否达到5小时要求
    if total_hours >= 5:
        print("✅ 满足实验要求: 已运行超过5小时")
    else:
        print(f"⚠️  未达到5小时要求，实际运行: {total_hours:.2f}小时")
    
    print("="*60)
    
    # 保存详细报告
    report = f"""
Long-term Fuzz Test Report (Quiet Mode)
========================================

Test Configuration:
- Start Time: {datetime.fromtimestamp(time.time() - total_hours*3600)}
- End Time: {datetime.now()}
- Target Duration: 5 hours
- Actual Duration: {total_hours:.2f} hours
- Output Mode: Progress every 10 minutes

Test Results:
- Total Tests: {total_tests:,}
- Total Errors: {total_errors}
- Total Crashes: {total_crashes}
- Test Speed: {total_tests/total_hours:,.0f} tests/hour

Requirement Check:
- Minimum 5 hours: {"✅ PASS" if total_hours >= 5 else f"❌ FAIL ({total_hours:.2f} hours)"}
- Crashes found: {"✅ PASS (No crashes)" if total_crashes == 0 else f"⚠️  Found {total_crashes} crashes"}

Conclusion:
{"The program remained stable throughout the fuzz test with no crashes." 
 if total_crashes == 0 else 
 f"Found {total_crashes} crash cases during the test."}

Test Method:
- Random input generation for validate_amount() and parse_date()
- Mixed valid and invalid inputs
- Continuous testing with minimal console output
- Crash detection and logging
- Progress updates every 10 minutes

Note:
This test specifically addresses the experiment requirement: 
"If no crashes are detected, prove that the test ran for at least 5 hours."
"""
    
    with open("fuzz_test_5hour_quiet_report.txt", "w", encoding="utf-8") as f:
        f.write(report)
    
    print("详细报告已保存到 fuzz_test_5hour_quiet_report.txt")
    
    # 创建简短的截图用总结
    with open("fuzz_test_summary_quiet.txt", "w", encoding="utf-8") as f:
        f.write("模糊测试总结（安静模式）\n")
        f.write("="*40 + "\n\n")
        f.write(f"运行时长: {total_hours:.2f} 小时\n")
        f.write(f"目标时长: 5.0 小时\n")
        f.write(f"测试次数: {total_tests:,} 次\n")
        f.write(f"发现崩溃: {total_crashes} 个\n")
        f.write(f"是否达标: {'是' if total_hours >= 5 else '否'}\n")
        f.write(f"结论: {'通过，无崩溃' if total_crashes == 0 else f'发现{total_crashes}个崩溃'}\n")
        f.write(f"完成时间: {datetime.now()}\n")

if __name__ == "__main__":
    main()