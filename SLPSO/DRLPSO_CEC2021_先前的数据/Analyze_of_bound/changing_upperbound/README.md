# 参数敏感性分析工具 - 上界配置

## 概述

本脚本用于分析DRLPSO算法中缓冲区(batch)上界参数对性能的影响，生成与MATLAB `significant_analysis.m` 相同格式的Excel比较表格。

## 文件说明

- **`generate_comparison_excel.py`** - Python分析脚本
- **`significant_analysis.m`** - 原MATLAB脚本(参考)
- **`comparison_results_upperbound.xlsx`** - 生成的Excel报告

## 参数配置

当前分析的上界参数值：
- Upper=60 (基准)
- Upper=70
- Upper=100
- Upper=130
- Upper=160
- Upper=200

## 使用方法

### 前置要求

确保已安装所需Python库：

```bash
pip install numpy pandas scipy openpyxl
```

### 运行脚本

```bash
cd changing_upperbound
python generate_comparison_excel.py
```

### 输出文件

生成的Excel文件格式：

```
| Function | Upper=60 (基准) | Upper=70 (符号) | Upper=100 (符号) | ... |
|----------|----------------|----------------|-----------------|-----|
| F1       | 3.39E-220±0.00E+00 | 3.41E-219±0.00E+00 (≈) | ... |
| F2       | 7.19E+01±8.78E+01  | 8.05E+01±1.10E+02 (≈)  | ... |
| ...      | ...            | ...            | ...             | ... |
| better/similar/worse |  | 0/10/0 | 0/10/0 | ... |
```

## Excel表格说明

### 列结构
1. **Function列** - 测试函数编号(F1-F10)
2. **第一列(基准)** - 基准参数的统计数据(均值±标准差)
3. **其他列** - 其他参数配置的数据 + 显著性符号

### 显著性符号
- **`+`** - 基准参数显著优于该配置 (p < 0.05, 且基准均值更小)
- **`-`** - 该配置显著优于基准参数 (p < 0.05, 且该配置均值更小)
- **`≈`** - 两者无显著差异 (p ≥ 0.05)

### 汇总行
最后一行 `better/similar/worse` 格式为 `X/Y/Z`:
- **X** - 基准更好的函数数量 (+)
- **Y** - 无显著差异的函数数量 (≈)
- **Z** - 该配置更好的函数数量 (-)

## 统计方法

- **检验方法**: Wilcoxon符号秩检验(非参数检验)
- **显著性水平**: α = 0.05
- **样本数**: 每个配置30次独立运行

## 分析结果

### 当前结果摘要

基准参数: Upper=60

| 配置 | +/≈/- | 说明 |
|------|-------|------|
| Upper=70 | 0/10/0 | 与基准无显著差异 |
| Upper=100 | 0/10/0 | 与基准无显著差异 |
| Upper=130 | 0/10/0 | 与基准无显著差异 |
| Upper=160 | 0/10/0 | 与基准无显著差异 |
| Upper=200 | 1/9/0 | 在F10上基准显著更优 |

**结论**: 上界参数在60-200范围内对算法性能影响较小，仅在Upper=200时F10函数性能略有下降。

## 自定义配置

### 修改参数值

在脚本中修改 `CONFIGS` 列表：

```python
CONFIGS: List[Config] = [
    Config("Upper=60", BASE_DIR / "60"),   # 第一个作为基准
    Config("Upper=70", BASE_DIR / "70"),
    # 添加或修改其他配置...
]
```

### 修改显著性水平

```python
ALPHA = 0.05  # 改为0.01或其他值
```

### 修改输出文件名

```python
OUTPUT_FILE = BASE_DIR / "comparison_results_upperbound.xlsx"
```

## 文件路径要求

脚本假设以下目录结构：

```
changing_upperbound/
├── generate_comparison_excel.py  # 本脚本
├── 60/                          # 参数文件夹
│   ├── 1_30_10total_DRLPSO.txt
│   ├── 2_30_10total_DRLPSO.txt
│   └── ...
├── 70/
├── 100/
└── ...
```

## 数据文件格式

每个 `*_30_10total_DRLPSO.txt` 文件应包含：

```
run1_result
run2_result
...
run30_result
average=xxx
std=xxx
best=xxx
```

## 与MATLAB脚本的对应关系

| MATLAB | Python | 说明 |
|--------|--------|------|
| `signrank()` | `scipy.stats.wilcoxon()` | Wilcoxon检验 |
| `mean()` | `numpy.mean()` | 均值计算 |
| `std()` | `numpy.std(ddof=1)` | 标准差(样本) |
| `writecell()` | `DataFrame.to_excel()` | Excel输出 |
| `sprintf('%.2E±%.2E')` | `f"{:.2E}±{:.2E}"` | 科学计数法格式化 |

## 常见问题

### Q1: 如何更换基准参数？
**A**: 将想要作为基准的配置放在 `CONFIGS` 列表的第一位。

### Q2: 为什么会有警告信息？
**A**: `RuntimeWarning: invalid value encountered in scalar divide` 是因为某些数据标准差为0，不影响结果。

### Q3: 如何解读 "≈" 符号？
**A**: 表示两组数据没有统计学上的显著差异(p ≥ 0.05)。

### Q4: 可以分析维度不同的数据吗？
**A**: 可以，只需修改 `FILENAME_PATTERN` 的正则表达式，例如改为 `_30_20` 用于20维数据。

## 扩展分析

如需更详细的分析(排名、可视化等)，请使用：
- `analyze_lowerbound.py` - 完整统计分析
- `visualize_results.py` - 生成6种可视化图表

## 版本信息

- **版本**: 1.0
- **日期**: 2025-10-23
- **Python版本**: 3.7+
- **依赖库**: numpy, pandas, scipy, openpyxl

## 许可证

本脚本用于学术研究，与DRLPSO项目保持一致的许可证。

---

**提示**: 首次运行前请确保数据文件完整且格式正确！
