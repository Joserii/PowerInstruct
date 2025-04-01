import os
import argparse
import json
from ...utils.idealab_utils import idealab_request
from ...utils.logger import logger
from src.extractor import JSONDataExtractor
from src.conclusion_generator import FaultConclusionGenerator

WAVE_RECORD_PATH: str = './data/1049个训练样本-1016/A相接地故障/220kV宝王线A相瞬时接地故障/宝都站/17299_31950_6X100000.xml'
DESCRIPTION_PATH: str = './data/102个测试样本-1015/A相接地故障/220kV东栾线A相瞬时接地故障/220kV东栾线A相瞬时接地故障.txt'
# MODE: str = 'test'  # 'train' or 'test'
# ERROR_TYPE: str = 'A相接地故障'  # 'A相接地故障' or 'B相接地故障' or 'C相接地故障'
# EXAMPLE_ID: str = '220kV东栾线A相瞬时接地故障'  # '220kV宝王线A相瞬时接地故障' or '220kV东栾线A相瞬时接地故障'
# STATION_NAME_A: str = '东江线'  
# STATION_NAME_B: str = '栾家站'  
# SYS_PROMPT: str = cot_0shot_rules_system_prompt()   # [cot_0shot_code_system_prompt(), cot_0shot_system_prompt(), cot_0shot_rules_system_prompt()]
# data_type = 'description'  # 'record' or 'description' or 'json'

def test_all_examples(mode='test'):
    """
    测试所有样例的函数
    :param mode: 'train' or 'test'
    """
    # 设置基础路径
    base_path = f'./data/{"1049个训练样本-1016" if mode == "train" else "102个测试样本-1015"}'
    
    # 统计变量
    total_cases = 0
    successful_cases = 0
    failed_cases = 0
    
    # 存储测试结果
    test_results = []
    
    # 遍历错误类型
    for error_type in os.listdir(base_path):
        error_type_path = os.path.join(base_path, error_type)
        if not os.path.isdir(error_type_path): continue   # 跳过非目录文件（如 .DS_Store）
        # 遍历具体用例
        for example_id in os.listdir(error_type_path):
            example_path = os.path.join(error_type_path, example_id)
            # 跳过非目录文件
            if not os.path.isdir(example_path): continue
            # 查找JSON文件
            json_files = [f for f in os.listdir(example_path) if f.endswith('.json')]
            # 确保有两个JSON文件
            if len(json_files) == 2:
                try:
                    # 完整路径
                    json_paths = [os.path.join(example_path, f) for f in json_files]
                    
                    # 加载JSON数据
                    a_content, b_content = load_json(json_paths[0]), load_json(json_paths[1])
                    
                    # 解析JSON数据
                    input_content_a, single_result_a = parse_json_data(a_content)
                    input_content_b, single_result_b = parse_json_data(b_content)
                    
                    # 生成结论
                    output = merge_result(single_result_a, single_result_b)
                    
                    # 记录测试结果
                    test_results.append({
                        'error_type': error_type,
                        'example_id': example_id,
                        'result': output,
                        'status': 'success'
                    })
                    
                    successful_cases += 1
                    
                except Exception as e:
                    # 记录失败的测试用例
                    test_results.append({
                        'error_type': error_type,
                        'example_id': example_id,
                        'result': None,
                        'status': 'failed',
                        'error': str(e)
                    })
                    
                    failed_cases += 1
                
                total_cases += 1

    # 生成测试报告
    generate_test_report(total_cases, successful_cases, failed_cases, test_results)
    return test_results

def generate_test_report(total_cases, successful_cases, failed_cases, test_results):
    """
    生成测试报告
    """
    logger.info("\n===== 测试报告 =====")
    logger.info(f"总测试用例数: {total_cases}")
    logger.info(f"成功用例数: {successful_cases}")
    logger.info(f"失败用例数: {failed_cases}")
    
    # 按错误类型统计
    error_type_stats = {}
    for result in test_results:
        error_type = result['error_type']
        status = result['status']
        
        if error_type not in error_type_stats:
            error_type_stats[error_type] = {'total': 0, 'success': 0, 'failed': 0}
        
        error_type_stats[error_type]['total'] += 1
        error_type_stats[error_type]['success' if status == 'success' else 'failed'] += 1
    
    logger.info("\n错误类型统计:")
    for error_type, stats in error_type_stats.items():
        logger.info(
            f"{error_type}: 总数={stats['total']}, "
            f"成功={stats['success']}, "
            f"失败={stats['failed']}"
        )
    
    # 可选：写入详细测试结果到文件
    with open(f'test_results_{args.mode}.json', 'w', encoding='utf-8') as f:
        json.dump(test_results, f, ensure_ascii=False, indent=2)

