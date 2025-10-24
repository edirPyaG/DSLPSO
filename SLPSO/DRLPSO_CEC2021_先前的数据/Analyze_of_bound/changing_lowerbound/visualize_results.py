"""
参数敏感性可视化分析
生成各种图表展示changing_lowerbound的分析结果
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import rcParams
import re

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial']
plt.rcParams['axes.unicode_minus'] = False


def read_total_file(filepath):
    """读取total文件"""
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    data = []
    for i, line in enumerate(lines):
        if i < 30:
            try:
                value = float(line.strip())
                data.append(value)
            except:
                continue
        else:
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


def load_all_data(base_folder, param_values):
    """加载所有数据"""
    all_results = {}
    
    for param in param_values:
        param_folder = os.path.join(base_folder, str(param))
        
        if not os.path.exists(param_folder):
            continue
        
        files = [f for f in os.listdir(param_folder) 
                if f.endswith('total_DRLPSO.txt')]
        
        files_with_num = []
        for f in files:
            func_num = extract_function_number(f)
            if func_num is not None:
                files_with_num.append((func_num, f))
        
        files_with_num.sort(key=lambda x: x[0])
        
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


def plot_boxplot_by_function(all_results, param_values, output_folder):
    """
    为每个函数绘制箱线图,展示不同参数配置的分布
    """
    func_nums = sorted(all_results[param_values[0]].keys())
    
    # 创建3x4的子图(假设10个函数)
    n_funcs = len(func_nums)
    n_cols = 4
    n_rows = (n_funcs + n_cols - 1) // n_cols
    
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(16, 4*n_rows), dpi=100)
    axes = axes.flatten() if n_rows > 1 else [axes]
    
    for idx, func_num in enumerate(func_nums):
        ax = axes[idx]
        
        # 准备数据
        data_to_plot = []
        labels = []
        for param in param_values:
            if func_num in all_results[param]:
                data_to_plot.append(all_results[param][func_num]['data'])
                labels.append(f'{param}')
        
        # 绘制箱线图
        bp = ax.boxplot(data_to_plot, tick_labels=labels, patch_artist=True)
        
        # 美化
        for patch in bp['boxes']:
            patch.set_facecolor('lightblue')
        
        ax.set_title(f'F{func_num}', fontsize=12, fontweight='bold')
        ax.set_xlabel('Lower Bound', fontsize=10)
        ax.set_ylabel('Fitness Value', fontsize=10)
        ax.set_yscale('log')  # 对数坐标
        ax.grid(True, alpha=0.3)
    
    # 隐藏多余的子图
    for idx in range(len(func_nums), len(axes)):
        axes[idx].axis('off')
    
    plt.tight_layout()
    output_file = os.path.join(output_folder, 'boxplot_by_function.png')
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"箱线图已保存至: {output_file}")


def plot_heatmap(all_results, param_values, output_folder):
    """
    绘制热图:参数值 × 函数编号
    """
    func_nums = sorted(all_results[param_values[0]].keys())
    
    # 创建数据矩阵
    data_matrix = []
    for param in param_values:
        row = []
        for func_num in func_nums:
            if func_num in all_results[param]:
                # 使用对数值以便可视化
                avg = all_results[param][func_num]['avg']
                row.append(np.log10(avg) if avg > 0 else 0)
            else:
                row.append(np.nan)
        data_matrix.append(row)
    
    # 绘制热图
    fig, ax = plt.subplots(figsize=(12, 6))
    
    im = ax.imshow(data_matrix, cmap='YlOrRd', aspect='auto')
    
    # 设置刻度
    ax.set_xticks(np.arange(len(func_nums)))
    ax.set_yticks(np.arange(len(param_values)))
    ax.set_xticklabels([f'F{fn}' for fn in func_nums])
    ax.set_yticklabels([f'{p}' for p in param_values])
    
    # 标签
    ax.set_xlabel('Test Function', fontsize=12, fontweight='bold')
    ax.set_ylabel('Lower Bound Value', fontsize=12, fontweight='bold')
    ax.set_title('Performance Heatmap (log10 of Average Fitness)', 
                 fontsize=14, fontweight='bold')
    
    # 颜色条
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('log10(Fitness)', rotation=270, labelpad=20)
    
    # 在每个格子中显示数值
    for i in range(len(param_values)):
        for j in range(len(func_nums)):
            if not np.isnan(data_matrix[i][j]):
                text = ax.text(j, i, f'{data_matrix[i][j]:.1f}',
                             ha="center", va="center", color="black", fontsize=8)
    
    plt.tight_layout()
    output_file = os.path.join(output_folder, 'heatmap_performance.png')
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"热图已保存至: {output_file}")


def plot_parameter_sensitivity_curve(all_results, param_values, output_folder):
    """
    绘制参数敏感性曲线:展示性能随参数变化的趋势
    """
    func_nums = sorted(all_results[param_values[0]].keys())
    
    fig, axes = plt.subplots(2, 5, figsize=(20, 8))
    axes = axes.flatten()
    
    for idx, func_num in enumerate(func_nums):
        ax = axes[idx]
        
        # 收集数据
        x_values = []
        y_avg = []
        y_std = []
        
        for param in param_values:
            if func_num in all_results[param]:
                x_values.append(param)
                y_avg.append(all_results[param][func_num]['avg'])
                y_std.append(all_results[param][func_num]['std'])
        
        x_values = np.array(x_values)
        y_avg = np.array(y_avg)
        y_std = np.array(y_std)
        
        # 绘制曲线和误差带
        ax.plot(x_values, y_avg, 'o-', linewidth=2, markersize=8, label='Average')
        ax.fill_between(x_values, y_avg - y_std, y_avg + y_std, 
                        alpha=0.3, label='Std Range')
        
        # 标记最优点
        best_idx = np.argmin(y_avg)
        ax.plot(x_values[best_idx], y_avg[best_idx], 'r*', 
               markersize=15, label='Best')
        
        ax.set_title(f'F{func_num}', fontsize=12, fontweight='bold')
        ax.set_xlabel('Lower Bound', fontsize=10)
        ax.set_ylabel('Fitness Value', fontsize=10)
        ax.set_yscale('log')
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=8)
    
    plt.tight_layout()
    output_file = os.path.join(output_folder, 'parameter_sensitivity_curves.png')
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"参数敏感性曲线已保存至: {output_file}")


def plot_ranking_bar(all_results, param_values, output_folder):
    """
    绘制参数配置的平均排名柱状图
    """
    func_nums = sorted(all_results[param_values[0]].keys())
    
    rankings = {param: [] for param in param_values}
    
    for func_num in func_nums:
        param_avgs = []
        for param in param_values:
            if func_num in all_results[param]:
                avg = all_results[param][func_num]['avg']
                param_avgs.append((param, avg))
        
        param_avgs.sort(key=lambda x: x[1])
        
        for rank, (param, avg) in enumerate(param_avgs, 1):
            rankings[param].append(rank)
    
    # 计算平均排名
    avg_rankings = {param: np.mean(ranks) for param, ranks in rankings.items()}
    
    # 绘制柱状图
    fig, ax = plt.subplots(figsize=(10, 6))
    
    params = sorted(avg_rankings.keys())
    ranks = [avg_rankings[p] for p in params]
    
    bars = ax.bar(range(len(params)), ranks, color='steelblue', alpha=0.7, edgecolor='black')
    
    # 标注数值
    for i, bar in enumerate(bars):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
               f'{height:.2f}',
               ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    ax.set_xlabel('Lower Bound Value', fontsize=12, fontweight='bold')
    ax.set_ylabel('Average Rank', fontsize=12, fontweight='bold')
    ax.set_title('Average Ranking of Different Parameter Configurations\n(Lower is Better)', 
                fontsize=14, fontweight='bold')
    ax.set_xticks(range(len(params)))
    ax.set_xticklabels([f'{p}' for p in params])
    ax.grid(True, axis='y', alpha=0.3)
    
    plt.tight_layout()
    output_file = os.path.join(output_folder, 'average_ranking_bar.png')
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"平均排名柱状图已保存至: {output_file}")


def plot_performance_profile(all_results, param_values, output_folder):
    """
    绘制性能剖面图(Performance Profile)
    """
    func_nums = sorted(all_results[param_values[0]].keys())
    
    # 计算性能比率
    performance_ratios = {param: [] for param in param_values}
    
    for func_num in func_nums:
        # 找到最优值
        best_value = float('inf')
        for param in param_values:
            if func_num in all_results[param]:
                avg = all_results[param][func_num]['avg']
                if avg < best_value:
                    best_value = avg
        
        # 计算每个参数的性能比率
        for param in param_values:
            if func_num in all_results[param]:
                avg = all_results[param][func_num]['avg']
                ratio = avg / best_value if best_value > 0 else 1.0
                performance_ratios[param].append(ratio)
    
    # 绘制累积分布曲线
    fig, ax = plt.subplots(figsize=(10, 6))
    
    tau_max = 10  # 最大比率
    tau_values = np.linspace(1, tau_max, 100)
    
    for param in param_values:
        ratios = np.array(performance_ratios[param])
        prob = [np.sum(ratios <= tau) / len(ratios) for tau in tau_values]
        ax.plot(tau_values, prob, linewidth=2, marker='o', 
               markersize=4, label=f'Lower={param}')
    
    ax.set_xlabel('Performance Ratio τ', fontsize=12, fontweight='bold')
    ax.set_ylabel('P(ratio ≤ τ)', fontsize=12, fontweight='bold')
    ax.set_title('Performance Profile', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=10)
    ax.set_xlim([1, tau_max])
    ax.set_ylim([0, 1.05])
    
    plt.tight_layout()
    output_file = os.path.join(output_folder, 'performance_profile.png')
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"性能剖面图已保存至: {output_file}")


def plot_violin_comparison(all_results, param_values, output_folder, selected_funcs=[1, 2, 5]):
    """
    为选定的函数绘制小提琴图,展示数据分布
    """
    fig, axes = plt.subplots(1, len(selected_funcs), figsize=(6*len(selected_funcs), 6))
    
    if len(selected_funcs) == 1:
        axes = [axes]
    
    for idx, func_num in enumerate(selected_funcs):
        ax = axes[idx]
        
        # 准备数据
        data_to_plot = []
        labels = []
        for param in param_values:
            if func_num in all_results[param]:
                data = all_results[param][func_num]['data']
                # 检查数据是否有足够的变异性
                if np.std(data) > 1e-15:  # 避免标准差为0的数据
                    data_to_plot.append(data)
                    labels.append(f'{param}')
        
        if not data_to_plot:
            ax.text(0.5, 0.5, 'No valid data\n(std ≈ 0)', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=12)
            ax.set_title(f'F{func_num}', fontsize=14, fontweight='bold')
            continue
        
        # 绘制小提琴图 - 使用try-except以防出错
        try:
            parts = ax.violinplot(data_to_plot, positions=range(len(labels)),
                                 showmeans=True, showmedians=True)
            
            # 美化
            for pc in parts['bodies']:
                pc.set_facecolor('lightblue')
                pc.set_alpha(0.7)
        except Exception as e:
            # 如果小提琴图失败,使用箱线图代替
            print(f"Warning: Violin plot failed for F{func_num}, using boxplot instead. Error: {e}")
            bp = ax.boxplot(data_to_plot, tick_labels=labels, patch_artist=True)
            for patch in bp['boxes']:
                patch.set_facecolor('lightblue')
        
        ax.set_title(f'F{func_num}', fontsize=14, fontweight='bold')
        ax.set_xlabel('Lower Bound', fontsize=12)
        ax.set_ylabel('Fitness Value', fontsize=12)
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels)
        ax.set_yscale('log')
        ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    output_file = os.path.join(output_folder, 'violin_plot_comparison.png')
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"小提琴图已保存至: {output_file}")


def main():
    """主函数"""
    
    # 设置路径
    base_folder = r'e:\科研\已有成果\SLPSO\SLPSO\DRLPSO_CEC2021_先前的数据\Analyze_of_bound\changing_lowerbound'
    output_folder = base_folder
    
    # 参数值列表
    param_values = [5, 10, 20, 30, 50, 60]
    
    print("=" * 80)
    print("生成参数敏感性可视化图表")
    print("=" * 80)
    print()
    
    # 加载数据
    print("正在加载数据...")
    all_results = load_all_data(base_folder, param_values)
    print(f"成功加载 {len(all_results)} 个参数配置的数据")
    print()
    
    # 生成各种图表
    print("生成图表...")
    print()
    
    print("1. 生成箱线图...")
    plot_boxplot_by_function(all_results, param_values, output_folder)
    
    print("2. 生成热图...")
    plot_heatmap(all_results, param_values, output_folder)
    
    print("3. 生成参数敏感性曲线...")
    plot_parameter_sensitivity_curve(all_results, param_values, output_folder)
    
    print("4. 生成平均排名柱状图...")
    plot_ranking_bar(all_results, param_values, output_folder)
    
    print("5. 生成性能剖面图...")
    plot_performance_profile(all_results, param_values, output_folder)
    
    print("6. 生成小提琴图...")
    plot_violin_comparison(all_results, param_values, output_folder)
    
    print()
    print("=" * 80)
    print("所有图表生成完成!")
    print(f"输出文件夹: {output_folder}")
    print("=" * 80)


if __name__ == '__main__':
    main()
