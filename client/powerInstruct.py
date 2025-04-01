import sys
import os
import ast
import random
import json
import time
from io import StringIO
from typing import Dict, List, Any
import requests
from requests.exceptions import RequestException
import argparse

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.prompt_template.codegen_prompt import *
from utils.prompt_template.directgen_prompt import *
from utils.run_python_utils import *
from utils.file_utils import *
from utils.logger import logger
from utils.idealab_utils import idealab_request
from utils.metrics import MetricsCollector


import datetime

# acl demo 最终版本，循环部分的代码
OUTPUT_BASE_DIR = "output"
CURRENT_TIME = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
CURRENT_OUTPUT_DIR = os.path.join(OUTPUT_BASE_DIR, CURRENT_TIME)

ALLTYPE_FET_SHOT_DATA_DIR = os.path.join(TEST_DATA_FOLDER, 'few_shot_data.json')
ALL_DATA_DIR = os.path.join(TEST_DATA_FOLDER, 'classified_all_data_including_gt.json')

SUPPORT_MODEL_REF = [
    "gpt-4o-mini-0718", "gpt-4o-0806", "gpt-4-0409",
    "gemini-1.5-pro", "gemini-1.5-pro-flash",
    "qwen_max", "qwen2.5-72b-instruct", "qwen2.5-7b-instruct",
    "claude35_sonnet", 

    "o1-preview-0912", "o1-mini-0912",
    "qwq-32b", "qwen_max"
]

# 常量定义
# TOTAL_DATA_DIR = "/Users/czy/projects/baohuchu_demo/data/test_data/1049个训练样本-1016_20250324_180309_ce79e70008f87ff1.json"
# TOTAL_DATA_DIR = "/Users/czy/projects/baohuchu_demo/data/test_data/102个测试样本-1015_20250307_173953_318ee91831f5aaac.json"
OUTPUT_FILE = "batch_results.json"
metrics = MetricsCollector()


def parse_args():
    parser = argparse.ArgumentParser(description="PowerInstruct 迭代acc初始化参数")
    parser.add_argument('--output_dir', type=str, default=CURRENT_OUTPUT_DIR, help='Base directory for output files')
    parser.add_argument('--total_data_dir', type=str, 
                        default="/Users/czy/projects/baohuchu_demo/data/test_data/1049个训练样本-1016_20250324_180309_ce79e70008f87ff1.json",
                        help='Path to total data file')
    # API相关参数
    parser.add_argument('--api_url', type=str, default="http://localhost:5000/analyze",
                        help='API URL for analysis')
    parser.add_argument('--clean_url', type=str, default='http://localhost:5000/clean',
                        help='API URL for data cleaning')

    # 模型选择参数
    parser.add_argument('--model_datagen', type=str, default="gpt-4o-0806",
                        help='Model ID for data generation')
    parser.add_argument('--model_codegen', type=str, default="qwen_max",
                        help='Model ID for code generation')

    # PowerInstruct 迭代参数
    parser.add_argument('--max_iterations', type=int, default=5,
                        help='Maximum number of iterations')
    parser.add_argument('--min_accuacy', type=float, default=0.95,
                        help='Accuracy threshold')
    parser.add_argument('--delta_accuracy', type=float, default=0.01,
                        help='Minimum improvement threshold')
    parser.add_argument('--test_sample_ratio', type=float, default=0.5,
                        help='Number of test samples')
    parser.add_argument('--max_failures', type=int, default=2,
                        help='Maximum number of failure cases to collect')

    args = parser.parse_args()
    return args