def get_json_path(mode, error_type, example_id):
    if mode == 'test':
        example_path = f'./data/102个测试样本-1015/{error_type}/{example_id}'
    elif mode == 'train':
        example_path = f'./data/1049个训练样本-1016/{error_type}/{example_id}'
    else:
        raise ValueError(f"Invalid mode: {mode}")

    json_files = [os.path.join(example_path, f) for f in os.listdir(example_path) if f.endswith('.json')]
    if len(json_files) == 0:
        raise ValueError(f"Invalid: Cannot find json files")
    elif len(json_files) == 1:
        raise ValueError(f"Invalid: Only find one json file")
    elif len(json_files) == 2:
        print(f"find two json files!")
        return json_files[0], json_files[1]
    else:
        raise ValueError(f"Invalid: Find more than two json files")


def load_record_waves(file_path: str, encoding='utf-8'):
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            record_content = f.read()
        return record_content
    except FileNotFoundError as e:
        print(f"文件不存在: {e}")
        return None
    except IOError as e:
        print(f"读取文件失败: {e}")
        return None
    

def load_description(file_path: str, encoding='utf-8'):
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            desc_content = f.read()
        return desc_content
    except FileNotFoundError as e:
        print(f"文件不存在: {e}")
        return None
    except IOError as e:
        print(f"读取文件失败: {e}")
        return None
    
def load_json(file_path: str, encoding='utf-8'):
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            json_data = json.load(f)
        return json_data
    except FileNotFoundError as e:
        print(f"文件不存在: {e}")
        return None
    except IOError as e:
        print(f"读取文件失败: {e}")
        return None

def parse_json_data(json_data: dict):
    extractor = JSONDataExtractor(json_data=json_data)
    input_content, single_result = extractor.analyze_single_output()
    return input_content, single_result


def merge_result(station_a_desc, station_b_desc):
    fault_conclusion_generator = FaultConclusionGenerator(station_a_desc, station_b_desc)
    output = fault_conclusion_generator.generate_conclusion()
    return output

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_type', type=str, default='json', help='The type of input data, ["json","xml","txt"].')
    parser.add_argument('--record_path', type=str, default=WAVE_RECORD_PATH, help='The path of the record wave file.')
    parser.add_argument('--description_path', type=str, default=DESCRIPTION_PATH, help='The path of the description file.')
    parser.add_argument('--mode', type=str, default='train', help='The mode of the data, train or test.')
    parser.add_argument('--error_type', type=str, default='A相接地故障', help='The type of the error, A相接地故障 or B相接地故障 or C相接地故障.')
    parser.add_argument('--example_id', type=str, default='220kV东栾线A相瞬时接地故障', help='The id of the example.')
    parser.add_argument('--test_all_data', type=bool, default=False, help='是否测试所有数据')

    args = parser.parse_args()
    args.test_all_data = False

    print(args)
    print(f"Data type: {args.data_type}")
    print(f"test_all_data: {args.test_all_data}")

    if args.test_all_data:
        test_results = test_all_examples(mode=args.mode)
    else:
        if args.data_type == 'json':
            a_dir, b_dir = get_json_path(mode=args.mode, error_type=args.error_type, example_id=args.example_id)
            print(f"Path of two json files: \n{a_dir}\n{b_dir}")
            # how to use json file for prompt?
            a_content, b_content = load_json(file_path=a_dir), load_json(file_path=b_dir)
            print(f"Content of two json files: \n{a_content}\n{b_content}")
            input_content_a, single_result_a = parse_json_data(a_content)
            input_content_b, single_result_b = parse_json_data(b_content)
            output = merge_result(single_result_a, single_result_b)
            
            logger.info(f"Input_station_a: {input_content_a}")
            logger.info(f"Input_station_b: {input_content_b}")
            logger.info(f"Output: {output}")

        elif args.data_type == 'xml':
            content = load_record_waves(file_path=args.record_path)
        elif args.data_type == 'txt':
            content = load_description(file_path=args.description_path)
