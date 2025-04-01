
import sys, os, re, math, datetime, collections
from io import StringIO
import signal
import json
from functools import wraps
from utils.logger import logger


class TimeoutException(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutException("代码执行超时")

# 超时装饰器
def timeout(seconds):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 设置信号处理器
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                # 取消警报
                signal.alarm(0)
            return result
        return wrapper
    return decorator

def execute_with_timeout(code, timeout=5):
    """使用线程池执行代码，支持超时"""
    output = StringIO()

def safe_import(name, globals=None, locals=None, fromlist=(), level=0):
    """安全的导入函数，只允许导入白名单中的模块"""
    ALLOWED_MODULES = {
        'json': __import__('json'),
        'math': __import__('math'),
        'datetime': __import__('datetime'),
        'os': __import__('os'),
    }
    if name not in ALLOWED_MODULES:
        raise ImportError(f"Module {name} is not allowed")
    return ALLOWED_MODULES[name]

def run_code(code, output):
    original_stdout = sys.stdout
    # 添加常用的数据处理库
    safe_modules = {
        'json': json,
        'os': os,
        'sys': sys,
        're': re,
        'math': math,
        'datetime': datetime,
        'collections': collections,
    }
    # 创建安全的执行环境
    namespace = {
        '__builtins__': {
            'print': lambda *args, **kwargs: print(*args, **kwargs, file=output),
            'len': len,
            'range': range,
            'str': str,
            'int': int,
            'float': float,
            'list': list,
            'dict': dict,
            'sum': sum,
            'min': min,
            'max': max,
            'bool': bool,
            'tuple': tuple,
            'set': set,
            'enumerate': enumerate,
            'zip': zip,
            'round': round,
            'abs': abs,
            'all': all,
            'any': any,
            'sorted': sorted,
            'reversed': reversed,
            'isinstance': isinstance,
            'type': type,
            'hasattr': hasattr,       # 可能需要的其他类型检查函数
            'getattr': getattr,
            'setattr': setattr,
            '__import__': safe_import,  # 添加 __import__ 函数
            'ValueError': ValueError,  # 添加常用异常类
            'TypeError': TypeError,
            'Exception': Exception,
            # 可以添加其他需要的异常类或模
            'input_data': {},
        },
        '__name__': '__main__',
        'True': True,
        'False': False,
        'None': None,
    }
    namespace.update(safe_modules)
    # 重定向标准输出
    sys.stdout = output
    try:
        logger.debug("Starting code execution")
        logger.debug(f"Code to execute:\n{code}")

        # 先编译代码
        compiled_code = compile(code, '<string>', 'exec')
        # 添加调试信息
        exec(compiled_code, namespace)
        logger.debug("Code executed successfully")
        
        # 检查是否有生成指令函数
        if 'generate_instruction' in namespace:
            logger.debug("Found generate_instruction function")
            if 'input_data' in namespace:
                result = namespace['generate_instruction'](namespace['input_data'])
                logger.debug(f"Function result: {result}")
                return result
            else:
                logger.warning("input_data not found in namespace")
                return None
        else:
            logger.warning("generate_instruction function not found")
            # 返回所有print输出
            return output.getvalue()

    except Exception as e:
        logger.error(f"Code execution error: {str(e)}")
        raise Exception(f"代码执行错误: {str(e)}")
    finally:
        sys.stdout = original_stdout


def process_markdown_code(markdown_code: str, input_path: str) -> str:
    """
    处理markdown格式的代码，提取其中的Python代码并添加main执行部分
    
    Args:
        markdown_code: 包含```python ```格式的markdown代码字符串
    
    Returns:
        处理后的Python代码字符串
    """
    # 提取```python 和 ``` 之间的代码
    try:
        # 查找代码块的开始和结束
        start_index = markdown_code.find('```python\n') + len('```python\n')
        end_index = markdown_code.find('```', start_index)
        
        if start_index == -1 or end_index == -1:
            raise ValueError("未找到有效的Python代码块")
        
        # 提取代码
        code = markdown_code[start_index:end_index].strip()

        with open(input_path, 'r') as f:
            input = json.load(f)
        
        # 添加main部分
        main_code = f"""\n\n
if __name__ == '__main__':
    # 测试数据
    input_data = {input}
"""
        
        # 组合完整代码
        complete_code = code + main_code
        
        return complete_code
        
    except Exception as e:
        return f"处理代码时出错: {str(e)}"


def get_executed_python_code(markdown_code: str) -> str:
    try:
        # 查找代码块的开始和结束
        start_index = markdown_code.find('```python\n') + len('```python\n')
        end_index = markdown_code.find('```', start_index)
        
        if start_index == -1 or end_index == -1:
            raise ValueError("未找到有效的Python代码块")
        
        # 提取代码
        executed_code = markdown_code[start_index:end_index].strip()

        return executed_code

    except Exception as e:
        return f"处理代码时出错: {str(e)}"

def format_output(result: dict) -> str:
    """格式化输出结果"""
    if isinstance(result, dict):
        return json.dumps(result, indent=4, ensure_ascii=False)
    else:
        return str(result)

def print_step(step_num: int, message: str):
    """打印步骤信息"""
    print(f"\n{'='*50}")
    print(f"Step {step_num}: {message}")
    print(f"{'='*50}\n")

def print_result(title: str, content):
    """打印结果信息"""
    print(f"\n{'-'*20} {title} {'-'*20}")
    print(content)
    print(f"{'-'*50}\n")


def label_adjustment(pred, gt):
    """
    Compares whether the predicted value and the actual value are the same, only designed for the current data set.
    
    Args:
        pred: predicted value
        gt: true value
        
    Returns:
        bool: whether they are the same
    """
    if pred == gt:
        return True
    # 特殊情况的判断
    phase_pairs = [
        ('BC相', 'BC相'),
        ('AC相', 'AC相'),
        ('AB相', 'AB相'),
        ('A相', 'A相'),
        ('B相', 'B相'),
        ('C相', 'C相')
    ]
    return any(p1 in pred and p1 in gt for p1, _ in phase_pairs)