import requests
import json
import traceback

def analyze_fault(
    data_type='json', 
    mode='test', 
    error_type='A相接地故障', 
    example_id='220kV东栾线A相瞬时接地故障',
    record_path=None,
    description_path=None
):
    """
    调用故障分析服务
    
    :param data_type: 数据类型
    :param mode: 模式（train/test）
    :param error_type: 错误类型
    :param example_id: 样例ID
    :param record_path: 录波文件路径（可选）
    :param description_path: 描述文件路径（可选）
    :return: 分析结果
    """
    url = 'http://localhost:5000/analyze'
    
    payload = {
        'data_type': data_type,
        'mode': mode,
        'error_type': error_type,
        'example_id': example_id
    }
    
    # 根据数据类型添加额外参数
    if data_type == 'xml' and record_path:
        payload['record_path'] = record_path
    elif data_type == 'txt' and description_path:
        payload['description_path'] = description_path
    
    try:
        # 打印发送的payload
        print("Sending payload:", json.dumps(payload, ensure_ascii=False, indent=2))
        
        response = requests.post(
            url, 
            json=payload, 
            headers={'Content-Type': 'application/json'}
        )
        
        # 打印完整的响应
        print("Response status code:", response.status_code)
        
        # 使用 json.dumps 正确打印中文
        print("Response content:", json.dumps(response.json(), ensure_ascii=False, indent=2))
        
        # 检查响应状态码
        if response.status_code == 200:
            result = response.json()
            return result
        else:
            print(f"Error: {response.status_code}")
            print("Response content:", json.dumps(response.json(), ensure_ascii=False, indent=2))
            return None
    
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        print(traceback.format_exc())
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        print(traceback.format_exc())
        return None

def test_all_data(mode='test'):
    """
    测试所有数据
    
    :param mode: 模式（train/test）
    :return: 测试结果
    """
    url = 'http://localhost:5000/test_all'
    
    payload = {
        'mode': mode
    }
    
    try:
        response = requests.post(
            url, 
            json=payload, 
            headers={'Content-Type': 'application/json'}
        )
        
        # 检查响应状态码
        if response.status_code == 200:
            result = response.json()
            return result
        else:
            print(f"Error: {response.status_code}")
            print("Response content:", response.text)
            return None
    
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        print(traceback.format_exc())
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        print(traceback.format_exc())
        return None

def main():
    # 单个样例分析示例
    result = analyze_fault(
        data_type='json',
        mode='test',
        error_type='A相接地故障',
        example_id='220kV东栾线A相瞬时接地故障'
    )
    
    if result:
        print("单个样例分析结果:", json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
