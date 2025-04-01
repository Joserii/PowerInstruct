import json
import numpy as np
from .analyzer import FaultAnalyzer
from utils.logger import logger

class JSONDataExtractor:
    def __init__(self, json_data):
        self.data = self._parse_json(json_data)
        self.analyzer = FaultAnalyzer()
    
    def _parse_json(self, json_data):
        """
        解析 JSON 数据
        """
        if isinstance(json_data, str):
            return json.loads(json_data)
        elif isinstance(json_data, dict):
            return json_data
        else:
            raise ValueError("无效的数据类型")
    
    def extract_wave_data(self, wave_key):
        """
        提取特定周波的波形数据
        """
        wave_data = self.data.get(wave_key, {})
        return {
            'current': {
                'Ia': float(wave_data.get('Ia', 0)),
                'Ib': float(wave_data.get('Ib', 0)),
                'Ic': float(wave_data.get('Ic', 0)),
                'I0': float(wave_data.get('I0', 0))
            },
            'voltage': {
                'Ua': float(wave_data.get('Ua', 0)),
                'Ub': float(wave_data.get('Ub', 0)),
                'Uc': float(wave_data.get('Uc', 0)),
                'U0': float(wave_data.get('U0', 0))
            }
        }
    
    def analyze_fault_characteristics(self):
        """
        分析故障特征
        """
        return {
            'line_name': self.data.get('line_name'),
            'station_name': self.data.get('station_name'),
            'time': self.data.get('time'),
            'reclosure': self.data.get('reclosure'),
            'error_type': self.data.get('error_type_in_machine', {})
        }
    
    def calculate_wave_changes(self):
        """
        计算波形变化
        """
        waves = [
            'error_wave_one_cycle_ago', 
            'error_wave_one_cycle_after', 
            'error_wave_eight_cycle_after'
        ]
        
        changes = {}
        for i in range(1, len(waves)):
            before = self.extract_wave_data(waves[i-1])
            after = self.extract_wave_data(waves[i])
            
            changes[f'change_{waves[i]}'] = {
                'current': {
                    phase: after['current'][phase] - before['current'][phase] 
                    for phase in ['Ia', 'Ib', 'Ic', 'I0']
                },
                'voltage': {
                    phase: after['voltage'][phase] - before['voltage'][phase] 
                    for phase in ['Ua', 'Ub', 'Uc', 'U0']
                }
            }
        
        return changes

    def extract_input_data(self):
        """
        提取输入数据
        """
        line_name = self.data.get('line_name')
        one_cycle_ago = self.extract_wave_data('error_wave_one_cycle_ago')
        one_cycle_after = self.extract_wave_data('error_wave_one_cycle_after')
        again_cycle_after = self.extract_wave_data('error_again_wave_one_cycle_after')

        input_data = (
            f'线路名称：{line_name}; '
            f'故障前一周波模拟值：{one_cycle_ago}; '
            f'故障后一周波模拟值：{one_cycle_after}; '
            f'再次故障后一周波模拟值：{again_cycle_after}; '
            f'重合闸数量：两套; '
            '请用json形式给出重合闸小结、分析结论和故障分类。'
        )
        input_dict = {
            'line_name': line_name,
            'one_cycle_ago': one_cycle_ago,
            'one_cycle_after': one_cycle_after,
            'again_cycle_after': again_cycle_after,
            'reclosure': 2
        }
        return input_data, input_dict
    
    def _prepare_fault_data(self, data_dict):
        """
        准备故障数据
        """
        fault_data = {
            'U_0': data_dict['one_cycle_after']['voltage']['U0'],
            'U_a': data_dict['one_cycle_after']['voltage']['Ua'],
            'U_b': data_dict['one_cycle_after']['voltage']['Ub'],
            'U_c': data_dict['one_cycle_after']['voltage']['Uc'],
            'I_a_before': data_dict['one_cycle_ago']['current']['Ia'],
            'I_a_after': data_dict['one_cycle_after']['current']['Ia'],
            'I_b_before': data_dict['one_cycle_ago']['current']['Ib'],
            'I_b_after': data_dict['one_cycle_after']['current']['Ib'],
            'I_c_before': data_dict['one_cycle_ago']['current']['Ic'],
            'I_c_after': data_dict['one_cycle_after']['current']['Ic'],
            'I_0': data_dict['one_cycle_after']['current']['I0']
        }
        return fault_data

    def analyze_single_output(self):
        input_data, input_dict = self.extract_input_data()

        # analysis logic
        fault_data = self._prepare_fault_data(input_dict)
        result = self.analyzer.comprehensive_fault_analysis(fault_data)
        
        return input_data, result
