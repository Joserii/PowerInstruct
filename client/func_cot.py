from utils.idealab_utils import idealab_request
import json
import textwrap
import requests
import os

api = 'https://idealab.alibaba-inc.com/api/v1/chat/completions'
api_key = os.getenv("SERVER_API_KEY")

def generate_code(codegen_prompt: str) -> str:
    # 定义function calling的消息格式
    messages = [
        {
            "role": "system",
            "content": """You are a Python programming expert. You will analyze the problem step by step 
            and generate code using the analyze_power_data function. Your analysis should cover data validation, 
            fault analysis, and instruction generation."""
        },
        {
            "role": "user",
            "content": f"""Let's break down the code generation process:

1. First, we need to validate the input data including:
   - Line name
   - Pre-fault and post-fault waveform data
   - Reclosing count

2. Then, analyze the fault characteristics:
   - Analyze zero-sequence voltage and current
   - Determine fault phase
   - Calculate current changes

3. Finally, generate standard format output:
   - Build input field
   - Build output field (including reclosing summary, analysis conclusion, fault classification)

Original prompt:
{codegen_prompt}

Please provide your analysis and generate code using the analyze_power_data function with the following structure:
{{
    "data_validation": "code for data validation",
    "fault_analysis": "code for fault analysis",
    "generate_instruction": "code for instruction generation"
}}"""
        }
    ]

    try:
        # 使用现有的 idealab_request 接口
        response, _, _ = idealab_request(messages, model="gpt-4o-0806", temperature=0.7)

        # 解析响应
        try:
            # 尝试解析返回的JSON格式响应
            function_args = json.loads(response)
        except json.JSONDecodeError:
            # 如果返回的不是JSON格式，尝试从文本中提取所需部分
            # 这里可能需要根据实际返回格式调整提取逻辑
            return response

        # 生成最终的Python代码
        final_code = f"""
def generate_instruction(input_data: dict) -> dict:
    # 1. 数据验证
    {function_args.get('data_validation', '# Data validation code here')}
    
    # 2. 故障分析
    {function_args.get('fault_analysis', '# Fault analysis code here')}
    
    # 3. 生成指令格式
    {function_args.get('generate_instruction', '# Instruction generation code here')}
    
    return output_data
"""
        return final_code.strip()
            
    except Exception as e:
        print(f"Error during code generation: {str(e)}")
        return None
    

def generate_code_with_function_call(codegen_prompt: str) -> str:
    # 1. 定义函数
    functions = [
        {
            "name": "analyze_power_data",
            "description": "分析电力系统故障数据并生成代码",
            "parameters": {
                "type": "object",
                "properties": {
                    "data_validation": {
                        "type": "string",
                        "description": "数据验证代码部分"
                    },
                    "fault_analysis": {
                        "type": "string",
                        "description": "故障分析代码部分"
                    },
                    "generate_instruction": {
                        "type": "string",
                        "description": "指令生成代码部分"
                    }
                },
                "required": ["data_validation", "fault_analysis", "generate_instruction"]
            }
        }
    ]

    messages = [
        {
            "role": "system",
            "content": "你是一个Python编程专家，请分析问题并生成相应的代码。"
        },
        {
            "role": "user",
            "content": f"请分析以下问题并生成代码：\n{codegen_prompt}"
        }
    ]

    # 2. 构建请求体
    body = {
        "messages": messages,
        "functions": functions,  # 添加函数定义
        "function_call": {"name": "analyze_power_data"},  # 指定要调用的函数
        "temperature": 0.7,
        "platformInput": {
            "model": "gpt-4o-0806",
            "isAcquireOriginalOutput": False,
        }
    }

    # 3. 发送请求
    header = {
        "Content-Type": "application/json",
        "X-AK": api_key
    }

    try:
        resp = requests.post(api, json=body, headers=header)
        if resp.status_code == 200:
            respData = json.loads(resp.text)
            if respData['success']:
                # 4. 处理函数调用结果
                function_call = respData["data"]["choices"][0].get("function_call")
                if function_call:
                    # 解析函数调用参数
                    function_args = json.loads(function_call["arguments"])
                    
                    # 生成最终代码
                    final_code = f"""
def generate_instruction(input_data: dict) -> dict:
    # 1. 数据验证
{textwrap.indent(function_args['data_validation'], '    ')}

    # 2. 故障分析
{textwrap.indent(function_args['fault_analysis'], '    ')}

    # 3. 生成指令格式
{textwrap.indent(function_args['generate_instruction'], '    ')}

    return output_data
"""
                    return final_code.strip()
                else:
                    return "No function call in response"
            else:
                return "API call failed"
        else:
            return "HTTP request failed"
    except Exception as e:
        print(f"Error: {str(e)}")
        return None


if __name__ == '__main__':
    # 使用示例
    test_prompt = """
    [你的代码生成提示]
    """

    result = generate_code_with_function_call(test_prompt)
    print(result)
