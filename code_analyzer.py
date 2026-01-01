import os
import re

def is_gui_auto_generated_line(line):
    """判断一行代码是否为GUI自动生成"""
    gui_patterns = [
        # PyQt/PySide 自动生成代码特征
        r'setGeometry\(.*\)',
        r'setObjectName\(.*\)',
        r'setupUi\(',
        r'retranslateUi',
        r'QtWidgets\.Q[A-Z][a-zA-Z]*\(',
        r'QtCore\.QMetaObject\.connectSlotsByName',
        
        # Tkinter 自动生成代码特征
        r'\.grid\(.*row=.*column=',
        r'\.pack\(.*side=',
        r'\.place\(.*x=.*y=',
        
        # 通用GUI特征
        r'^self\.[a-zA-Z]+[0-9]*\s*=',
        r'^#[^\n]*Auto-generated',
        r'^#[^\n]*Form generated from reading UI file',
        r'\.ui[\'"]',
        
        # 布局相关
        r'addWidget\(.*\)',
        r'addLayout\(.*\)',
        r'setLayout\(.*\)',
    ]
    
    line = line.strip()
    
    # 空行不算
    if not line:
        return False
    
    # 纯注释行不算GUI代码（单独统计）
    if line.startswith('#'):
        return False
    
    for pattern in gui_patterns:
        if re.search(pattern, line, re.IGNORECASE):
            return True
    
    return False

def is_comment_line(line):
    """判断是否为注释行"""
    line = line.strip()
    return line.startswith('#') or line.startswith('"""') or line.startswith("'''")

def analyze_file(filepath):
    """分析单个文件"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except:
        try:
            with open(filepath, 'r', encoding='gbk') as f:
                lines = f.readlines()
        except:
            print(f"无法读取文件: {filepath}")
            return None
    
    total_lines = len(lines)
    gui_lines = 0
    comment_lines = 0
    empty_lines = 0
    business_lines = 0
    
    for line in lines:
        line_stripped = line.strip()
        
        if not line_stripped:
            empty_lines += 1
        elif is_comment_line(line_stripped):
            comment_lines += 1
        elif is_gui_auto_generated_line(line):
            gui_lines += 1
        else:
            business_lines += 1
    
    return {
        'total_lines': total_lines,
        'gui_lines': gui_lines,
        'comment_lines': comment_lines,
        'empty_lines': empty_lines,
        'business_lines': business_lines,
        'filepath': filepath
    }

def analyze_project():
    """分析整个项目"""
    python_files = []
    
    for root, dirs, files in os.walk('.'):
        # 忽略一些常见的不需要分析的目录
        if '__pycache__' in root or '.git' in root or 'venv' in root:
            continue
            
        for file in files:
            if file.endswith('.py') and file != 'code_analyzer.py':
                python_files.append(os.path.join(root, file))
    
    if not python_files:
        print("未找到Python文件！")
        return
    
    total_stats = {
        'total_lines': 0,
        'gui_lines': 0,
        'comment_lines': 0,
        'empty_lines': 0,
        'business_lines': 0,
        'files_count': 0
    }
    
    print("=" * 80)
    print("代码分析报告 - GUI自动生成代码统计")
    print("=" * 80)
    
    file_results = []
    
    for filepath in python_files:
        result = analyze_file(filepath)
        if result:
            file_results.append(result)
            
            # 累加统计
            for key in total_stats:
                if key in result and key != 'filepath':
                    total_stats[key] += result[key]
            total_stats['files_count'] += 1
            
            # 打印文件详情
            filename = os.path.basename(filepath)
            print(f"{filename:<25} | 总行: {result['total_lines']:4d} | "
                  f"GUI: {result['gui_lines']:3d} | "
                  f"业务: {result['business_lines']:4d} | "
                  f"注释: {result['comment_lines']:3d} | "
                  f"空行: {result['empty_lines']:3d}")
    
    print("=" * 80)
    
    # 打印汇总统计
    if total_stats['total_lines'] > 0:
        gui_percentage = (total_stats['gui_lines'] / total_stats['total_lines']) * 100
        business_percentage = (total_stats['business_lines'] / total_stats['total_lines']) * 100
        
        print(f"\n📊 汇总统计:")
        print(f"📁 文件数量: {total_stats['files_count']} 个")
        print(f"📄 总代码行数: {total_stats['total_lines']} 行")
        print(f"🎨 GUI自动生成代码: {total_stats['gui_lines']} 行 ({gui_percentage:.1f}%)")
        print(f"💼 有效业务代码: {total_stats['business_lines']} 行 ({business_percentage:.1f}%)")
        print(f"💬 注释行数: {total_stats['comment_lines']} 行")
        print(f"⬜ 空行数: {total_stats['empty_lines']} 行")
        
        print(f"\n🎯 您的实际代码量(不含GUI): {total_stats['business_lines']} 行")
        
        # 建议
        if gui_percentage > 30:
            print(f"\n💡 建议: GUI代码占比较高({gui_percentage:.1f}%)，考虑重构UI代码")
        else:
            print(f"\n✅ 良好: GUI代码占比合理({gui_percentage:.1f}%)")

if __name__ == "__main__":
    analyze_project()