import os
import argparse
import json
from ...utils.idealab_utils import idealab_request
from ...utils.system_prompt import cot_0shot_code_system_prompt, cot_0shot_system_prompt, cot_0shot_rules_system_prompt, \
                                datagen_1shot_system_prompt
from ...utils.logger import logger

WAVE_RECORD_PATH: str = './data/1049个训练样本-1016/A相接地故障/220kV宝王线A相瞬时接地故障/宝都站/17299_31950_6X100000.xml'
DESCRIPTION_PATH: str = './data/102个测试样本-1015/A相接地故障/220kV东栾线A相瞬时接地故障/220kV东栾线A相瞬时接地故障.txt'
# MODE: str = 'test'  # 'train' or 'test'
# ERROR_TYPE: str = 'A相接地故障'  # 'A相接地故障' or 'B相接地故障' or 'C相接地故障'
# EXAMPLE_ID: str = '220kV东栾线A相瞬时接地故障'  # '220kV宝王线A相瞬时接地故障' or '220kV东栾线A相瞬时接地故障'
# STATION_NAME_A: str = '东江线'  
# STATION_NAME_B: str = '栾家站'  
# SYS_PROMPT: str = cot_0shot_rules_system_prompt()   # [cot_0shot_code_system_prompt(), cot_0shot_system_prompt(), cot_0shot_rules_system_prompt()]
# data_type = 'description'  # 'record' or 'description' or 'json'

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
            data = f.read()
            json_content = json.dumps(data, separators=(',', ':'), ensure_ascii=False)
        return json_content
    except FileNotFoundError as e:
        print(f"文件不存在: {e}")
        return None
    except IOError as e:
        print(f"读取文件失败: {e}")
        return None


def merge_prompt(sys_prompt, data_type='record', content=None):
    merged_prompt = f"{sys_prompt}\n录波文件如下：\n{content}" if data_type == 'record' else f"{sys_prompt}\n故障信息如下：\n{content}"
    # print(f"merged_prompt: \n{merged_prompt}")
    return merged_prompt

def select_sys_prompt(prompt_type='cot_0shot_rules_system_prompt'):
    if prompt_type == 'cot_0shot_code_system_prompt':
        return cot_0shot_code_system_prompt()
    elif prompt_type == 'cot_0shot_system_prompt':
        return cot_0shot_system_prompt()
    elif prompt_type == 'cot_0shot_rules_system_prompt':
        return cot_0shot_rules_system_prompt()
    elif prompt_type == 'datagen_1shot_system_prompt':
        return datagen_1shot_system_prompt()
    else:
        raise ValueError(f"Invalid prompt type: {prompt_type}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_type', type=str, default='json', help='The type of input data, ["json","xml","txt"].')
    parser.add_argument('--prompt_type', type=str, default='cot_0shot_rules_system_prompt', help='The type of the prompt, ["cot_0shot_code_system_prompt","cot_0shot_system_prompt","cot_0shot_rules_system_prompt"].')
    parser.add_argument('--record_path', type=str, default=WAVE_RECORD_PATH, help='The path of the record wave file.')
    parser.add_argument('--description_path', type=str, default=DESCRIPTION_PATH, help='The path of the description file.')
    parser.add_argument('--mode', type=str, default='train', help='The mode of the data, train or test.')
    parser.add_argument('--error_type', type=str, default='A相接地故障', help='The type of the error, A相接地故障 or B相接地故障 or C相接地故障.')
    parser.add_argument('--example_id', type=str, default='220kV东栾线A相瞬时接地故障', help='The id of the example.')

    args = parser.parse_args()
    print(f"Data type: {args.data_type}")

    if args.data_type == 'json':
        a_dir, b_dir = get_json_path(mode=args.mode, error_type=args.error_type, example_id=args.example_id)
        print(f"Path of two json files: \n{a_dir}\n{b_dir}")
        # how to use json file for prompt?
        content = load_json(file_path=a_dir) + load_json(file_path=b_dir)
    elif args.data_type == 'xml':
        content = load_record_waves(file_path=args.record_path)
    elif args.data_type == 'txt':
        content = load_description(file_path=args.description_path)

    if content is None:
        raise ValueError("Invalid content")
    else:
        sys_prompt = select_sys_prompt(prompt_type=args.prompt_type)
        final_prompt = merge_prompt(sys_prompt=sys_prompt, content=content)
        logger.info(f"\nFinal prompt: \n{final_prompt}\n\n")

    message_status = idealab_request(final_prompt, model='qwen2.5-72b-instruct')

    if isinstance(message_status, str):
        # print(message_status)
        logger.info(f"\nMessage_status: {message_status}")
    else:
        messages, token_prompt, token_completion = message_status
        logger.info(f"\nResponse: \n{messages}\n\n")
        logger.info(f"\nToken_prompt: {token_prompt}")
        logger.info(f"\nToken_completion: {token_completion}")
