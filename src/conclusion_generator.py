class FaultConclusionGenerator:
    def __init__(self, fault_description1, fault_description2):
        """
        初始化故障结论生成器
        
        :param fault_description1: 第一个故障描述
        :param fault_description2: 第二个故障描述
        """
        self.fault_descriptions = [fault_description1, fault_description2]
    
    def analyze_zero_voltage(self):
        """分析零序电压"""
        return all('大于5V' in desc['zero_voltage']['result'] for desc in self.fault_descriptions)
    
    def analyze_phase_voltage(self):
        """分析相电压"""
        def count_voltage(result_str, phase):
            return sum(phase in result for result in 
                       [desc['phase_voltage']['result'] for desc in self.fault_descriptions])
        
        return {
            'A': count_voltage('A相电压大于55V', 'A相电压大于55V'),
            'B': count_voltage('B相电压大于55V', 'B相电压大于55V'),
            'C': count_voltage('C相电压大于55V', 'C相电压大于55V')
        }
    
    def analyze_current_changes(self):
        """分析电流变化"""
        current_changes = [
            desc['current_change']['sorted_changes'] for desc in self.fault_descriptions
        ]
        
        phase_current_changes = {
            'A': [changes['A'] for changes in current_changes],
            'B': [changes['B'] for changes in current_changes],
            'C': [changes['C'] for changes in current_changes]
        }
        
        return {
            'mean_changes': {
                phase: sum(changes) / len(changes) 
                for phase, changes in phase_current_changes.items()
            },
            'max_changes': {
                phase: max(changes) 
                for phase, changes in phase_current_changes.items()
            }
        }
    
    def analyze_zero_current(self):
        """分析零序电流"""
        return all('大于1A' in desc['zero_current']['result'] for desc in self.fault_descriptions)
    
    def determine_fault_phase(self, phase_voltage, current_changes):
        """确定故障相"""
        # 电压小于55V的相
        low_voltage_phases = [
            phase for phase in ['A', 'B', 'C']
            if phase_voltage[phase] < 2  # 两个描述中都低于55V
        ]
        
        # 如果没有低压相，返回None
        if not low_voltage_phases:
            return None
        
        # 在低压相中选择电流变化最大的相
        fault_candidates = [
            (phase, current_changes['max_changes'][phase])
            for phase in low_voltage_phases
        ]
        
        return max(fault_candidates, key=lambda x: x[1])[0]
    
    def generate_reclosure_summary(self, phase_voltage):
        """生成重合闸小结"""
        if all(count == 2 for count in phase_voltage.values()):
            return '两套保护重合闸动作，重合后三相电压均大于55V，零序电压小于5V，重合后故障消失，重合成功。'
        return '重合闸动作后故障未完全消除'
    
    def generate_analysis_conclusion(self, zero_voltage, phase_voltage, current_changes, zero_current, fault_phase):
        """生成详细分析结论"""
        conclusion_parts = []
        
        if zero_voltage:
            conclusion_parts.append('故障时零序电压大于5V')
        
        # 描述相电压情况
        low_voltage_phases = [
            phase for phase in ['A', 'B', 'C'] 
            if phase_voltage[phase] < 2  # 两个描述中都低于55V
        ]
        if low_voltage_phases:
            conclusion_parts.append(f'仅有{"、".join(low_voltage_phases)}相电压小于55V')
        
        # 描述电流变化
        max_change_phase = max(
            current_changes['max_changes'], 
            key=current_changes['max_changes'].get
        )
        if max_change_phase != fault_phase:
            conclusion_parts.append(
                f'{max_change_phase}相电流变化量大于其他相电流变化量的5倍'
            )
        
        if zero_current:
            conclusion_parts.append('零序电流大于1A')
        
        # 添加具体故障描述
        if fault_phase:
            conclusion_parts.append(f'符合{fault_phase}相接地故障特征')
            conclusion_parts.append(f'220kV楼牵Ⅱ线发生{fault_phase}相接地故障')
        
        conclusion_parts.append('重合成功')
        
        return '，'.join(conclusion_parts) + '。'
    
    def generate_conclusion(self):
        """
        生成最终故障结论
        
        :return: 故障结论字典
        """
        # 主分析流程
        zero_voltage = self.analyze_zero_voltage()
        phase_voltage = self.analyze_phase_voltage()
        current_changes = self.analyze_current_changes()
        zero_current = self.analyze_zero_current()
        
        # 确定故障相
        fault_phase = self.determine_fault_phase(phase_voltage, current_changes)
        
        # 生成重合闸小结
        reclosure_summary = self.generate_reclosure_summary(phase_voltage)
        
        # 生成分析结论
        analysis_conclusion = self.generate_analysis_conclusion(
            zero_voltage, phase_voltage, current_changes, zero_current, fault_phase
        )
        
        # 生成最终结果
        result = {
            '重合闸小结': reclosure_summary,
            '分析结论': analysis_conclusion,
            '故障分类': f'{fault_phase}相接地故障'
        }
        
        return result

# 使用示例
def generate_fault_conclusion(fault_description1, fault_description2):
    """
    便捷的故障结论生成函数
    
    :param fault_description1: 第一个故障描述
    :param fault_description2: 第二个故障描述
    :return: 故障结论字典
    """
    generator = FaultConclusionGenerator(fault_description1, fault_description2)
    return generator.generate_conclusion()


if __name__ == '__main__':
    # 测试代码
    fault_description1 = {
        'zero_voltage': {'result': '零序电压大于5V', 'is_ground_fault': True},
        'phase_voltage': {'result': 'A相电压大于55V，B相电压小于55V，C相电压大于55V', 'fault_phase': None},
        'current_change': {
            'result': '各相电流变化量：B相电流变化量为6.086A，A相电流变化量为0.13A，C相电流变化量为0.03A', 
            'comparative_analysis': 'B相电流变化量大于A相电流变化量约46.8倍，A相电流变化量大于C相电流变化量约4.3倍', 
            'current_changes': {'A': 0.13, 'B': 6.086, 'C': 0.03}, 
            'sorted_changes': {'B': 6.086, 'A': 0.13, 'C': 0.03}
        },
        'zero_current': {'result': '零序电流大于1A', 'is_ground_fault': True}
    }

    fault_description2 = {
        'zero_voltage': {'result': '零序电压大于5V', 'is_ground_fault': True},
        'phase_voltage': {'result': 'A相电压大于55V，B相电压小于55V，C相电压大于55V', 'fault_phase': None},
        'current_change': {
            'result': '各相电流变化量：B相电流变化量为25.461A，A相电流变化量为0.675A，C相电流变化量为0.118A', 
            'comparative_analysis': 'B相电流变化量大于A相电流变化量约37.7倍，A相电流变化量大于C相电流变化量约5.7倍', 
            'current_changes': {'A': 0.675, 'B': 25.461, 'C': 0.118}, 
            'sorted_changes': {'B': 25.461, 'A': 0.675, 'C': 0.118}
        },
        'zero_current': {'result': '零序电流大于1A', 'is_ground_fault': True}
    }

    result = generate_fault_conclusion(fault_description1, fault_description2)
    # print(result)
