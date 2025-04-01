import sys
import os
import ast
import random
import json
import time
from io import StringIO
from typing import Dict, Any
import requests
from requests.exceptions import RequestException

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.prompt_template.codegen_prompt import *
from utils.prompt_template.directgen_prompt import *
from utils.run_python_utils import *
from utils.logger import logger

import datetime

# 在文件开头添加输出目录相关的常量
OUTPUT_BASE_DIR = "output"
CURRENT_TIME = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
CURRENT_OUTPUT_DIR = os.path.join(OUTPUT_BASE_DIR, CURRENT_TIME)


ALLTYPE_FET_SHOT_DATA_DIR = os.path.join(TEST_DATA_FOLDER, 'few_shot_data.json')

SUPPORT_MODEL_REF = [
    "gpt-4o-mini-0718", "gpt-4o-0806", "gpt-4-0409",
    "gemini-1.5-pro", "gemini-1.5-pro-flash",
    "qwen_max", "qwen2.5-72b-instruct", "qwen2.5-7b-instruct",
    "claude35_sonnet", 
    "o1-preview-0912", "o1-mini-0912",
    "qwq-32b", "qwen_max"
]


# 常量定义
# TOTAL_DATA_DIR = "/Users/czy/projects/baohuchu_demo/data/test_data/1049个训练样本-1016_20250306_114145_04171bef2b50213a.json"
TOTAL_DATA_DIR = "/Users/czy/projects/baohuchu_demo/data/test_data/102个测试样本-1015_20250307_173953_318ee91831f5aaac.json"
API_URL = "http://localhost:5000/analyze"
MODEL_ID_FOR_DATAGEN = "qwen2.5-7b-instruct"
MODEL_ID_FOR_CODEGEN = "o1-mini-0912"
OUTPUT_FILE = "batch_results.json"


def select_random_data(data_path: str) -> Dict[str, Any]:
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
        with open(data_path, "r", encoding='utf-8') as f:
            batch_data = json.load(f)
            
        if not batch_data:
            raise ValueError("数据列表为空")
            
        id_ = random.randint(0, len(batch_data) - 1)
        random_data = batch_data[id_]
        
        logger.info(f"Random Select ID: {id_}")
        logger.debug(f"Random Select Data: {random_data}")
        
        return {
            "id": id_,
            "data": random_data
        }
    except Exception as e:
        logger.error(f"读取数据出错: {str(e)}")
        raise ValueError(f"读取数据出错: {str(e)}")


    

