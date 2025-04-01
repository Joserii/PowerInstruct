import os
import sys
import json
import random
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import *
from utils.logger import logger

data_dir = BASE_DATA_FOLDER['test']

def select_random_data(data_path: str):
    """
    随机选择一个JSON文件并读取其内容
    
    Args:
        data_path (str): 数据目录路径
        
    Returns:
        dict: 包含文件路径、故障类型和内容的字典
    """
    json_files = []
    try:
        for root, dirs, files in os.walk(data_path):
            for file in files:
                if file.lower().endswith('.json'):
                    json_files.append(os.path.join(root, file))
        
        if not json_files:
            logger.error("未找到任何JSON文件")
            print("未找到任何JSON文件")
            return None
            
        random_file = random.choice(json_files)
        logger.info(f"随机选择的文件: {random_file}")
        print(f"随机选择的文件: {random_file}")

        try:
            with open(random_file, 'r', encoding='utf-8') as f:  # 添加 encoding='utf-8'
                content = json.load(f)
            return {
                'file_path': random_file,
                'fault_type': random_file.split('/')[-3],
                'content': content
            }
        except json.JSONDecodeError as e:
            logger.error(f"JSON文件解析错误: {str(e)}")
            print(f"JSON文件解析错误: {str(e)}")
            raise ValueError(f"JSON文件解析错误: {str(e)}")

    except OSError as e:
        logger.error(f"搜索目录时出错: {str(e)}")
        print(f"搜索目录时出错: {str(e)}")
        raise


def print_stats_info(fault_type_dict):
    # 输出统计信息
    stats = {fault_type: len(data) 
            for fault_type, data in fault_type_dict.items()}
    logger.info("故障类型统计:")
    for fault_type, count in stats.items():
        logger.info(f"- {fault_type}: {count}条数据")
    print("故障类型统计:")
    for fault_type, count in stats.items():
        print(f"- {fault_type}: {count}条数据")


def save_all_data(data_path: str, save_name: str = "all_data_including_gt.json"):
    """
    保存所有JSON文件的内容到一个文件中
    
    Args:
        data_path (str): 数据目录路径
        save_name (str): 保存文件名
    """
    json_files = []
    try:
        # 收集所有JSON文件
        for root, dirs, files in os.walk(data_path):
            for file in files:
                if file.lower().endswith('.json'):
                    json_files.append(os.path.join(root, file))
        
        if not json_files:
            logger.error("未找到任何JSON文件")
            print("未找到任何JSON文件")
            return None

        try:
            save_dir = os.path.join(TEST_DATA_FOLDER, save_name)
            output_list = []
            fault_type_dict = {}
            
            # 读取每个JSON文件
            for file_path in json_files:
                with open(file_path, 'r', encoding='utf-8') as f:  # 添加 encoding='utf-8'
                    content = json.load(f)
                    fault_type = file_path.split('/')[-3]

                    output = {
                        'file_path': file_path,
                        'fault_type': fault_type,
                        'content': content
                    }
                    output_list.append(output)
                    if fault_type not in fault_type_dict:
                        fault_type_dict[fault_type] = []
                    fault_type_dict[fault_type].append(output)
            
                        # 保存完整列表
            with open(save_dir, 'w', encoding='utf-8') as f:
                json.dump(output_list, f, 
                         ensure_ascii=False,
                         indent=4)
            
            # 保存按故障类型分类的数据
            classified_save_dir = os.path.join(TEST_DATA_FOLDER, 
                                             f"classified_{save_name}")
            
            # 保存合并后的数据
            with open(classified_save_dir, 'w', encoding='utf-8') as f:
                json.dump(fault_type_dict, f, 
                         ensure_ascii=False,
                         indent=4)
            

            print_stats_info(fault_type_dict)
            
            return fault_type_dict
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON文件解析错误: {str(e)}")
            print(f"JSON文件解析错误: {str(e)}")
            raise ValueError(f"JSON文件解析错误: {str(e)}")

    except OSError as e:
        logger.error(f"搜索目录时出错: {str(e)}")
        print(f"搜索目录时出错: {str(e)}")
        raise

def get_few_shot_data(fault_type_data, num_samples_each_type: int = 1, save_name: str = "few_shot_data.json"):
    '''
    每种故障类型随机选择指定数量的样本数据
    '''
    print("故障类型数据:", fault_type_data.keys())
    few_shot_save_dir = os.path.join(TEST_DATA_FOLDER, save_name)
    few_shot_data = {}
    for fault_type, data in fault_type_data.items():
        few_shot_data[fault_type] = []
        if len(data) < num_samples_each_type:
            logger.warning(f"故障类型 {fault_type} 的数据量小于指定数量，将使用全部数据")
            num_samples_each_type = len(data)
        
        random_samples = random.sample(data, num_samples_each_type)
        few_shot_data[fault_type].append(random_samples)
    
    # with open(few_shot_save_dir, 'w', encoding='utf-8') as f:
    #     json.dump(few_shot_data, f, 
    #               ensure_ascii=False,
    #               indent=4)
    with open(few_shot_save_dir, 'w', encoding='utf-8') as f:
        json.dump(few_shot_data, f, 
                ensure_ascii=False,
                indent=2,
                separators=(',', ':'))


    
    return few_shot_data

# TODO: 后续汇总到 prompt_utils.py 里面
def get_few_shot_prompt(few_shot_data):
    '''
    从少样本数据中提取系统提示
    '''
    few_shot_prompt = {}
    for fault_type, data in few_shot_data.items():
        few_shot_prompt[fault_type] = []
        for sample in data:
            prompt = sample['content']['prompt']
            few_shot_prompt[fault_type].append(prompt)
    
    return few_shot_prompt



if __name__ == "__main__":
    # data = select_random_data(data_dir)  # 102个测试样本-1015
    fault_type_data = save_all_data(data_dir)   
    few_shot_data = get_few_shot_data(fault_type_data, num_samples_each_type=1)
    print(f"少样本数据: {len(few_shot_data)}")
    print(few_shot_data)
