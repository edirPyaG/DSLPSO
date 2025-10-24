"""
参数敏感性分析 - 缓冲区下界分析
分析changing_lowerbound文件夹下不同参数配置的性能
"""

import os
import numpy as np
import pandas as pd
from scipy.stats import wilcoxon, friedmanchisquare
import re


def read_total_file(filepath):
    """
    读取total文件,提取30次运行结果和统计数据
    
    参数:
        filepath: 文件路径
    
    返回:
        data: 30次运行的结果数组
        avg: 平均值
        std: 标准差
        best: 最优值
    """
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    # 提取前30行数据(30次运行结果)
    data = []
    for i, line in enumerate(lines):
        if i < 30:
            try:
                value = float(line.strip())
                data.append(value)
            except:
                continue
        else:
            # 提取统计数据
            if 'average=' in line:
                avg = float(line.split('=')[1].strip())
            elif 'std=' in line:
                std = float(line.split('=')[1].strip())
            elif 'best=' in line:
                best = float(line.split('=')[1].strip())
    
    return np.array(data), avg, std, best


def extract_function_number(filename):
    """从文件名提取函数编号"""
    match = re.match(r'(\d+)_30_10total_DRLPSO\.txt', filename)
    if match:
        return int(match.group(1))
    return None


def analyze_parameter_sensitivity(base_folder, param_values):
    """
    分析参数敏感性
    
    参数:
        base_folder: 基础文件夹路径
        param_values: 参数值列表,如 [5, 10, 20, 30, 50, 60]
    """
    
    # 存储所有数据
    all_results = {}
    
    # 遍历每个参数配置
    for param in param_values:
        param_folder = os.path.join(base_folder, str(param))
        
        if not os.path.exists(param_folder):
            print(f"警告: 文件夹 {param_folder} 不存在,跳过")
            continue
        
        # 获取该参数下的所有文件
        files = [f for f in os.listdir(param_folder) 
                if f.endswith('total_DRLPSO.txt')]
        
        # 按函数编号排序
        files_with_num = []
        for f in files:
            func_num = extract_function_number(f)
            if func_num is not None:
                files_with_num.append((func_num, f))
        
        files_with_num.sort(key=lambda x: x[0])
        
        # 读取每个函数的数据
        param_results = {}
        for func_num, filename in files_with_num:
            filepath = os.path.join(param_folder, filename)
            data, avg, std, best = read_total_file(filepath)
            param_results[func_num] = {
                'data': data,
                'avg': avg,
                'std': std,
                'best': best
            }
        
        all_results[param] = param_results
    
    return all_results


def perform_statistical_tests(all_results, param_values, baseline_param):
    """
    执行统计检验,比较各参数配置与基准参数的差异
    
    参数:
        all_results: 所有结果数据
        param_values: 参数值列表
        baseline_param: 基准参数值(用于比较)
    """
    
    # 获取函数编号列表
    func_nums = sorted(all_results[baseline_param].keys())
    
    # 创建结果DataFrame
    comparison_results = []
    
    for func_num in func_nums:
        row = {'Function': f'F{func_num}'}
        
        # 基准参数的数据
        baseline_data = all_results[baseline_param][func_num]['data']
        baseline_avg = all_results[baseline_param][func_num]['avg']
        baseline_std = all_results[baseline_param][func_num]['std']
        
        row[f'Param={baseline_param}'] = f'{baseline_avg:.2E}±{baseline_std:.2E}'
        
        # 与其他参数比较
        for param in param_values:
            if param == baseline_param:
                continue
            
            if func_num not in all_results[param]:
                row[f'Param={param}'] = 'N/A'
                continue
            
            compare_data = all_results[param][func_num]['data']
            compare_avg = all_results[param][func_num]['avg']
            compare_std = all_results[param][func_num]['std']
            
            # Wilcoxon符号秩检验
            try:
                stat, p_value = wilcoxon(baseline_data, compare_data)
                
                if p_value < 0.05:
                    if baseline_avg < compare_avg:
                        significance = '+'  # 基准更好
                    else:
                        significance = '-'  # 比较参数更好
                else:
                    significance = '≈'  # 无显著差异
            except:
                significance = '?'  # 检验失败
            
            row[f'Param={param}'] = f'{compare_avg:.2E}±{compare_std:.2E} ({significance})'
        
        comparison_results.append(row)
    
    df = pd.DataFrame(comparison_results)
    return df


