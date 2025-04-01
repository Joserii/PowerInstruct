import logging
import os
import traceback

from src.file_loader import load_json, load_record_waves, load_description, get_json_path
from src.extractor import JSONDataExtractor
from src.conclusion_generator import FaultConclusionGenerator

logger = logging.getLogger(__name__)

class FaultAnalysisService:
    @staticmethod
    def analyze_fault(data):
        """故障分析主服务方法"""
        try:
            # 参数校验
            required_params = ['data_type', 'mode', 'error_type', 'example_id']
            for param in required_params:
                if param not in data:
                    raise ValueError(f'Missing required parameter: {param}')
            
            # 根据不同数据类型处理
            if data['data_type'] == 'json':
                return FaultAnalysisService._analyze_json_data(data)
            
            elif data['data_type'] == 'xml':
                return FaultAnalysisService._analyze_xml_data(data)
            
            elif data['data_type'] == 'txt':
                return FaultAnalysisService._analyze_txt_data(data)
            
            else:
                raise ValueError(f"Invalid data type: {data['data_type']}")
        
        except Exception as e:
            logger.error(f"Fault analysis error: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    @staticmethod
    def _analyze_json_data(data):
        """分析 JSON 数据"""
        # 获取 JSON 文件路径
        a_dir, b_dir = get_json_path(
            mode=data['mode'], 
            error_type=data['error_type'], 
            example_id=data['example_id']
        )
        
        # 加载文件内容
        a_content = load_json(a_dir)
        b_content = load_json(b_dir)
        
        # 解析 JSON 数据
        input_content_a, single_result_a = FaultAnalysisService._parse_json_data(a_content)
        input_content_b, single_result_b = FaultAnalysisService._parse_json_data(b_content)
        
        # 生成结论
        output = FaultAnalysisService._merge_result(single_result_a, single_result_b)
        
        return {
            'input_station_a': input_content_a,
            'input_station_b': input_content_b,
            'output': output
        }

    @staticmethod
    def _analyze_xml_data(data):
        """分析 XML 数据"""
        record_path = data.get('record_path')
        content = load_record_waves(record_path)
        return {'content': content}

    @staticmethod
    def _analyze_txt_data(data):
        """分析文本数据"""
        description_path = data.get('description_path')
        content = load_description(description_path)
        return {'content': content}

    @staticmethod
    def _parse_json_data(json_data: dict):
        """解析 JSON 数据"""
        extractor = JSONDataExtractor(json_data=json_data)
        input_content, single_result = extractor.analyze_single_output()
        return input_content, single_result

    @staticmethod
    def _merge_result(station_a_desc, station_b_desc):
        """合并结果"""
        fault_conclusion_generator = FaultConclusionGenerator(station_a_desc, station_b_desc)
        output = fault_conclusion_generator.generate_conclusion()
        return output

    @staticmethod
    def test_all_examples(mode='test'):
        """测试所有样例的方法"""
        # 实现与原来类似，但使用新的工具函数
        pass
