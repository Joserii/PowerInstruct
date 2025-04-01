
import sys, os, re, math, datetime, collections
from io import StringIO
import signal
import json
from functools import wraps
from utils.logger import logger


class TimeoutException(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutException("Code execution timeout")

# Timeout decorator
def timeout(seconds):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Set up the signal handler
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                # Cancel the alarm
                signal.alarm(0)
            return result
        return wrapper
    return decorator

def execute_with_timeout(code, timeout=5):
    """Use thread pool to execute code, support timeout"""
    output = StringIO()

def safe_import(name, globals=None, locals=None, fromlist=(), level=0):
    """Safe import function, only allows importing modules in the whitelist"""
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
    # Add commonly used data processing libraries
    safe_modules = {
        'json': json,
        'os': os,
        'sys': sys,
        're': re,
        'math': math,
        'datetime': datetime,
        'collections': collections,
    }
    # Create a secure execution environment
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
            'hasattr': hasattr,       # Other type checking functions that may be needed
            'getattr': getattr,
            'setattr': setattr,
            '__import__': safe_import,  # Add __import__ function
            'ValueError': ValueError,  # Add common exception classes
            'TypeError': TypeError,
            'Exception': Exception,
            # You can add other required exception classes or models
            'input_data': {},
        },
        '__name__': '__main__',
        'True': True,
        'False': False,
        'None': None,
    }
    namespace.update(safe_modules)
    # Redirect standard output
    sys.stdout = output
    try:
        logger.debug("Starting code execution")
        logger.debug(f"Code to execute:\n{code}")

        # Compile the code first
        compiled_code = compile(code, '<string>', 'exec')
        # Add debugging information
        exec(compiled_code, namespace)
        logger.debug("Code executed successfully")
        
        # Check if there is a generated instruction function
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
            # Return all print output
            return output.getvalue()

    except Exception as e:
        logger.error(f"Code execution error: {str(e)}")
        raise Exception(f"Code execution error: {str(e)}")
    finally:
        sys.stdout = original_stdout


def process_markdown_code(markdown_code: str, input_path: str) -> str:
    """
    Process the code in markdown format, extract the Python code and add the main execution part

    Args:
    markdown_code: contains the markdown code string in the format of ```python```

    Returns:
    Processed Python code string
    """
    # Extract the code between ```python and ```
    try:
        # Find the start and end of a code block
        start_index = markdown_code.find('```python\n') + len('```python\n')
        end_index = markdown_code.find('```', start_index)
        
        if start_index == -1 or end_index == -1:
            raise ValueError("No valid Python code block found")
        
        # Extract code
        code = markdown_code[start_index:end_index].strip()

        with open(input_path, 'r') as f:
            input = json.load(f)
        
        # Add the main function
        main_code = f"""\n\n
if __name__ == '__main__':
    input_data = {input}
"""
        
        # Combined complete code
        complete_code = code + main_code
        
        return complete_code
        
    except Exception as e:
        return f"Error processing code: {str(e)}"


def get_executed_python_code(markdown_code: str) -> str:
    try:
        # Find the start and end of a code block
        start_index = markdown_code.find('```python\n') + len('```python\n')
        end_index = markdown_code.find('```', start_index)
        
        if start_index == -1 or end_index == -1:
            raise ValueError("No valid Python code block found")
        
        # 提取代码
        executed_code = markdown_code[start_index:end_index].strip()

        return executed_code

    except Exception as e:
        return f"Error processing code: {str(e)}"

def format_output(result: dict) -> str:
    """Format output results"""
    if isinstance(result, dict):
        return json.dumps(result, indent=4, ensure_ascii=False)
    else:
        return str(result)

def print_step(step_num: int, message: str):
    """Print step information"""
    print(f"\n{'='*50}")
    print(f"Step {step_num}: {message}")
    print(f"{'='*50}\n")

def print_result(title: str, content):
    """Print result information"""
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
    phase_pairs = [
        ('BC相', 'BC相'),
        ('AC相', 'AC相'),
        ('AB相', 'AB相'),
        ('A相', 'A相'),
        ('B相', 'B相'),
        ('C相', 'C相')
    ]
    return any(p1 in pred and p1 in gt for p1, _ in phase_pairs)