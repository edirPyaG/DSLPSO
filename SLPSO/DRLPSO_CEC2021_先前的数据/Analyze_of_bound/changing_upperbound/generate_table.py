from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import pandas as pd


ROOT = Path(__file__).resolve().parent


@dataclass(frozen=True)
class Dataset:
    excel: Path
    caption: str
    label: str
    output: Path


DATASETS: tuple[Dataset, ...] = (
    Dataset(
        excel=ROOT / "comparison_results_Upperbound.xlsx",
        caption="Performance comparison with different Upper bound values on CEC2021 test functions",
        label="tab:Upperbound-comparison",
        output=ROOT / "table_Upperbound.tex",
    ),
)

COLUMNS = ("Function", "Upper=60", "Upper=70", "Upper=100", "Upper=130", "Upper=160", "Upper=200")
BASELINE_COL = "Upper=60"  # 基准列名
ALIGN_SPEC = "l" + "c" * (len(COLUMNS) - 1)
HEADER_LINE = " & ".join(COLUMNS) + r" \\"


def _format_cell(value: str | None, is_baseline: bool = False) -> str:
    if value is None:
        return ""
    text = value.strip()
    if not text or text.Upper() == "nan":
        return ""
    
    # 移除可能的括号和符号
    has_symbol = False
    symbol = ""
    if "(+)" in text:
        text = text.replace(" (+)", "").replace("(+)", "")
        has_symbol = True
        symbol = " $(+)$"
    elif "(-)" in text:
        text = text.replace(" (-)", "").replace("(-)", "")
        has_symbol = True
        symbol = " $(-)$"
    elif r"(\approx)" in text or "(≈)" in text:
        text = text.replace(" (≈)", "").replace("(≈)", "").replace(r" (\approx)", "").replace(r"(\approx)", "")
        has_symbol = True
        symbol = r" $(\approx)$"
    
    # 基准列不应该有符号
    if is_baseline:
        symbol = ""
    
    # 将科学记数法和符号包装在 \text{} 中
    text = text.replace("±", r"}\pm\text{")
    
    # 包装为LaTeX格式
    result = r"$\text{" + text + r"}$" + symbol
    return result


def _build_body(rows: Iterable[tuple[str, ...]]) -> str:
    rendered: list[str] = []
    for i, row in enumerate(rows):
        formatted_cells = []
        for j, cell in enumerate(row):
            if j == 0:  # Function 列
                # 检查是否是汇总行
                if "better/similar/worse" in cell or "(+/≈/-)" in cell or "+/" in cell:
                    formatted_cells.append(r"\textbf{(+/≈/-)}")
                else:
                    formatted_cells.append(f"$\\text{{{cell}}}$")
            elif j == 1:  # 基准列（第二列）
                # 检查是否是汇总行的统计数据
                if "/" in cell and "E" not in cell and cell.strip():
                    formatted_cells.append("")  # 基准列的汇总为空
                else:
                    formatted_cells.append(_format_cell(cell, is_baseline=True))
            else:  # 其他比较列
                # 检查是否是汇总行的统计数据
                if "/" in cell and "E" not in cell and cell.strip():
                    formatted_cells.append(f"\\textbf{{$\\text{{{cell}}}$}}")
                else:
                    formatted_cells.append(_format_cell(cell, is_baseline=False))
        rendered.append(" & ".join(formatted_cells) + r" \\")
    return "\n".join(rendered)


def _generate_table(dataset: Dataset) -> None:
    df = pd.read_excel(dataset.excel, dtype=str)
    
    # 按照COLUMNS指定的顺序重新排列列
    df = df[list(COLUMNS)].copy()
    df[COLUMNS[0]] = df[COLUMNS[0]].fillna("(+/≈/-)")
    df = df.fillna("")

    # 构建表格主体
    rows_tex = []
    for idx, row in df.iterrows():
        cells_tex = []
        for col_idx, col_name in enumerate(COLUMNS):
            cell_value = row[col_name].strip()
            
            if col_idx == 0:  # Function 列
                if "better/similar/worse" in cell_value or "(+/≈/-)" in cell_value:
                    cells_tex.append(r"\textbf{(+/≈/-)}")
                else:
                    cells_tex.append(f"$\\text{{{cell_value}}}$")
            elif col_name == BASELINE_COL:  # 基准列 (Upper=10)
                # 检查是否是汇总行
                if "/" in cell_value and "E" not in cell_value:
                    cells_tex.append("")  # 基准列的汇总为空
                elif not cell_value:  # 空值
                    cells_tex.append("")
                else:
                    # 移除任何符号
                    clean_value = cell_value.replace(" (+)", "").replace(" (-)", "").replace(" (≈)", "")
                    clean_value = clean_value.replace("(+)", "").replace("(-)", "").replace("(≈)", "")
                    clean_value = clean_value.replace("±", r"}\pm\text{")
                    cells_tex.append(f"$\\text{{{clean_value}}}$")
            else:  # 其他比较列
                # 检查是否是汇总行
                if "/" in cell_value and "E" not in cell_value:
                    if cell_value.strip():  # 有内容
                        cells_tex.append(f"\\textbf{{$\\text{{{cell_value}}}$}}")
                    else:  # 空值
                        cells_tex.append("")
                elif not cell_value:  # 空值
                    cells_tex.append("")
                else:
                    # 提取符号
                    symbol = ""
                    if " (+)" in cell_value:
                        symbol = " $(+)$"
                        cell_value = cell_value.replace(" (+)", "")
                    elif " (-)" in cell_value:
                        symbol = " $(-)$"
                        cell_value = cell_value.replace(" (-)", "")
                    elif " (≈)" in cell_value:
                        symbol = r" $(\approx)$"
                        cell_value = cell_value.replace(" (≈)", "")
                    
                    # 格式化数值
                    cell_value = cell_value.replace("±", r"}\pm\text{")
                    cells_tex.append(f"$\\text{{{cell_value}}}${symbol}")
        
        rows_tex.append(" & ".join(cells_tex) + r" \\")
    
    body = "\n".join(rows_tex)

    table_tex = rf"""\begin{{table*}}[htbp]
\centering
\caption{{{dataset.caption}}}
\label{{{dataset.label}}}
\begingroup
\scriptsize
\setlength{{\tabcolsep}}{{2pt}}
\renewcommand{{\arraystretch}}{{1.05}}
\begin{{tabular}}{{{ALIGN_SPEC}}}
\toprule
{HEADER_LINE}
\midrule
{body}
\bottomrule
\end{{tabular}}
\endgroup
\end{{table*}}
"""

    dataset.output.write_text(table_tex, encoding="utf-8")
    print(f"✅ LaTeX表格已生成: {dataset.output}")


def main() -> None:
    for dataset in DATASETS:
        _generate_table(dataset)


if __name__ == "__main__":
    main()
