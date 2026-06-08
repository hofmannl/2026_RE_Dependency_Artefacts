from pathlib import Path

def save_results_to_csv(file_path: Path, results: list[tuple[str, str]]) -> None:
    """Save classification results to a CSV file."""
    with open(file_path, "w", encoding="utf-8") as f:
        for dep in results:
            f.write(f"{dep[0]} -> {dep[1]}\n")