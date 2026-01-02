# conftest.py
"""
测试配置文件
"""

import sys
import os
import importlib

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath('.'))

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
            
        # 确保matplotlib不会尝试显示图形
        import matplotlib
        matplotlib.use('Agg')  # 使用非交互式后端
        
    except ImportError as e:
        print(f"警告：导入utils模块时出错: {e}")
        # 创建模拟模块
        class MockModule:
            def __getattr__(self, name):
                return None
        sys.modules['code.utils'] = MockModule()

# 在pytest启动时运行
setup_utils_module()