"""
参数敏感性分析 - 缓冲区下界比较
生成与MATLAB significant_analysis.m相同格式的Excel表格

参照changing_upperbound/significant_analysis.m的处理方法
"""

import os
import re
import math
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy.stats import wilcoxon


@dataclass
class Config:
    """参数配置"""
    name: str
    folder: Path


# ==================== 配置区域 ====================
BASE_DIR = Path(__file__).resolve().parent

# 参数配置列表 - 第一个作为基准列
CONFIGS: List[Config] = [
    Config("Lower=5", BASE_DIR / "5"),
    Config("Lower=10", BASE_DIR / "10"),
    Config("Lower=20", BASE_DIR / "20"),
    Config("Lower=30", BASE_DIR / "30"),
    Config("Lower=50", BASE_DIR / "50"),
    Config("Lower=60", BASE_DIR / "60"),
]

RUNS_PER_FILE = 30  # 每个文件的运行次数
FILENAME_PATTERN = re.compile(r"^(\d+)_30_10total_DRLPSO\.txt$")  # 文件名模式
OUTPUT_FILE = BASE_DIR / "comparison_results_lowerbound.xlsx"  # 输出文件
ALPHA = 0.05  # 显著性水平
# ==================================================


def discover_files(config: Config) -> Dict[int, Path]:
    """
    发现配置文件夹中的所有测试函数文件
    
    参数:
        config: 配置对象
    
    返回:
        Dict[函数编号, 文件路径]
    """
    files: Dict[int, Path] = {}
    
    if not config.folder.exists():
        raise FileNotFoundError(f"文件夹不存在: {config.folder}")
    
    for path in config.folder.glob("*_30_10total_DRLPSO.txt"):
        match = FILENAME_PATTERN.match(path.name)
        if match:
            func_id = int(match.group(1))
            files[func_id] = path
    
    if not files:
        raise FileNotFoundError(f"在 {config.folder} 中未找到匹配文件")
    
    return dict(sorted(files.items()))


def read_runs(path: Path) -> np.ndarray:
    """
    读取文件前30行的运行结果
    
    参数:
        path: 文件路径
    
    返回:
        30次运行结果的numpy数组
    """
    values: List[float] = []
    
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            text = line.strip()
            
            # 跳过空行
            if not text:
                continue
            
            # 遇到统计数据行就停止
            if "=" in text:
                break
            
            try:
                values.append(float(text))
            except ValueError:
                continue
            
            # 读够30个就停止
            if len(values) == RUNS_PER_FILE:
                break
    
    if len(values) != RUNS_PER_FILE:
        raise ValueError(f"期望读取 {RUNS_PER_FILE} 个值，实际读取 {len(values)} 个: {path}")
    
    return np.asarray(values, dtype=float)


def format_stats(data: np.ndarray) -> Tuple[str, float, float]:
    """
    计算并格式化统计数据
    
    参数:
        data: 运行结果数组
    
    返回:
        (格式化字符串, 均值, 标准差)
    """
    mean_val = float(np.mean(data))
    std_val = float(np.std(data, ddof=1))  # 样本标准差
    formatted = f"{mean_val:.2E}±{std_val:.2E}"
    return formatted, mean_val, std_val


def perform_wilcoxon_test(baseline_data: np.ndarray, 
                          compare_data: np.ndarray,
                          baseline_mean: float,
                          compare_mean: float,
                          baseline_std: float,
                          compare_std: float) -> str:
    """
    执行Wilcoxon符号秩检验并返回显著性符号
    
    比较逻辑:
    1. 对均值进行显著性检验
    2. 如果均值有显著差异,则根据均值大小返回结果
    3. 如果均值无显著差异,则对方差进行显著性检验
    4. 如果方差有显著差异,则根据方差大小返回结果(越小越好)
    5. 如果方差也无显著差异,则返回约等于符号
    
    参数:
        baseline_data: 基准数据 (30次运行)
        compare_data: 比较数据 (30次运行)
        baseline_mean: 基准均值
        compare_mean: 比较均值
        baseline_std: 基准标准差
        compare_std: 比较标准差
    
    返回:
        显著性符号: '+' (基准更好), '-' (比较更好), '≈' (无显著差异)
    """
    # 第一步: 对均值进行Wilcoxon显著性检验
    try:
        _, p_value_mean = wilcoxon(
            baseline_data,
            compare_data,
            zero_method="pratt",
            alternative="two-sided",
            mode="approx",
        )
    except ValueError:
        # 处理所有数据相同的情况
        p_value_mean = math.nan
    
    # 第二步: 如果均值有显著差异,直接根据均值比较
    if not math.isnan(p_value_mean) and p_value_mean < ALPHA:
        if baseline_mean < compare_mean:
            return "+"  # 基准均值更小,更好
        else:
            return "-"  # 比较配置均值更小,更好
    
    # 第三步: 均值无显著差异,对方差(标准差)进行显著性检验
    # 使用绝对偏差来比较方差的差异
    baseline_abs_dev = np.abs(baseline_data - baseline_mean)
    compare_abs_dev = np.abs(compare_data - compare_mean)
    
    try:
        _, p_value_var = wilcoxon(
            baseline_abs_dev,
            compare_abs_dev,
            zero_method="pratt",
            alternative="two-sided",
            mode="approx",
        )
    except ValueError:
        p_value_var = math.nan
    
    # 第四步: 如果方差有显著差异,根据方差大小比较(越小越好)
    if not math.isnan(p_value_var) and p_value_var < ALPHA:
        if baseline_std < compare_std:
            return "+"  # 基准方差更小,更稳定,更好
        else:
            return "-"  # 比较配置方差更小,更稳定,更好
    
    # 第五步: 均值和方差都无显著差异
    return "≈"


