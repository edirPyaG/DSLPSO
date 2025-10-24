"""Generate a comparison Excel report for lower-bound settings.

The output mimics the layout produced by significant_analysis.m:
Function column, baseline statistics, then other configurations with
Wilcoxon significance markers.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from scipy.stats import wilcoxon


@dataclass
class Config:
    name: str
    folder: Path


# Configuration for the analysis. The first entry acts as the baseline column.
BASE_DIR = Path(__file__).resolve().parent
CONFIGS: List[Config] = [
    Config("Lower=5", BASE_DIR / "5"),
    Config("Lower=10", BASE_DIR / "10"),
    Config("Lower=20", BASE_DIR / "20"),
    Config("Lower=30", BASE_DIR / "30"),
    Config("Lower=50", BASE_DIR / "50"),
    Config("Lower=60", BASE_DIR / "60"),
]
RUNS_PER_FILE = 30
FILENAME_PATTERN = re.compile(r"^(\d+)_30_10total_DRLPSO\.txt$")
OUTPUT_FILE = BASE_DIR / "comparison_results_lowerbound.xlsx"
ALPHA = 0.05


def discover_files(config: Config) -> Dict[int, Path]:
    """Return mapping function id -> file path for a configuration."""
    files: Dict[int, Path] = {}
    if not config.folder.exists():
        raise FileNotFoundError(f"Folder not found: {config.folder}")
    for path in config.folder.glob("*_30_10total_DRLPSO.txt"):
        match = FILENAME_PATTERN.match(path.name)
        if match:
            func_id = int(match.group(1))
            files[func_id] = path
    if not files:
        raise FileNotFoundError(f"No matching files in {config.folder}")
    return dict(sorted(files.items()))


def read_runs(path: Path) -> np.ndarray:
    """Read the first RUNS_PER_FILE floating-point values from a file."""
    values: List[float] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            text = line.strip()
            if not text:
                continue
            if "=" in text:
                break
            try:
                values.append(float(text))
            except ValueError:
                continue
            if len(values) == RUNS_PER_FILE:
                break
    if len(values) != RUNS_PER_FILE:
        raise ValueError(f"Expected {RUNS_PER_FILE} values in {path}")
    return np.asarray(values, dtype=float)


def format_stats(data: np.ndarray) -> Tuple[str, float, float]:
    mean_val = float(np.mean(data))
    std_val = float(np.std(data, ddof=1))
    formatted = f"{mean_val:.2E}±{std_val:.2E}"
    return formatted, mean_val, std_val


def evaluate_configs() -> pd.DataFrame:
    # Preload data for every configuration and function.
    data_store: Dict[str, Dict[int, np.ndarray]] = {}
    stats_store: Dict[str, Dict[int, Tuple[str, float, float]]] = {}

    for config in CONFIGS:
        files = discover_files(config)
        data_store[config.name] = {}
        stats_store[config.name] = {}
        for func_id, path in files.items():
            runs = read_runs(path)
            data_store[config.name][func_id] = runs
            stats_store[config.name][func_id] = format_stats(runs)

    baseline_name = CONFIGS[0].name
    func_ids = sorted(data_store[baseline_name].keys())

    rows: List[Dict[str, str]] = []
    counters: Dict[str, List[int]] = {cfg.name: [0, 0, 0] for cfg in CONFIGS[1:]}

    for func_id in func_ids:
        row: Dict[str, str] = {"Function": f"F{func_id}"}
        baseline_text, baseline_mean, _ = stats_store[baseline_name][func_id]
        row[baseline_name] = baseline_text

        baseline_runs = data_store[baseline_name][func_id]

        for cfg in CONFIGS[1:]:
            cfg_stats = stats_store[cfg.name].get(func_id)
            if cfg_stats is None:
                row[cfg.name] = "N/A"
                continue
            cfg_text, cfg_mean, _ = cfg_stats
            compare_runs = data_store[cfg.name][func_id]

            try:
                _, p_value = wilcoxon(
                    baseline_runs,
                    compare_runs,
                    zero_method="pratt",
                    alternative="two-sided",
                    mode="approx",
                )
            except ValueError:
                p_value = math.nan

            if math.isnan(p_value) or p_value >= ALPHA:
                symbol = "≈"
                counters[cfg.name][1] += 1
            else:
                if baseline_mean < cfg_mean:
                    symbol = "+"
                    counters[cfg.name][0] += 1
                else:
                    symbol = "-"
                    counters[cfg.name][2] += 1

            row[cfg.name] = f"{cfg_text} ({symbol})"

        rows.append(row)

    summary: Dict[str, str] = {"Function": "better/similar/worse"}
    summary[baseline_name] = ""
    for cfg in CONFIGS[1:]:
        wins, ties, losses = counters[cfg.name]
        summary[cfg.name] = f"{wins}/{ties}/{losses}"

    rows.append(summary)
    columns = ["Function"] + [cfg.name for cfg in CONFIGS]
    dataframe = pd.DataFrame(rows, columns=columns)
    return dataframe


def main() -> None:
    df = evaluate_configs()
    df.to_excel(OUTPUT_FILE, index=False)
    print(f"Excel report written to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