def calculate_summary_statistics(all_results, param_values, baseline_param):
    """
    计算汇总统计(+/-/≈的数量)
    
    参数:
        all_results: 所有结果数据
        param_values: 参数值列表
        baseline_param: 基准参数值
    """
    
    func_nums = sorted(all_results[baseline_param].keys())
    
    summary = {}
    
    for param in param_values:
        if param == baseline_param:
            continue
        
        better = 0  # +
        similar = 0  # ≈
        worse = 0   # -
        
        for func_num in func_nums:
            if func_num not in all_results[param]:
                continue
            
            baseline_data = all_results[baseline_param][func_num]['data']
            baseline_avg = all_results[baseline_param][func_num]['avg']
            compare_data = all_results[param][func_num]['data']
            compare_avg = all_results[param][func_num]['avg']
            
            try:
                stat, p_value = wilcoxon(baseline_data, compare_data)
                
                if p_value < 0.05:
                    if baseline_avg < compare_avg:
                        better += 1
                    else:
                        worse += 1
                else:
                    similar += 1
            except:
                pass
        
        summary[param] = f'{better}/{similar}/{worse}'
    
    return summary


def generate_performance_table(all_results, param_values):
    """
    生成性能对比表(所有参数配置)
    
    参数:
        all_results: 所有结果数据
        param_values: 参数值列表
    """
    
    # 获取所有函数编号
    func_nums = set()
    for param in param_values:
        func_nums.update(all_results[param].keys())
    func_nums = sorted(func_nums)
    
    # 创建表格
    rows = []
    for func_num in func_nums:
        row = {'Function': f'F{func_num}'}
        
        for param in param_values:
            if func_num in all_results[param]:
                avg = all_results[param][func_num]['avg']
                std = all_results[param][func_num]['std']
                row[f'Lower={param}'] = f'{avg:.2E}±{std:.2E}'
            else:
                row[f'Lower={param}'] = 'N/A'
        
        rows.append(row)
    
    df = pd.DataFrame(rows)
    return df


def calculate_rankings(all_results, param_values):
    """
    计算每个参数配置在每个函数上的排名
    
    参数:
        all_results: 所有结果数据
        param_values: 参数值列表
    """
    
    func_nums = set()
    for param in param_values:
        func_nums.update(all_results[param].keys())
    func_nums = sorted(func_nums)
    
    rankings = {param: [] for param in param_values}
    
    for func_num in func_nums:
        # 收集该函数上所有参数的平均值
        param_avgs = []
        for param in param_values:
            if func_num in all_results[param]:
                avg = all_results[param][func_num]['avg']
                param_avgs.append((param, avg))
        
        # 排序(值越小排名越好)
        param_avgs.sort(key=lambda x: x[1])
        
        # 分配排名
        for rank, (param, avg) in enumerate(param_avgs, 1):
            rankings[param].append(rank)
    
    # 计算平均排名
    avg_rankings = {}
    for param in param_values:
        if rankings[param]:
            avg_rankings[param] = np.mean(rankings[param])
        else:
            avg_rankings[param] = None
    
    return avg_rankings, rankings


