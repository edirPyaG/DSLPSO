from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Dataset:
    excel: Path
    caption: str
    label: str
    output: Path


DATASETS: tuple[Dataset, ...] = (
    Dataset(
        excel=ROOT / "数据分析" / "数据分析10D.xlsx",
        caption="Performance comparison on CEC2014 test problems (dimensions 1–10)",
        label="tab:cec2014-dim-1-10",
        output=ROOT / "table_10d.tex",
    ),
    Dataset(
        excel=ROOT / "数据分析" / "数据分析20D.xlsx",
        caption="Performance comparison on CEC2014 test problems (dimensions 10–20)",
        label="tab:cec2014-dim-10-20",
        output=ROOT / "table_20d.tex",
    ),
)

COLUMNS = ("Function", "SLPSO", "OLPSO", "MPSO","LEO",  "GLPSO","ALC-PSO")
ALIGN_SPEC = "l" + "c" * (len(COLUMNS) - 1)
HEADER_LINE = " & ".join(COLUMNS) + r" \\" 


def _format_cell(value: str | None, is_last_row: bool = False) -> str:
    if value is None:
        return ""
    text = value.strip()
    if not text or text.lower() == "nan":
        return ""
    
    # Handle summary row like "(+/≈/-)"
    if text.startswith("(") and text.endswith(")"):
        return rf"\textbf{{{text}}}" if is_last_row else text
    
    # Split value and suffix like "(+)", "(-)", "(≈)"
    parts = text.split(" ", 1)
    main = parts[0]
    suffix = parts[1] if len(parts) > 1 else ""
    
    # Format main value with \text{} and \pm
    if r"±" in main or "±" in main:
        main = main.replace("±", r"}\pm\text{")
        main = rf"$\text{{{main}}}$"
    else:
        main = rf"$\text{{{main}}}$"
    
    # Format suffix
    if suffix:
        suffix = suffix.replace("≈", r"\approx")
        if is_last_row:
            suffix = rf"\textbf{{{suffix}}}"
        else:
            suffix = rf"${suffix}$"
        return f"{main} {suffix}"
    
    if is_last_row and not text.startswith("("):
        return rf"\textbf{{{main}}}"
    
    return main


def _build_body(rows: list[tuple[str, ...]]) -> str:
    rendered: list[str] = []
    row_terminator = " " + ("\\" * 2)
    total_rows = len(rows)
    
    for idx, row in enumerate(rows):
        is_last = (idx == total_rows - 1)
        rendered.append(" & ".join(row) + row_terminator)
    
    return "\n".join(rendered)


def _generate_table(dataset: Dataset) -> None:
    df = pd.read_excel(dataset.excel, dtype=str)
    df = df.loc[:, COLUMNS].copy()
    df["Function"] = df["Function"].fillna("(+/≈/-)")
    df = df.fillna("")

    # Format each row with awareness of whether it's the last row
    formatted_rows = []
    total = len(df)
    for idx, record in enumerate(df.itertuples(index=False, name=None)):
        is_last = (idx == total - 1)
        formatted_rows.append(tuple(_format_cell(cell, is_last_row=is_last) for cell in record))
    
    body = _build_body(formatted_rows)

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


def main() -> None:
    for dataset in DATASETS:
        _generate_table(dataset)


if __name__ == "__main__":
    main()
