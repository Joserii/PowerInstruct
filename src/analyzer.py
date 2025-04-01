class FaultAnalyzer:
    def __init__(self):
        # 阈值设置
        self.U_THR = 5  # 零序电压阈值
        self.U_P_THR = 55  # 相电压阈值
        self.I_THR = 1  # 零序电流阈值

    def analyze_zero_sequence_voltage(self, U_0):
        """
        分析零序电压
        :param U_0: 零序电压值
        :return: 分析结果
        """
        U_0_comparison = (
            '大于' if U_0 > self.U_THR else 
            '小于' if U_0 < self.U_THR else 
            '等于'
        )
        result = f'零序电压{U_0_comparison}{self.U_THR}V'
        # print(result)
        
        is_ground_fault = U_0 > self.U_THR
        return {
            'result': result,
            'is_ground_fault': is_ground_fault
        }

    def analyze_phase_voltage(self, U_a, U_b, U_c):
        """
        分析各相电压
        :param U_a: A相电压
        :param U_b: B相电压
        :param U_c: C相电压
        :return: 分析结果
        """
        U_a_comparison = (
            '大于' if U_a > self.U_P_THR else 
            '小于' if U_a < self.U_P_THR else 
            '等于'
        )
        U_b_comparison = (
            '大于' if U_b > self.U_P_THR else 
            '小于' if U_b < self.U_P_THR else 
            '等于'
        )
        U_c_comparison = (
            '大于' if U_c > self.U_P_THR else 
            '小于' if U_c < self.U_P_THR else 
            '等于'
        )
        
        result = f'A相电压{U_a_comparison}{self.U_P_THR}V，B相电压{U_b_comparison}{self.U_P_THR}V，C相电压{U_c_comparison}{self.U_P_THR}V'
        # print(result)
        
        # 判断故障相
        fault_phase = None
        if U_a < self.U_P_THR and U_b > self.U_P_THR and U_c > self.U_P_THR:
            fault_phase = 'A'
        
        return {
            'result': result,
            'fault_phase': fault_phase
        }


    def analyze_current_change(self, I_a_before, I_a_after, I_b_before, I_b_after, I_c_before, I_c_after):
        """
        动态分析各相电流变化，并根据变化量大小调整比较顺序
        
        :param I_a_before: A相故障前电流
        :param I_a_after: A相故障后电流
        :param I_b_before: B相故障前电流
        :param I_b_after: B相故障后电流
        :param I_c_before: C相故障前电流
        :param I_c_after: C相故障后电流
        :return: 分析结果
        """
        # 计算各相电流变化量
        I_a_change = abs(I_a_after - I_a_before)
        I_b_change = abs(I_b_after - I_b_before)
        I_c_change = abs(I_c_after - I_c_before)
        
        # 创建变化量字典
        current_changes = {
            'A': I_a_change,
            'B': I_b_change,
            'C': I_c_change
        }
        
        # 按变化量降序排序
        sorted_changes = sorted(current_changes.items(), key=lambda x: x[1], reverse=True)
        
        # 生成详细结果字符串
        result = f'各相电流变化量：' + '，'.join([f'{phase}相电流变化量为{round(change, 3)}A' for phase, change in sorted_changes])
        # print(result)
        
        # 生成比较分析
        comparative_analysis_parts = []
        for i in range(len(sorted_changes) - 1):
            phase1, change1 = sorted_changes[i]
            phase2, change2 = sorted_changes[i+1]
            
            # 避免除零错误
            if change2 != 0:
                ratio = round(change1 / change2, 1)
                comparative_analysis_parts.append(
                    f'{phase1}相电流变化量大于{phase2}相电流变化量约{ratio}倍'
                )
        
        comparative_analysis = '，'.join(comparative_analysis_parts)
        # print(comparative_analysis)
        
        return {
            'result': result,
            'comparative_analysis': comparative_analysis,
            'current_changes': current_changes,
            'sorted_changes': dict(sorted_changes)
        }


    def analyze_zero_sequence_current(self, I_0):
        """
        分析零序电流
        :param I_0: 零序电流值
        :return: 分析结果
        """
        I_0_comparison = (
            '大于' if I_0 > self.I_THR else 
            '小于' if I_0 < self.I_THR else 
            '等于'
        )
        result = f'零序电流{I_0_comparison}{self.I_THR}A'
        # print(result)
        
        is_ground_fault = I_0 > self.I_THR
        return {
            'result': result,
            'is_ground_fault': is_ground_fault
        }

    def comprehensive_fault_analysis(self, data):
        """
        综合故障分析
        :param data: 包含故障数据的字典
        :return: 综合分析结果
        """
        # 零序电压分析
        zero_voltage_result = self.analyze_zero_sequence_voltage(data['U_0'])
        
        # 相电压分析
        phase_voltage_result = self.analyze_phase_voltage(
            data['U_a'], data['U_b'], data['U_c']
        )
        
        # 电流变化分析
        current_change_result = self.analyze_current_change(
            data['I_a_before'], data['I_a_after'],
            data['I_b_before'], data['I_b_after'],
            data['I_c_before'], data['I_c_after']
        )
        
        # 零序电流分析
        zero_current_result = self.analyze_zero_sequence_current(data['I_0'])
        
        # 综合判断
        fault_analysis = {
            'zero_voltage': zero_voltage_result,
            'phase_voltage': phase_voltage_result,
            'current_change': current_change_result,
            'zero_current': zero_current_result
        }
        
        return fault_analysis
    

# 示例使用
def main():
    # 准备故障数据
    fault_data = {
        'U_0': 114.608,  # 零序电压
        'U_a': 15.899,   # A相电压
        'U_b': 62.095,   # B相电压
        'U_c': 73.02,    # C相电压
        'I_a_before': 0.079,   # A相故障前电流
        'I_a_after': 16.954,   # A相故障后电流
        'I_b_before': 0.088,   # B相故障前电流
        'I_b_after': 0.462,    # B相故障后电流
        'I_c_before': 0.086,   # C相故障前电流
        'I_c_after': 0.761,    # C相故障后电流
        'I_0': 15.741    # 零序电流
    }

    analyzer = FaultAnalyzer()
    result = analyzer.comprehensive_fault_analysis(fault_data)
    
    # 打印详细分析结果
    print("\n综合故障分析结果:")
    for key, value in result.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
