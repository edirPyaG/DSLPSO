@echo off
REM 参数敏感性分析 - 一键运行脚本
echo ========================================
echo  缓冲区下界参数敏感性分析工具
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未检测到Python,请先安装Python 3.7+
    pause
    exit /b 1
)

echo [1/4] 检查依赖库...
python -c "import numpy, pandas, scipy, matplotlib, seaborn" >nul 2>&1
if %errorlevel% neq 0 (
    echo 缺少依赖库,正在安装...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo 安装失败,请手动运行: pip install -r requirements.txt
        pause
        exit /b 1
    )
)
echo 依赖库检查完成!
echo.

echo [2/4] 运行统计分析...
python analyze_lowerbound.py
if %errorlevel% neq 0 (
    echo 统计分析出错!
    pause
    exit /b 1
)
echo 统计分析完成!
echo.

echo [3/4] 生成可视化图表...
python visualize_results.py
if %errorlevel% neq 0 (
    echo 可视化生成出错!
    pause
    exit /b 1
)
echo 可视化完成!
echo.

echo [4/4] 打开结果文件夹...
start .

echo.
echo ========================================
echo  分析完成!
echo  - Excel表格: performance_comparison.xlsx等
echo  - 图表: *.png
echo ========================================
echo.
pause
