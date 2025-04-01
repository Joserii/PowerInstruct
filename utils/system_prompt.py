import os
import json
from config.settings import *
from utils.logger import logger
from utils.prompt_template.directgen_prompt import datagen_1shot_system_prompt
from utils.prompt_template.codegen_prompt import codegen_1shot_system_prompt, codegen_1shot_multiple_data


# TODO 1 normalize the template content
def get_default_templates():
    """获取默认模板"""
    return {
        'prompt': datagen_1shot_system_prompt(),
        'codegen': codegen_1shot_system_prompt()
    }


def load_user_templates():
    """加载用户自定义模板，如果没有则返回默认模板"""
    try:
        templates = get_default_templates()

        # if TEMPLATE_FILE.exists():
        #     with open(TEMPLATE_FILE, 'r', encoding='utf-8') as f:
        #         user_templates = json.load(f)

        #         # 合并用户模板，仅更新已修改的部分
        #         if user_templates.get('prompt'):
        #             templates['prompt'] = user_templates['prompt']
        #         if user_templates.get('codegen'):
        #             templates['codegen'] = user_templates['codegen']
        return templates
    
    except Exception as e:
        logger.error(f"Error loading user templates: {e}")
        return get_default_templates()

def save_user_templates(templates):
    """保存用户自定义模板"""
    try:
        with open(TEMPLATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(templates, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving user templates: {e}")
        return False


if __name__ == '__main__':
    # print(f"Code generation system prompt:\n {cot_0shot_code_system_prompt()}\n\n")
    # print(f"System prompt:\n {cot_0shot_system_prompt()}\n\n")
    # print(f"Rules system prompt:\n {cot_0shot_rules_system_prompt()}\n\n")

    # print(f"Data generation system prompt:\n {datagen_1shot_system_prompt()}\n\n")
    # print(f"Code generation system prompt:\n {codegen_1shot_system_prompt()}\n\n")

    with open('/Users/czy/projects/baohuchu_demo/data/102个测试样本-1015/B相接地故障（不投重合闸）/220kV楼牵Ⅱ线B相接地故障（不投重合闸）/张楼站.json', 'r') as f:
        input_format = json.load(f)
    
    with open('/Users/czy/projects/baohuchu_demo/data/output.json', 'r') as f:
        output_format = json.load(f)
    print(f"Code generation system prompt:\n {codegen_1shot_multiple_data(input_format, output_format)}\n\n")
