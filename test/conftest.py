"""
测试配置文件
"""

import sys
import os
import importlib

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath('.'))

# 修复utils模块的导入问题
def setup_utils_module():
    """设置utils模块的正确导入"""
    try:
        # 动态设置utils模块的属性
        utils_module = importlib.import_module('code.utils')
        
        # 确保utils模块有必要的属性
        if not hasattr(utils_module, 'os'):
            import os as os_module
            utils_module.os = os_module
            
        if not hasattr(utils_module, 'subprocess'):
            import subprocess as subprocess_module
            utils_module.subprocess = subprocess_module
            
    except ImportError as e:
        print(f"警告：导入utils模块时出错: {e}")

# 在pytest启动时运行
setup_utils_module()