def evaluate_configs() -> pd.DataFrame:
    """
    评估所有配置并生成DataFrame
    
    返回:
        包含比较结果的DataFrame
    """
    print("=" * 80)
    print("缓冲区下界参数敏感性分析")
    print("=" * 80)
    print(f"参数配置: {[cfg.name for cfg in CONFIGS]}")
    print(f"基准参数: {CONFIGS[0].name}")
    print()
    
    # 预加载所有配置和函数的数据
    data_store: Dict[str, Dict[int, np.ndarray]] = {}
    stats_store: Dict[str, Dict[int, Tuple[str, float, float]]] = {}
    
    print("正在读取数据...")
    for config in CONFIGS:
        print(f"  读取 {config.name}...", end=" ")
        files = discover_files(config)
        data_store[config.name] = {}
        stats_store[config.name] = {}
        
        for func_id, path in files.items():
            runs = read_runs(path)
            data_store[config.name][func_id] = runs
            stats_store[config.name][func_id] = format_stats(runs)
        
        print(f"完成 ({len(files)} 个函数)")
    
    print()
    
    # 获取基准配置和函数列表
    baseline_name = CONFIGS[0].name
    func_ids = sorted(data_store[baseline_name].keys())
    
    # 初始化计数器
    counters: Dict[str, List[int]] = {
        cfg.name: [0, 0, 0]  # [better, similar, worse]
        for cfg in CONFIGS[1:]
    }
    
    # 构建数据行
    rows: List[Dict[str, str]] = []
    
    print("执行统计检验...")
    for func_id in func_ids:
        row: Dict[str, str] = {"Function": f"F{func_id}"}
        
        # 添加基准列
        baseline_text, baseline_mean, _ = stats_store[baseline_name][func_id]
        row[baseline_name] = baseline_text
        baseline_runs = data_store[baseline_name][func_id]
        
        # 与其他配置比较
        for cfg in CONFIGS[1:]:
            cfg_stats = stats_store[cfg.name].get(func_id)
            
            if cfg_stats is None:
                row[cfg.name] = "N/A"
                continue
            
            cfg_text, cfg_mean, cfg_std = cfg_stats
            compare_runs = data_store[cfg.name][func_id]
            
            # 获取基准标准差
            _, _, baseline_std = stats_store[baseline_name][func_id]
            
            # 执行Wilcoxon检验 (增加标准差参数)
            symbol = perform_wilcoxon_test(
                baseline_runs, compare_runs,
                baseline_mean, cfg_mean,
                baseline_std, cfg_std
            )
            
            # 更新计数器
            if symbol == "+":
                counters[cfg.name][0] += 1  # better
            elif symbol == "≈":
                counters[cfg.name][1] += 1  # similar
            else:  # "-"
                counters[cfg.name][2] += 1  # worse
            
            # 格式化为 "值±标准差 (符号)"
            row[cfg.name] = f"{cfg_text} ({symbol})"
        
        rows.append(row)
    
    print(f"  完成 {len(func_ids)} 个函数的比较")
    print()
    
    # 添加汇总行
    summary: Dict[str, str] = {"Function": "better/similar/worse"}
    summary[baseline_name] = ""
    
    print("统计汇总:")
    print(f"  与基准 ({baseline_name}) 比较:")
    for cfg in CONFIGS[1:]:
        wins, ties, losses = counters[cfg.name]
        summary[cfg.name] = f"{wins}/{ties}/{losses}"
        print(f"    {cfg.name}: +{wins} / ≈{ties} / -{losses}")
    
    rows.append(summary)
    
    # 创建DataFrame
    columns = ["Function"] + [cfg.name for cfg in CONFIGS]
    dataframe = pd.DataFrame(rows, columns=columns)
    
    return dataframe


def main() -> None:
    """主函数"""
    try:
        # 生成比较表
        df = evaluate_configs()
        
        # 保存Excel
        print()
        print("保存Excel文件...")
        df.to_excel(OUTPUT_FILE, index=False, engine='openpyxl')
        
        print()
        print("=" * 80)
        print(f"✅ Excel报告已生成: {OUTPUT_FILE}")
        print("=" * 80)
        print()
        
        # 显示预览
        print("表格预览:")
        print(df.to_string(index=False))
        print()
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()