def save_results(results: Dict[str, Any], filename: str = "batch_results.json") -> None:
    """保存最终结果"""
    try:
        # 确保输出目录存在
        os.makedirs(CURRENT_OUTPUT_DIR, exist_ok=True)
        
        # 使用时间戳目录
        output_file = os.path.join(CURRENT_OUTPUT_DIR, filename)
        
        with open(output_file, "w", encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        accuracy = convert_result_to_chat(source_file=output_file)
        logger.info(f"结果已保存到: {filename}")

    except Exception as e:
        logger.error(f"保存结果失败: {str(e)}")
        raise


def get_standard_data(single_data: Dict[str, Any], max_retries: int = 3, retry_delay: int = 5) -> str:
    """
    从单条数据中提取标准数据格式
    
    Args:
        single_data: 输入的单条数据
        max_retries: 最大重试次数
        retry_delay: 每次重试之间的延迟时间（秒）
        
    Returns:
        标准格式的数据字符串
    """
    if not single_data:
        raise ValueError("输入数据为空")
    
    for attempt in range(max_retries + 1):
        try:
            data = {
                "filepath": TOTAL_DATA_DIR,
                "mode": "prompt",
                "file_content": str(single_data),
                "template": datagen_1shot_system_prompt(),
                "model_id": MODEL_ID_FOR_DATAGEN,
            }
            
            response = requests.post(API_URL, json=data, timeout=180).json()
            ai_response = response.get("ai_response")
            
            if ai_response:
                logger.info("成功获取标准数据格式")
                return ai_response
            
            logger.warning(f"AI响应为空，尝试第 {attempt + 1} 次")
            if attempt < max_retries:
                time.sleep(retry_delay)
            else:
                raise ValueError("多次尝试后 AI 响应仍然为空")
                
        except RequestException as e:
            logger.error(f"API请求失败: {str(e)}")
            if attempt < max_retries:
                time.sleep(retry_delay)
            else:
                raise

def merge_template(single_data: Dict[str, Any], std_single_data: str) -> str:
    """合并模板和数据"""
    merged_prompt = merge_codegen_template(single_data, std_single_data)
    logger.debug(f"生成的codegen prompt: {merged_prompt}")
    return merged_prompt

def merge_template_alltype(alltype_datadict: Dict[str, Any], single_data: Dict[str, Any], std_single_data: str) -> str:
    """合并模板和数据"""
    merged_prompt = merge_codegen_template_alltype(alltype_datadict, single_data, std_single_data)
    logger.debug(f"生成的codegen prompt: {merged_prompt}")
    return merged_prompt


def generate_code(prompt: str) -> str:
    """生成可执行的Python代码"""
    try:
        data = {
            "filepath": TOTAL_DATA_DIR,
            "mode": "codegen",
            "file_content": str(prompt),  # prompt is here
            "template": codegen_1shot_system_prompt(), # not used
            "model_id": MODEL_ID_FOR_CODEGEN,
        }
        
        response = requests.post(API_URL, json=data, timeout=180).json()
        ai_response = response.get("ai_response")
        
        if not ai_response:
            raise ValueError("AI响应为空")
            
        executed_code = get_executed_python_code(ai_response)
        logger.debug(f"生成的代码: {executed_code}")
        
        return executed_code
        
    except Exception as e:
        logger.error(f"生成代码失败: {str(e)}")
        raise

def concat_input(executed_code: str, input_data: Dict[str, Any]) -> str:
    """拼接代码和输入数据"""
    main_code = f"""\n\n
if __name__ == '__main__':
    # 测试数据
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

def run_batch_data(total_data_dir: str, executed_code: str) -> Dict[str, Any]:
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
        save_results(final_results)
        
        logger.info(f"处理完成. 成功: {success_count}, 失败: {failure_count}")
        return final_results
        
    except Exception as e:
        print(f"\n处理第 {i} 条数据失败: {str(e)}")
        logger.error(f"批量处理失败: {str(e)}")
        raise



def convert_result_to_chat(source_file: str, target_filename: str = 'chat_results.json'):
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
        target_filedir = os.path.join(CURRENT_OUTPUT_DIR, target_filename)
        test_result_dir = os.path.join(CURRENT_OUTPUT_DIR, 'test_results.json')

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
                # correct_count += issame(gt, pred)
                correct_count += (gt == pred)
                
                
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

'''
1. 从 TOTAL_DATA_DIR 中随机选择一条数据
2. 选取模型，执行prompt mode
3. 拼接生成codegen prompt
4. 执行codegen mode, 输出结果(python 代码)，可以执行的python代码
5. 执行python代码，得到结果
6. 对 TOTAL_DATA_DIR 中的所有数据执行以上步骤
7. 将所有的结果整合，保存到一个文件中，保存为 json 格式
'''
def main():
    alltype_few_shot = True
    try:
        os.makedirs(CURRENT_OUTPUT_DIR, exist_ok=True)
        logger.info(f"输出将保存到目录: {CURRENT_OUTPUT_DIR}")

        # 1. 从 TOTAL_DATA_DIR 中随机选择一条数据
        print_step(1, "随机选择示例数据")
        demo_data = select_random_data(TOTAL_DATA_DIR)
        demo_data = demo_data.get('data', '')
        print_result("随机选择的数据", demo_data)
        logger.info(f"Step 1 \n随机选择的数据: {demo_data}")

        # 2. 选取模型，执行prompt mode
        print_step(2, "生成标准数据格式")
        std_single_data = get_standard_data(demo_data)
        print_result("标准数据格式", std_single_data)
        logger.info(f"Step 2 \n标准数据格式: {std_single_data}")

        # 3. 拼接生成codegen prompt
        print_step(3, "生成代码生成提示")
        if alltype_few_shot:
            alltype_data = json.load(open(ALLTYPE_FET_SHOT_DATA_DIR, 'r', encoding='utf-8'))
            codegen_prompt = merge_template_alltype(alltype_data, demo_data, std_single_data)
            # import ipdb; ipdb.set_trace()
        else:
            codegen_prompt = merge_template(demo_data, std_single_data)
        print_result("代码生成提示", codegen_prompt)
        logger.info(f"Step 3 \n代码生成prompt: {codegen_prompt}")

        # 4. 执行codegen mode, 输出结果
        print_step(4, "生成Python代码")
        executed_code = generate_code(codegen_prompt)
        print_result("生成的Python代码", executed_code)
        logger.info(f"Step 4 \n生成的python代码: {executed_code}")

        # 5. 测试单条数据
        print_step(5, "测试单条数据")
        test_data = select_random_data(TOTAL_DATA_DIR)
        result = run_single_data(executed_code=executed_code, input_data=test_data)
        logger.info(f"Step 5 \n单条数据测试结果: {result}")
        
        if result.get('success'):
            print_result("单条数据测试成功", result.get('result'))
        else:
            print_result("单条数据测试失败", {
                'error': result.get('error'),
                'input_data': result.get('input_data')
            })
            # 可以选择是否在这里抛出异常
            # raise Exception(result.get('error'))

        # 6. 批量处理
        print_step(6, "开始批量处理")
        results = run_batch_data(total_data_dir=TOTAL_DATA_DIR, executed_code=executed_code)
        
        # 7. 输出统计信息
        print_step(7, "处理完成，统计信息")
        stats = results['statistics']
        print_result("处理统计", 
                    f"总数: {stats['total']}\n"
                    f"成功: {stats['success']}\n"
                    f"失败: {stats['failure']}\n"
                    f"成功率: {stats['success_rate']}")
        
        if results['failed_results']:
            print_result("失败案例样本", 
                        f"共有 {len(results['failed_results'])} 条失败数据\n"
                        f"第一条失败案例:\n{results['failed_results'][0]}")
        
    except Exception as e:
        print_result("程序执行失败", str(e))
        raise

if __name__ == "__main__":
    main()
