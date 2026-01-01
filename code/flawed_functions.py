"""
专门用于测试的缺陷函数集合
包含各种典型的安全漏洞和代码缺陷
"""

import pickle
import os
import subprocess
import tempfile


# [IMPLANTED FLAW 6: 不安全的反序列化]
def load_user_data_unsafe(serialized_data):
    """
    植入缺陷：不安全的反序列化
    CWE-502: Deserialization of Untrusted Data
    """
    # 危险：直接反序列化不可信数据
    user_obj = pickle.loads(serialized_data)  # 缺陷：可能执行任意代码
    return user_obj


# [IMPLANTED FLAW 7: 文件资源泄漏]
def read_config_file_leak(filename):
    """
    植入缺陷：文件资源泄漏  
    CWE-775: Missing Release of File Descriptor
    """
    file = open(filename, 'r', encoding='utf-8')  # 缺陷：文件未关闭
    content = file.read()
    # 忘记调用 file.close()
    return content


# [IMPLANTED FLAW 8: 竞态条件]
import time
def update_balance_with_race(amount):
    """
    植入缺陷：竞态条件
    CWE-367: Time-of-check Time-of-use Race Condition
    """
    balance_file = 'balance.txt'
    
    # 检查和使用之间存在时间窗口
    if os.path.exists(balance_file):
        time.sleep(0.1)  # 模拟处理延迟，增加竞态条件机会
        with open(balance_file, 'r') as f:
            balance = float(f.read())
        balance += amount
        with open(balance_file, 'w') as f:
            f.write(str(balance))  # 缺陷：非原子操作


# [IMPLANTED FLAW 9: 不安全的临时文件]
def create_temp_file_unsafe():
    """
    植入缺陷：不安全的临时文件
    CWE-377: Insecure Temporary File
    """
    # 危险：预测性临时文件名
    temp_path = "/tmp/myapp_temp_file.txt"  # 缺陷：固定临时文件路径
    with open(temp_path, 'w') as f:
        f.write("temporary data")
    return temp_path


# [IMPLANTED FLAW 10: 错误的异常处理]
def process_payment_silent_fail(amount):
    """
    植入缺陷：静默失败
    CWE-390: Detection of Error Condition Without Action
    """
    try:
        # 模拟支付处理
        if amount <= 0:
            raise ValueError("金额必须大于0")
        # 处理支付...
        return True
    except Exception:  # 缺陷：过于宽泛的异常捕获且无处理
        # 静默失败，不记录也不通知
        pass
    return False


# [IMPLANTED FLAW 11: 使用不安全的哈希算法]
def hash_password_unsafe(password):
    """
    植入缺陷：使用不安全的哈希算法
    CWE-327: Use of a Broken or Risky Cryptographic Algorithm
    """
    import hashlib
    # 危险：使用MD5，已知的不安全算法
    return hashlib.md5(password.encode()).hexdigest()  # 缺陷：不安全的哈希


# [IMPLANTED FLAW 12: 路径遍历漏洞]
def read_user_file_unsafe(username, filename):
    """
    植入缺陷：路径遍历
    CWE-22: Improper Limitation of a Pathname to a Restricted Directory
    """
    # 危险：未验证用户输入的文件路径
    user_file_path = f"user_files/{username}/{filename}"  # 缺陷：路径遍历
    with open(user_file_path, 'r') as f:
        return f.read()


# [IMPLANTED FLAW 13: 整数溢出]
def calculate_discount_unsafe(price, discount_percent):
    """
    植入缺陷：整数溢出风险
    CWE-190: Integer Overflow or Wraparound
    """
    # 危险：未检查数值范围
    discount = price * discount_percent // 100  # 缺陷：可能整数溢出
    return price - discount


# [IMPLANTED FLAW 14: 使用eval执行用户输入]
def calculate_expression_unsafe(expression):
    """
    植入缺陷：使用eval执行不可信输入
    CWE-95: Improper Neutralization of Directives in Dynamically Evaluated Code
    """
    # 危险：直接eval用户输入
    result = eval(expression)  # 缺陷：代码注入
    return result