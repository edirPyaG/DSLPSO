# 缓冲区下界参数敏感性分析工具

## 概述

本工具用于分析DRLPSO算法中缓冲区(batch)下界参数对性能的影响。通过统计分析和可视化,帮助确定最优参数配置。

## 文件说明

### 1. `analyze_lowerbound.py` - 数据统计分析脚本

**功能:**
- 读取所有参数配置下的实验数据
- 执行Wilcoxon符号秩检验
- 计算平均排名
- 生成多种统计表格

**输出文件:**
- `performance_comparison.xlsx` - 性能对比表(所有参数配置)
- `statistical_comparison_baseline{X}.xlsx` - 统计检验结果(与基准参数X比较)
- `parameter_rankings.xlsx` - 参数排名表
- `best_parameter_configs.xlsx` - 每个函数的最优参数配置

**使用方法:**
```bash
python analyze_lowerbound.py
```

### 2. `visualize_results.py` - 数据可视化脚本

**功能:**
- 生成6种可视化图表
- 多角度展示参数敏感性

**输出图表:**
1. `boxplot_by_function.png` - 箱线图(按函数分组)
2. `heatmap_performance.png` - 性能热图
3. `parameter_sensitivity_curves.png` - 参数敏感性曲线
4. `average_ranking_bar.png` - 平均排名柱状图
5. `performance_profile.png` - 性能剖面图
6. `violin_plot_comparison.png` - 小提琴图(选定函数)

**使用方法:**
```bash
python visualize_results.py
```

## 参数说明

### 当前分析的参数值
- **下界值:** 5, 10, 20, 30, 50, 60
- **测试函数:** CEC2021 F1-F10
- **维度:** 10维
- **独立运行次数:** 30次

### 修改基准参数

在 `analyze_lowerbound.py` 的 `main()` 函数中修改:
```python
baseline_param = 10  # 修改为其他值如 5, 20, 30等
```

## 环境要求

### Python版本
- Python 3.7+

### 依赖库
```bash
pip install numpy pandas scipy openpyxl matplotlib seaborn
```

或使用requirements.txt:
```bash
pip install -r requirements.txt
```

## 输出结果解读

### 统计检验符号说明
- `+` : 基准参数显著优于比较参数 (p < 0.05)
- `-` : 比较参数显著优于基准参数 (p < 0.05)
- `≈` : 两者无显著差异 (p ≥ 0.05)

### 汇总统计格式
`X/Y/Z` 表示:
- X: 基准参数更好的函数数量 (+)
- Y: 无显著差异的函数数量 (≈)
- Z: 比较参数更好的函数数量 (-)

### 排名解释
- 排名越小表示性能越好
- 平均排名综合了在所有测试函数上的表现

## 数据文件格式

### 输入文件格式
每个参数配置文件夹下应包含:
```
{FuncNum}_30_10total_DRLPSO.txt
```

文件内容格式:
```
run1_result
run2_result
...
run30_result
average={avg_value}
std={std_value}
best={best_value}
```

## 示例工作流程

1. **运行统计分析**
   ```bash
   python analyze_lowerbound.py
   ```
   - 查看控制台输出的汇总统计
   - 打开生成的Excel文件查看详细结果

2. **生成可视化图表**
   ```bash
   python visualize_results.py
   ```
   - 查看生成的PNG图片
   - 用于论文或报告

3. **结果分析**
   - 检查`parameter_rankings.xlsx`确定总体最优参数
   - 查看`best_parameter_configs.xlsx`了解各函数的最优配置
   - 使用热图和曲线图观察参数变化趋势
   - 参考性能剖面图进行算法比较

## 扩展功能

### 修改参数值列表

在两个脚本的 `main()` 函数中修改:
```python
param_values = [5, 10, 20, 30, 50, 60]  # 添加或删除参数值
```

### 修改选定函数(小提琴图)

在 `visualize_results.py` 中修改:
```python
plot_violin_comparison(all_results, param_values, output_folder, 
                      selected_funcs=[1, 2, 5])  # 修改函数编号
```

### 调整图表样式

修改 `visualize_results.py` 中的:
- `figsize` - 图表大小
- `dpi` - 分辨率
- 颜色方案
- 字体大小

## 常见问题

### Q1: 提示找不到文件
**A:** 检查 `base_folder` 路径是否正确,确保数据文件存在

### Q2: 中文显示乱码
**A:** 安装中文字体,或修改 `plt.rcParams['font.sans-serif']`

### Q3: 内存不足
**A:** 减少同时处理的参数数量,或分批处理

### Q4: 统计检验失败
**A:** 检查数据是否完整(需要30个样本),确保数值有效

## 引用格式

如果使用本工具进行分析,请引用:
```
DRLPSO参数敏感性分析工具 v1.0
用于CEC2021基准测试函数的参数优化分析
```

## 版本历史

- v1.0 (2025-10-23): 初始版本
  - 实现基本统计分析功能
  - 实现6种可视化图表
  - 支持Wilcoxon检验和排名分析

## 联系方式

如有问题或建议,请联系项目维护者。

---

**注意:** 运行脚本前请确保数据文件完整且格式正确!