def main():
    """主函数"""
    
    # 设置路径
    base_folder = r'e:\科研\已有成果\SLPSO\SLPSO\DRLPSO_CEC2021_先前的数据\Analyze_of_bound\changing_lowerbound'
    
    # 参数值列表
    param_values = [5, 10, 20, 30, 50, 60]
    
    # 基准参数(用于统计检验比较)
    baseline_param = 10  # 可以根据需要修改
    
    print("=" * 80)
    print("缓冲区下界参数敏感性分析")
    print("=" * 80)
    print(f"分析参数值: {param_values}")
    print(f"基准参数: {baseline_param}")
    print()
    
    # 读取所有数据
    print("正在读取数据...")
    all_results = analyze_parameter_sensitivity(base_folder, param_values)
    print(f"成功读取 {len(all_results)} 个参数配置的数据")
    print()
    
    # 1. 生成性能对比表
    print("生成性能对比表...")
    performance_table = generate_performance_table(all_results, param_values)
    output_file1 = os.path.join(base_folder, 'performance_comparison.xlsx')
    performance_table.to_excel(output_file1, index=False)
    print(f"性能对比表已保存至: {output_file1}")
    print(performance_table)
    print()
    
    # 2. 统计检验(与基准参数比较)
    print(f"执行统计检验(基准参数: Lower={baseline_param})...")
    comparison_df = perform_statistical_tests(all_results, param_values, baseline_param)
    output_file2 = os.path.join(base_folder, f'statistical_comparison_baseline{baseline_param}.xlsx')
    comparison_df.to_excel(output_file2, index=False)
    print(f"统计检验结果已保存至: {output_file2}")
    print(comparison_df)
    print()
    
    # 3. 计算汇总统计
    print("计算汇总统计(+/≈/-)...")
    summary = calculate_summary_statistics(all_results, param_values, baseline_param)
    print(f"与基准参数(Lower={baseline_param})比较:")
    for param, result in summary.items():
        print(f"  Lower={param}: {result}")
    print()
    
    # 4. 计算排名
    print("计算参数配置排名...")
    avg_rankings, detailed_rankings = calculate_rankings(all_results, param_values)
    print("平均排名(越小越好):")
    for param in sorted(avg_rankings.keys()):
        rank = avg_rankings[param]
        if rank is not None:
            print(f"  Lower={param}: {rank:.2f}")
    print()
    
    # 保存排名到文件
    ranking_df = pd.DataFrame({
        'Parameter': [f'Lower={p}' for p in sorted(avg_rankings.keys())],
        'Average Rank': [avg_rankings[p] for p in sorted(avg_rankings.keys())]
    })
    output_file3 = os.path.join(base_folder, 'parameter_rankings.xlsx')
    ranking_df.to_excel(output_file3, index=False)
    print(f"排名结果已保存至: {output_file3}")
    print()
    
    # 5. 生成最优参数配置汇总
    print("生成最优参数配置汇总...")
    best_configs = []
    func_nums = sorted(all_results[param_values[0]].keys())
    
    for func_num in func_nums:
        best_param = None
        best_avg = float('inf')
        
        for param in param_values:
            if func_num in all_results[param]:
                avg = all_results[param][func_num]['avg']
                if avg < best_avg:
                    best_avg = avg
                    best_param = param
        
        if best_param is not None:
            best_configs.append({
                'Function': f'F{func_num}',
                'Best Lower Bound': best_param,
                'Best Average': f'{best_avg:.2E}',
                'Best Std': f'{all_results[best_param][func_num]["std"]:.2E}'
            })
    
    best_config_df = pd.DataFrame(best_configs)
    output_file4 = os.path.join(base_folder, 'best_parameter_configs.xlsx')
    best_config_df.to_excel(output_file4, index=False)
    print(f"最优参数配置已保存至: {output_file4}")
    print(best_config_df)
    print()
    
    print("=" * 80)
    print("分析完成!")
    print(f"生成文件:")
    print(f"  1. {output_file1}")
    print(f"  2. {output_file2}")
    print(f"  3. {output_file3}")
    print(f"  4. {output_file4}")
    print("=" * 80)


if __name__ == '__main__':
    main()
