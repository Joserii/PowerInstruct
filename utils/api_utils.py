# qwen_api_key

import os
from openai import OpenAI
from typing import Optional, Union, List
import anthropic

# Here we put a temporal api key for test, please replace it with your own api key.
# Supported Model List: ['qwen-max', 'qwen-coder-plus', 'qwen2.5-7b-instruct']
os.environ["DASHSCOPE_API_KEY"] = 'sk-658896d9b7754ca69fa869308704606d'
os.environ["DASHSCOPE_BASE_URL"] = "https://dashscope.aliyuncs.com/compatible-mode/v1"


qwen_series_model = ['qwen-max', 'qwen-coder-plus', 'qwen2.5-7b-instruct']
openai_series_model = ['o1', 'o1-mini', 'gpt-4o', 'gpt-4o-mini']
anthropic_series_model = ['claude-3-7-sonnet-20250219', 'claude-3-5-sonnet-20241022']

def api_request(
    prompt: str,
    model_name: str='qwen-plus',
    **kwargs
    ):

    if model_name in qwen_series_model:
        response, token_prompt, token_compli = qwen_request(prompt=prompt, model_name=model_name)
        return response, token_prompt, token_compli
    elif model_name in openai_series_model:
        response, token_prompt, token_compli = openai_request(prompt=prompt, model_name=model_name)
        return response, token_prompt, token_compli
    elif model_name in anthropic_series_model:
        response, token_prompt, token_compli = anthropic_request(prompt=prompt, model_name=model_name)
        return response, token_prompt, token_compli
    else:
        raise ValueError(f"model_name: {model_name} is not in the qwen_series_model list.")


def qwen_request(
    prompt: str,
    model_name: str='qwen-plus',
    **kwargs
    ):
    client = OpenAI(
        api_key=os.getenv("DASHSCOPE_API_KEY"), 
        base_url=os.getenv("DASHSCOPE_BASE_URL"),
    )
    # Here we take qwen-plus as an example, and the model name can be changed as needed. 
    # Model list: https://help.aliyun.com/zh/model-studio/models
    completion = client.chat.completions.create(
        model=model_name, 
        messages=[
            {'role': 'system', 'content': 'You are a helpful assistant.'},
            {'role': 'user', 'content': prompt}],
        )
    response = completion.choices[0].message.content
    token_prompt = completion.usage.prompt_tokens
    token_compli = completion.usage.completion_tokens
    return response, token_prompt, token_compli

# https://platform.openai.com/docs/pricing
def openai_request(
    prompt: str,
    model_name: str='gpt-4o',
    system_message: Optional[Union[str, List]] = "You are a helpful assistant.",
    **kwargs
    ):
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")
    client = OpenAI(api_key=api_key, base_url=base_url)
    # Here we take gpt-4o as an example, and the model name can be changed as needed. 
    # Model list: https://platform.openai.com/docs/pricing
    if isinstance(system_message, str):
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt},
        ]
    elif isinstance(system_message, list):
        messages = system_message
    else:
        raise ValueError(
            "system_message should be either a string or a list of strings."
        )
        
    response = client.chat.completions.create(
        model=model_name,
        messages=messages,
        **kwargs
    )
    output = response.choices[0].message.content.strip()
    return output, 0, 0


def anthropic_request(
    prompt: str,
    model_name: str='claude-3-5-sonnet-20241022',
    max_tokens_to_sample: Optional[int] = 1024,
    **kwargs
    ):
    api_key = os.getenv("ANTHROPIC_API_KEY")
    client = anthropic.Anthropic(api_key=api_key)
    # Here we take claude-3-5-sonnet as an example, and the model name can be changed as needed. 
    # Model list: https://docs.anthropic.com/en/docs/about-claude/models/all-models
    response = client.completions.create(
        prompt=f"{anthropic.HUMAN_PROMPT} {prompt} {anthropic.AI_PROMPT}",
        model=model_name,
        max_tokens_to_sample=max_tokens_to_sample,
    )
    output = response.completion.strip()
    return output, 0, 0

def test_anthropic():
    response, token_prompt, token_compli = api_request(
        prompt= 'who are you?',
        model_name='claude-3-5-sonnet-20241022'
    )
    return response, token_prompt, token_compli


def test_openai():
    response, token_prompt, token_compli = api_request(
        prompt= 'who are you?',
        model_name='gpt-4o'
    )
    return response, token_prompt, token_compli
    
def test_qwen():
    response, token_prompt, token_compli = api_request(
        prompt= 'who are you?',
        model_name='qwen-max'
    )
    return response, token_prompt, token_compli

if __name__ == '__main__':
    response, token_prompt, token_compli = test_anthropic()
    print(response, token_prompt, token_compli)
    # response, token_prompt, token_compli = test_openai()
    # print(response, token_prompt, token_compli)
    # response, token_prompt, token_compli = test_qwen()
    # print(response, token_prompt, token_compli)
    
    