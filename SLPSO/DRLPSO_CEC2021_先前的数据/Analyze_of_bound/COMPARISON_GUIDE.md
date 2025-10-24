# 参数敏感性分析工具对比 - Lowerbound vs Upperbound

## 📁 目录结构

```
Analyze_of_bound/
├── changing_lowerbound/        # 下界分析
│   ├── generate_comparison_excel.py
│   ├── comparison_results_lowerbound.xlsx
│   └── 5/, 10/, 20/, 30/, 50/, 60/
│
└── changing_upperbound/        # 上界分析
    ├── generate_comparison_excel.py
    ├── comparison_results_upperbound.xlsx
    └── 60/, 70/, 100/, 130/, 160/, 200/
```

## 🔄 两个脚本的对应关系

| 特性 | changing_lowerbound | changing_upperbound |
|------|---------------------|---------------------|
| **参数类型** | 缓冲区下界 (batch_size_min) | 缓冲区上界 (batch_size_max) |
| **参数值** | 5, 10, 20, 30, 50, 60 | 60, 70, 100, 130, 160, 200 |
| **基准参数** | Lower=5 | Upper=60 |
| **输出文件** | comparison_results_lowerbound.xlsx | comparison_results_upperbound.xlsx |
| **文件名模式** | `*_30_10total_DRLPSO.txt` | `*_30_10total_DRLPSO.txt` |
| **测试函数** | F1-F10 | F1-F10 |
| **运行次数** | 30次/配置 | 30次/配置 |

## 📊 分析结果对比

### Changing Lowerbound (下界)

**基准**: Lower=5

| 配置 | +/≈/- | 排名 |
|------|-------|------|
| Lower=5 (基准) | - | 2.70 ⭐ |
| Lower=10 | 0/10/0 | 3.40 |
| Lower=20 | 0/10/0 | 3.20 |
| Lower=30 | 0/10/0 | 3.80 |
| Lower=50 | 0/10/0 | 3.50 |
| Lower=60 | 0/10/0 | 4.40 |

**结论**: Lower=5 整体表现最优

### Changing Upperbound (上界)

**基准**: Upper=60

| 配置 | +/≈/- |
|------|-------|
| Upper=60 (基准) | - |
| Upper=70 | 0/10/0 |
| Upper=100 | 0/10/0 |
| Upper=130 | 0/10/0 |
| Upper=160 | 0/10/0 |
| Upper=200 | 1/9/0 |

**结论**: 上界参数影响较小，60-200范围内性能相近

## 🎯 核心发现

### 参数敏感性

1. **下界敏感度**: 中等
   - Lower=5 表现最优
   - 随着下界增大，性能略有下降
   - 但统计检验未显示显著差异(可能因标准差极小)

2. **上界敏感度**: 低
   - 60-200范围内几乎无差异
   - 仅Upper=200在F10上略差
   - 表明上界对算法鲁棒性影响小

### 推荐配置

基于分析结果，推荐参数配置：
- **batch_size_min (下界)**: 5-10
- **batch_size_max (上界)**: 60-160

## 🔧 使用方法

### Lowerbound分析

```bash
cd changing_lowerbound
python generate_comparison_excel.py
```

### Upperbound分析

```bash
cd changing_upperbound
python generate_comparison_excel.py
```

## 📝 Excel表格格式

两个脚本生成相同格式的表格：

```
| Function | 基准配置 | 配置2 (符号) | 配置3 (符号) | ... |
|----------|---------|-------------|-------------|-----|
| F1       | xxx±xxx | xxx±xxx (≈) | xxx±xxx (+) | ... |
| F2       | xxx±xxx | xxx±xxx (-) | xxx±xxx (≈) | ... |
| ...      | ...     | ...         | ...         | ... |
| better/similar/worse | | X/Y/Z | X/Y/Z | ... |
```

### 符号说明
- **`+`**: 基准显著更优
- **`≈`**: 无显著差异
- **`-`**: 该配置显著更优

## 🔬 统计方法

两个脚本使用相同的统计方法：

- **检验**: Wilcoxon符号秩检验
- **显著性**: α = 0.05
- **样本**: 30次独立运行
- **度量**: 均值 ± 标准差(科学计数法)

## 📦 依赖库

两个脚本共享相同的依赖：

```bash
pip install numpy pandas scipy openpyxl
```

## 🆚 与MATLAB脚本的区别

### 相似之处
✅ 相同的Wilcoxon检验  
✅ 相同的显著性符号  
✅ 相同的Excel输出格式  
✅ 相同的汇总统计方式  

### Python版本的优势
✨ 更清晰的代码结构  
✨ 详细的中文注释  
✨ 更好的错误处理  
✨ 进度显示  
✨ 自动化程度更高  
✨ 易于扩展和修改  

## 📈 进一步分析

如需更深入的分析，可使用 `changing_lowerbound` 下的完整工具集：

1. **`analyze_lowerbound.py`**
   - 参数排名分析
   - 最优配置识别
   - 4种统计表格

2. **`visualize_results.py`**
   - 箱线图
   - 热图
   - 参数敏感性曲线
   - 性能剖面图
   - 等6种可视化

## 🎓 论文撰写建议

### 表格呈现
- 使用生成的Excel表格作为主表
- 在论文中突出显著性符号
- 添加汇总行的统计解读

### 图表补充
- 使用箱线图展示分布
- 使用参数曲线展示趋势
- 使用热图进行整体对比

### 文字描述
- 说明Wilcoxon检验方法
- 解释显著性水平(α=0.05)
- 讨论参数敏感性程度

## ⚠️ 注意事项

1. **数据完整性**: 确保每个参数文件夹都有10个函数的数据
2. **文件格式**: 文件名必须符合 `*_30_10total_DRLPSO.txt` 格式
3. **运行次数**: 每个文件必须包含30次运行结果
4. **基准选择**: 第一个配置自动作为基准列

## 🔄 自定义配置

### 修改参数列表

在脚本中找到 `CONFIGS` 定义：

```python
CONFIGS: List[Config] = [
    Config("参数名", BASE_DIR / "文件夹名"),
    # 第一个自动作为基准
    # 添加更多配置...
]
```

### 修改文件名模式

```python
FILENAME_PATTERN = re.compile(r"^(\d+)_30_10total_DRLPSO\.txt$")
# 修改为其他维度: _30_20 (20维)
```

## 📧 技术支持

如有问题，请检查：
1. Python版本 ≥ 3.7
2. 所有依赖库已安装
3. 数据文件路径正确
4. 文件格式符合要求

## 📚 相关文档

- `changing_lowerbound/README.md` - 下界分析详细说明
- `changing_upperbound/README.md` - 上界分析详细说明
- `changing_lowerbound/VERIFICATION_REPORT.md` - 验证报告

---

**最后更新**: 2025-10-23  
**版本**: 1.0  
**状态**: ✅ 已验证可用