def select_random_data(data) -> Dict[str, Any]:
    """
    从数据文件中随机选择一条数据
    Args:
        data_path: 数据文件路径
    Returns:
        包含ID和数据的字典
    Raises:
        ValueError: 当数据读取失败时
    """
    try:
        batch_data = data
            
        if not batch_data:
            raise ValueError("数据列表为空")
            
        id_ = random.randint(0, len(batch_data) - 1)
        random_data = batch_data[id_]
        
        logger.info(f"随机选择的数据ID: {id_}")
        logger.debug(f"随机选择的数据: {random_data}")
        
        return {
            "id": id_,
            "data": random_data
        }
    except Exception as e:
        logger.error(f"读取数据出错: {str(e)}")
        raise ValueError(f"读取数据出错: {str(e)}")
    

def save_results(args, results: Dict[str, Any], filename: str = "batch_results.json") -> None:
    """保存最终结果"""
    try:
        # 确保输出目录存在
        os.makedirs(args.output_dir, exist_ok=True)
        
        # 使用时间戳目录
        output_file = os.path.join(args.output_dir, filename)
        
        with open(output_file, "w", encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        accuracy = convert_result_to_chat(args, source_file=output_file)
        logger.info(f"结果已保存到: {filename}")

    except Exception as e:
        logger.error(f"保存结果失败: {str(e)}")
        raise


def get_standard_data(args, single_data: Dict[str, Any], max_retries: int = 3, retry_delay: int = 5) -> str:
    """
    Extract standard data format from a single piece of data
    
    Args:
        single_data: input single data
        max_retries: Maximum number of retries
        retry_delay: Delay between each retry (seconds)
        
    Returns:
        Standard format data string
    """
    if not single_data:
        raise ValueError("Input data is empty.")
    
    for attempt in range(max_retries + 1):
        try:
            data = {
                "filepath": args.total_data_dir,
                "mode": "prompt",
                "file_content": str(single_data),
                "template": datagen_1shot_system_prompt(),
                "model_id": args.model_datagen,
            }

            response = requests.post(args.api_url, json=data, timeout=120).json()
            ai_response = response.get("ai_response")
            token_prompt, token_cli = response.get("token_prompt", 0), response.get("token_compli", 0)
            metrics.add_tokens(token_prompt, token_cli)
            
            if ai_response:
                logger.info("Successfully obtained standard data format")
                return ai_response
            
            logger.warning(f"AI response is empty, try the {attempt + 1} times")
            if attempt < max_retries:
                time.sleep(retry_delay)
            else:
                raise ValueError("AI response remains empty after multiple attempts")
                
        except RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            if attempt < max_retries:
                time.sleep(retry_delay)
            else:
                raise


def generate_code(args, prompt: str, max_retries: int = 3, retry_delay: int = 5) -> str:
    """
    Generate executable Python code
    
    Args:
        prompt: Input prompt for code generation
        max_retries: Maximum number of retries
        retry_delay: Delay between each retry (seconds)
        
    Returns:
        Executable Python code
    """
    for attempt in range(max_retries + 1):
        try:
            data = {
                "filepath": args.total_data_dir,
                "mode": "codegen",
                "file_content": str(prompt),            # prompt is here
                "template": codegen_1shot_system_prompt(), # not used
                "model_id": args.model_codegen,
            }
            
            response = requests.post(args.api_url, json=data, timeout=180).json()

            ai_response = response.get("ai_response")
            token_prompt, token_cli = response.get("token_prompt"), response.get("token_compli")
            metrics.add_tokens(token_prompt, token_cli)
            
            if ai_response:
                executed_code = get_executed_python_code(ai_response)
                logger.debug(f"Generated code: {executed_code}")
                logger.info(f"Successfully generated code on attempt {attempt + 1}")
                return executed_code
            
            logger.warning(f"AI response is empty, attempt {attempt + 1} of {max_retries + 1}")
            if attempt < max_retries:
                time.sleep(retry_delay)
            else:
                raise ValueError("AI response remains empty after multiple attempts")
                
        except RequestException as e:
            logger.error(f"API request failed on attempt {attempt + 1}: {str(e)}")
            if attempt < max_retries:
                time.sleep(retry_delay)
                continue
            raise
        except Exception as e:
            logger.error(f"Code generation failed on attempt {attempt + 1}: {str(e)}")
            if attempt < max_retries:
                time.sleep(retry_delay)
                continue
            raise

def concat_input(executed_code: str, input_data: Dict[str, Any]) -> str:
    """concat code and input data"""
    main_code = f"""\n\n
if __name__ == '__main__':
    # test data
    input_data = {input_data}
"""
    return executed_code + main_code

def run_single_data(executed_code: str, input_data: Dict[str, Any]) -> Any:
    """
    执行单条数据的代码，增加数据验证和错误处理
    
    Args:
        executed_code: 要执行的Python代码
        input_data: 输入数据
        
    Returns:
        处理结果
    """
    output = StringIO()
    try:
        # 1. 数据验证
        if not input_data or not isinstance(input_data, dict):
            raise ValueError("输入数据无效")
            
        # 2. 获取实际的数据（因为之前的select_random_data返回的是带id的字典）
        actual_data = input_data.get('data') if 'data' in input_data else input_data
        
        # 3. 执行代码
        final_code = concat_input(executed_code, actual_data)
        
        try:
            result = run_code(code=final_code, output=output)
            logger.debug(f"代码执行结果: {result}")
        except Exception as e:
            logger.error(f"代码执行错误: {str(e)}")
            return {
                'code': 500,
                'success': False,
                'error': str(e),
                'input_data': actual_data
            }
        
        # 4. 处理结果
        stdout_content = output.getvalue()
        formatted_output = format_output(result)
        
        return {
            'code': 200,
            'success': True,
            'result': str(formatted_output),
            'stdout': stdout_content,
            'executed_code': executed_code
        }
        
    except Exception as e:
        error_msg = f"处理数据失败: {str(e)}"
        logger.error(error_msg)
        return {
            'code': 500,
            'success': False,
            'error': error_msg,
            'input_data': input_data
        }

def run_batch_data(args, total_data_dir: str, executed_code: str) -> Dict[str, Any]:
    """
    批量执行数据处理
    
    Args:
        total_data_dir: 数据文件路径
        executed_code: 要执行的代码
        
    Returns:
        Dict containing:
            - success_results: 成功处理的结果列表
            - failed_results: 失败的数据及错误信息
            - statistics: 处理统计信息
    """
    try:
        with open(total_data_dir, "r", encoding='utf-8') as f:
            batch_data = json.load(f)
            
        if not batch_data:
            raise ValueError("数据列表为空")
            
        success_results = []
        failed_results = []
        total = len(batch_data)
        success_count = 0
        failure_count = 0
        
        for i, data in enumerate(batch_data, 1):
            # import ipdb; ipdb.set_trace()
            try:
                
                # 数据验证
                if not isinstance(data, dict):
                    raise ValueError(f"数据格式错误: 期望dict类型，实际为{type(data)}")
                
                # 执行处理
                result = run_single_data(executed_code=executed_code, input_data=data)
                
                success_results.append({
                    "index": i-1,
                    "input": data,
                    "result": result
                })
                success_count += 1
                
            except Exception as e:
                failure_count += 1
                error_info = {
                    "index": i-1,
                    "input": data,
                    "error": str(e),
                    "error_type": type(e).__name__
                }
                failed_results.append(error_info)
                logger.error(f"处理第 {i} 条数据失败: {str(e)}")
                continue  # 继续处理下一条数据
                
        # 统计信息
        statistics = {
            "total": total,
            "success": success_count,
            "failure": failure_count,
            "success_rate": f"{(success_count/total)*100:.2f}%"
        }
        
        # 保存最终结果
        final_results = {
            "success_results": success_results,
            "failed_results": failed_results,
            "statistics": statistics
        }
        
        # 保存到文件
        save_results(args, final_results)
        
        logger.info(f"处理完成. 成功: {success_count}, 失败: {failure_count}")
        return final_results
        
    except Exception as e:
        print(f"\n处理第 {i} 条数据失败: {str(e)}")
        logger.error(f"批量处理失败: {str(e)}")
        raise

def convert_result_to_chat(args, source_file: str, target_filename: str = 'chat_results.json'):
    """
    将原始结果文件转换为聊天格式
    
    Args:
        source_file: 源文件路径
        target_file: 目标文件路径
    """
    try:
        # 读取源文件
        with open(source_file, 'r', encoding='utf-8') as f:
            source_data = json.load(f)
        
        chat_results = []
        target_filedir = os.path.join(args.output_dir, target_filename)
        test_result_dir = os.path.join(args.output_dir, 'test_results.json')

        # 用于统计正确率
        total_count = 0
        correct_count = 0
        
        # 处理每个成功的结果
        for item in source_data.get('success_results', []):
            try:
                # 获取原始result字符串并解析
                result_str = item['result']['result']
                result_dict = json.loads(result_str)
                gt = item['input']['gt']
                # 解析嵌套的JSON字符串
                pred = ast.literal_eval(result_dict['output'])['故障分类']

                # 创建聊天格式的结果
                chat_result = {
                    "index": item['index'],
                    "chat": [
                        {
                            "role": "Human",
                            "content": result_dict['input'],
                            "metadata": {
                                "language": "cn",
                                "task": "BaohuchuFenlei.Q"
                            }
                        },
                        {
                            "role": "Assistant",
                            "content": result_dict['output'],
                            "metadata": {
                                "language": "cn",
                                "task": "BaohuchuFenlei.A"
                            }
                        }
                    ],
                    "metadata": {
                        "language": "cn",
                        "gt": gt,
                        "pred": pred
                    }
                }
                
                
                total_count += 1
                correct_count += label_adjustment(gt, pred)
                # correct_count += (gt == pred)
                
                
                chat_results.append(chat_result)
                
            except Exception as e:
                print(f"处理索引 {item['index']} 时出错: {str(e)}")
                # 计算正确率
        
        accuracy = correct_count / total_count if total_count > 0 else 0
        accuracy_percentage = f"{accuracy * 100:.2f}%"
        
        # 创建包含统计信息的结果
        final_results = {
            "statistics": {
                "total_samples": total_count,
                "correct_predictions": correct_count,
                "accuracy": accuracy_percentage
            },
            "results": chat_results
        }
        with open(test_result_dir, 'w', encoding='utf-8') as f:
            json.dump(final_results, f, ensure_ascii=False, indent=2)   
        
        # 保存转换后的结果
        with open(target_filedir, 'w', encoding='utf-8') as f:
            json.dump(chat_results, f, ensure_ascii=False, indent=2)
            
        print(f"转换完成，共处理 {len(chat_results)} 条记录")
        print(f"预测正确率: {accuracy_percentage} ({correct_count}/{total_count})")
        return accuracy
    

    except Exception as e:
        print(f"转换过程出错: {str(e)}")
        raise

def data_cleaning(args, data):
    try:
        response = requests.post(args.clean_url, json=data, timeout=30).json()
        processed_data = response.get('cleaned_data', [])
        print(f"cleaned data: {len(processed_data)}")
        return processed_data
    
    except:
        logger.error("failed to clean data")
        raise


def _evaluate_code(executed_code, test_samples):
    """评估代码在测试样本上的表现"""
    # 用于统计正确率
    total_count = 0
    correct_count = 0

    failure_cases = []
    max_failures = 3

    for i, data in enumerate(test_samples):
        try:
            # 数据验证
            if not isinstance(data, dict):
                raise ValueError(f"数据格式错误: 期望dict类型，实际为{type(data)}")
            
            # 执行处理
            result = run_single_data(executed_code=executed_code, input_data=data)
             
            # 解析结果
            result_str = result['result']
            result_dict = json.loads(result_str)
            gt = data['gt']
            # import ipdb; ipdb.set_trace()
            # 检查输出格式是否正确
            try:
                output_dict = ast.literal_eval(result_dict['output'])
                if '故障分类' not in output_dict:
                    raise KeyError("输出结果中缺少'故障分类'字段")
                pred = output_dict['故障分类']

            except (KeyError, ValueError, SyntaxError) as e:
                # 如果解析失败或缺少字段，记录为失败案例
                if len(failure_cases) < max_failures:
                    failure_cases.append({
                        'index': i,
                        'input': data,
                        'ground_truth': gt,
                        'prediction': 'FORMAT_ERROR',
                        'error_message': f"输出格式错误: {str(e)}",
                        'raw_output': result_dict.get('output', 'No output')
                    })
                total_count += 1
                continue
            
            total_count += 1
            is_correct = label_adjustment(gt, pred)
            correct_count += is_correct

            # import ipdb; ipdb.set_trace()
            # correct_count += (gt == pred)

            # 收集失败样例
            if not is_correct and len(failure_cases) < max_failures:
                failure_cases.append({
                    'index': i,
                    'input': data,
                    'ground_truth': gt,
                    'prediction': pred,
                    'error_type': 'PREDICTION_ERROR',
                    'error_message': f"预测结果错误: 预期 {gt}, 实际 {pred}"
                })
            
        except Exception as e:
            print(f"处理第 {i} 条数据失败: {str(e)}")
            logger.error(f"处理第 {i} 条数据失败: {str(e)}")

            # 记录执行异常的失败案例
            if len(failure_cases) < max_failures:
                failure_cases.append({
                    'index': i,
                    'input': data,
                    'ground_truth': data.get('gt', 'Unknown'),  # 防止gt不存在
                    'error_type': 'EXECUTION_ERROR',
                    'error_message': str(e),
                    'error_class': e.__class__.__name__
                })
            total_count += 1  # 异常也计入总数
            continue
    print(f"total count: {total_count}, correct_count: {correct_count}")
    accuracy = correct_count / total_count if total_count > 0 else 0
    return accuracy, failure_cases

def format_failed_cases(failed_cases):
    """将失败案例格式化为更易理解的形式"""
    formatted_cases = []
    for i, case in enumerate(failed_cases, 1):
        error_type = case.get('error_type', 'Unknown')
        formatted_case = f"\n案例 {i}:\n"
        
        # 添加输入数据的关键信息
        input_data = case.get('input', {})
        formatted_case += f"输入数据: {json.dumps(input_data, ensure_ascii=False, indent=2)}\n"
        
        # 根据错误类型添加不同的信息
        if error_type == 'PREDICTION_ERROR':
            formatted_case += f"预期输出: {case.get('ground_truth')}\n"
            formatted_case += f"实际输出: {case.get('prediction')}\n"
        elif error_type == 'FORMAT_ERROR':
            formatted_case += f"格式错误: {case.get('error_message')}\n"
            formatted_case += f"原始输出: {case.get('raw_output')}\n"
        elif error_type == 'EXECUTION_ERROR':
            formatted_case += f"执行错误: {case.get('error_message')}\n"
            formatted_case += f"错误类型: {case.get('error_class')}\n"
            
        formatted_cases.append(formatted_case)
    
    return "\n".join(formatted_cases)


def _get_llm_feedback(args, current_code, failed_cases):
    # 对失败案例进行分类统计
    error_stats = {}
    for case in failed_cases:
        error_type = case.get('error_type', 'Unknown')
        error_stats[error_type] = error_stats.get(error_type, 0) + 1
    
    # 格式化失败案例
    formatted_cases = format_failed_cases(failed_cases)

    # import ipdb; ipdb.set_trace()

    feedback_prompt = f"""请作为一个Python编程以及代码优化专家，帮助分析和改进以下Python代码。
当前代码：
```python
{current_code}
失败统计：
{json.dumps(error_stats, indent=2, ensure_ascii=False)}
典型失败案例：
{formatted_cases}
请按照以下步骤提供分析和建议：
1. 错误模式分析：识别代码中的主要问题模式,分析每种错误类型的可能原因
2. 改进建议：提供具体的代码修改建议,说明每个修改的目的和预期效果
3. 健壮性增强：建议添加的错误处理机制;提供输入验证和异常处理的改进方案;请提供详细的代码示例和解释。
下面请开始分析失败原因：
"""
    # import ipdb; ipdb.set_trace()
    feedback_from_llm, token_prompt, token_cli = idealab_request(feedback_prompt, model=args.model_codegen)
    metrics.add_tokens(token_prompt, token_cli)

    return feedback_from_llm


def iterative_code_generation(args, processed_data, current_code):
    cnt = 0                 # iteration counter
    prev_accuracy = 0       # previous accuracy
    best_code = None        # best code
    best_accuracy = 0       # best accuracy
    failed_cases = []       # failed cases
    test_sample_size = int(args.test_sample_ratio * len(processed_data))

    while cnt < args.max_iterations:
        print(f"{cnt+1}th iteration")
        metrics.start_step(f"iteration_{cnt}")
        # a. Randomly select some samples
        test_samples = random.sample(processed_data, test_sample_size)
        # b. Evaluate code
        current_acc, failure_cases = _evaluate_code(current_code, test_samples)
        metrics.add_iteration(cnt, current_acc, len(failed_cases))

        print(f"The current accuracy is {current_acc:.4f}")
        logger.info(f"The {cnt+1}th iteration accuracy is {current_acc:.4f}")

        # Update best results
        if current_acc > best_accuracy:
            best_accuracy = current_acc
            best_code = current_code
        
        # c. Check the termination condition
        if current_acc > args.min_accuacy:
            print("The accuracy reaches the threshold and the iteration stops.")
            break
        
        accuracy_improvement = current_acc - prev_accuracy
        if cnt > 0 and accuracy_improvement < args.delta_accuracy:
            print("Accuracy is not improved, stop iteration")
            break
        
        # Collect failure cases
        failed_cases = [r for r in failure_cases if not r.get('success')]
        if not failed_cases:
            print("No failure cases, continue iteration")
            break

        # use strong LLM to get feedback
        feedback = _get_llm_feedback(args, current_code, failed_cases) 

        # import ipdb; ipdb.set_trace()
        # TODO: use new feedback prompt to generate new code
        improvement_prompt = f"""你是一个专业的Python代码优化专家。请基于以下信息生成改进后的代码：
1. 当前代码:
```python
{current_code}
2. 分析反馈:
基于以下反馈优化代码：
{feedback}
3. 失败案例摘要:
{json.dumps([{'error_type': case.get('error_type'),'error_message': case.get('error_message')} for case in failed_cases[:3]], indent=2, ensure_ascii=False)}
请按照以下要求生成新的代码：
1. 确保处理所有已知的错误类型
2. 增强代码的健壮性
3. 保持代码的可读性
4. 只返回完整的Python代码，无需解释

请生成完整的、可直接执行的Python代码。
"""
        current_code = generate_code(args, improvement_prompt)
        metrics.end_step(f"iteration_{cnt}")
        # Update iteration parameters
        prev_accuracy = current_acc
        cnt += 1
        print(f"The current accuracy is {current_acc:.4f}")
    
    metrics.set_final_accuracy(best_accuracy)
    
    return best_accuracy, best_code, failed_cases
    
def print_metrics_report(args, metrics: MetricsCollector):
    report = metrics.get_metrics_report()
    
    print("\n=== Experiment Configuration ===")
    config = report["experiment_config"]["experiment_settings"]
    print(f"Model (CodeGen): {config['model_codegen']}")
    print(f"Model (DataGen): {config['model_datagen']}")
    print(f"Max Iterations: {config['max_iterations']}")
    print(f"Target Accuracy: {config['target_accuracy']}")
    print(f"Batch Size: {config['batch_size']}")
    print(f"Data Path: {config['data_path']}")
    print(f"Output Directory: {config['output_dir']}")
    print(f"Timestamp: {config['timestamp']}")
    
    print("\n=== Performance Metrics ===")
    print(f"Total Runtime: {report['execution_metrics']['total_time']}")
    
    print("\n=== Iteration Summary ===")
    iter_metrics = report["iteration_metrics"]
    print(f"Total Iterations: {iter_metrics['total_iterations']}")
    print(f"Initial Accuracy: {iter_metrics.get('initial_accuracy', 'N/A')}")
    print(f"Final Accuracy: {iter_metrics['final_accuracy']}")
    print(f"Accuracy Improvement: {iter_metrics.get('accuracy_improvement', 'N/A')}")
    
    print("\n=== Iteration Details ===")
    for iter_info in iter_metrics['iterations']:
        print(f"Iteration {iter_info['iteration']}:")
        print(f"  Accuracy: {iter_info['accuracy']:.4f}")
        print(f"  Failed Cases: {iter_info['failed_cases']}")
        print(f"  Time: {iter_info['timestamp']}")
    
    print("\n=== Token Usage ===")
    token_metrics = report["token_metrics"]
    print(f"Prompt Tokens: {token_metrics['total_tokens']['prompt']}")
    print(f"Completion Tokens: {token_metrics['total_tokens']['completion']}")
    print(f"Total Tokens: {token_metrics['total_token_count']}")
    
    # 保存详细报告到JSON文件
    metrics_file = os.path.join(args.output_dir, "metrics.json")
    with open(metrics_file, "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\nDetailed metrics have been saved to: {metrics_file}")

def power_instruct():
    args = parse_args()
    print(args)
    metrics.set_config(args)

    # step1: data cleaning
    print_step(1, "Data cleaning")
    metrics.start_step("data_cleaning")
    data = load_json(args.total_data_dir)
    data = { 'raw_data': data }
    processed_data = data_cleaning(args, data)
    metrics.end_step("data_cleaning")

    # step2: seed data generation
    print_step(2, "Seed Data Generation")
    # 2.1 select random data
    metrics.start_step("seed_generation")
    seed_data = select_random_data(processed_data).get('data', '')

    # 2.2 get standard data
    # TODO: choose different types of training data, including alcapa, role-based, task-based, etc.
    # model choice. here, we use L_weak LLM 
    std_single_data = get_standard_data(args, seed_data)
    print(std_single_data)
    metrics.end_step("seed_generation")

    # step 3: generate code
    print_step(3, "Achieve code generation prompt")
    # 3.1 merge template
    metrics.start_step("initial_code_generation")
    codegen_prompt = merge_codegen_template(seed_data, std_single_data)
    # generate initial code, here, we use L_strong LLM (such as Claude37, QwenMax)
    current_code = generate_code(args, codegen_prompt)    # 初始化代码
    print(codegen_prompt)
    metrics.end_step("initial_code_generation")
    
    # step 4: Iteratively optimize code
    print_step(4, "Iteratively optimize code")
    metrics.start_step("code_optimization")
    best_accuracy, best_code, failed_cases = iterative_code_generation(args, processed_data, current_code)
    # import ipdb; ipdb.set_trace()
    metrics.end_step("code_optimization")

    # step 5: process all data
    print_step(5, "Process all data")
    metrics.start_step("final_processing")
    print_result("Final code accuracy", f"{best_accuracy:.4f}")
    executed_code = best_code
    batch_results = run_batch_data(args, total_data_dir=args.total_data_dir,executed_code=executed_code)
    metrics.end_step("final_processing")

    # step 6: print results
    print_step(6, "Processing completed, statistical information")
    logger.info(f"Final code accuracy: {best_accuracy}")
    logger.info(f"Final code: {best_code}")

    print_metrics_report(args, metrics)


if __name__ == "__main__":
    power_instruct()
