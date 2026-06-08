from __future__ import annotations

from pathlib import Path

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    fbeta_score,
    confusion_matrix,
)


def load_inclusion_dependencies(file_path: str) -> set[tuple[str, str]]:
    """
    Load inclusion dependencies from file with format: user_story1 -> user_story2

    Returns set of tuples: (user_story1, user_story2)
    Skips empty lines and handles whitespace.
    """
    dependencies: set[tuple[str, str]] = set()
    file_path = str(file_path)

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or "->" not in line:
                continue
            
            parts = line.split("->")
            if len(parts) != 2:
                continue
            
            us1 = parts[0].strip()
            us2 = parts[1].strip()
            
            if us1 and us2:
                dependencies.add((us1, us2))

    return dependencies


def compute_metrics(y_true: list[bool], y_pred: list[bool]) -> dict:
    """Compute evaluation metrics from true and predicted labels."""
    cm = confusion_matrix(y_true, y_pred, labels=[False, True])
    tn, fp, fn, tp = cm.ravel()
    return {
        "accuracy": accuracy_score(y_true, y_pred),
        "precision": precision_score(y_true, y_pred, zero_division=0),
        "recall": recall_score(y_true, y_pred, zero_division=0),
        "f1": f1_score(y_true, y_pred, zero_division=0),
        "f2": fbeta_score(y_true, y_pred, beta=2, zero_division=0),
        "confusion_matrix": cm,
        "tp": int(tp),
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
    }


def print_results(metrics: dict) -> None:
    """Print evaluation results to console."""
    print("=" * 50)
    print("INCLUSION DEPENDENCIES EVALUATION RESULTS")
    print("=" * 50)
    print(f"Accuracy:  {metrics['accuracy']:.4f}")
    print(f"Precision: {metrics['precision']:.4f}")
    print(f"Recall:    {metrics['recall']:.4f}")
    print(f"F1-Score:  {metrics['f1']:.4f}")
    print(f"F2-Score:  {metrics['f2']:.4f}")
    print(f"TP: {metrics['tp']}  FP: {metrics['fp']}  FN: {metrics['fn']}  TN: {metrics['tn']}")
    print("\nConfusion Matrix (labels=[False, True]):")
    print(metrics["confusion_matrix"])
    print("=" * 50)


def main() -> None:
    print("=" * 50)
    print("DEPENDENCIES EVALUATION TOOL")
    print("MULTIPLE DATASETS")
    print("=" * 50)

    file_pairs: list[tuple[str, str]] = []
    pair_num = 1

    print("\nEnter ground truth and prediction file pairs:")
    print("(Enter ground truth file, then prediction file for each pair, press Enter twice to finish)\n")

    while True:
        gt_path = input(f"Pair {pair_num} - Enter ground truth file path (or press Enter to finish): ").strip()
        if not gt_path:
            if file_pairs:
                break
            print("Please enter at least one pair of files.")
            continue

        pred_path = input(f"Pair {pair_num} - Enter prediction file path: ").strip()
        if not pred_path:
            print("Please enter a prediction file path.")
            continue

        file_pairs.append((gt_path, pred_path))
        pair_num += 1
        print()

    all_y_true: list[bool] = []
    all_y_pred: list[bool] = []

    processed_pairs = 0
    skipped_pairs = 0

    total_gt_deps = 0
    total_pred_deps = 0
    total_missed_deps = 0
    total_extra_deps = 0

    results_per_pair: list[dict] = []

    for i, (gt_path, pred_path) in enumerate(file_pairs, start=1):
        gt_path_p = Path(gt_path)
        pred_path_p = Path(pred_path)

        if not gt_path_p.exists():
            print(f"Warning: Ground truth file does not exist (pair {i}): {gt_path_p}")
            skipped_pairs += 1
            continue
        if not pred_path_p.exists():
            print(f"Warning: Prediction file does not exist (pair {i}): {pred_path_p}")
            skipped_pairs += 1
            continue

        gt_deps = load_inclusion_dependencies(str(gt_path_p))
        pred_deps = load_inclusion_dependencies(str(pred_path_p))
        identifier = pred_path_p.stem

        gt_set = gt_deps
        pred_set = pred_deps
        common_deps = gt_set & pred_set

        missed_deps = gt_set - pred_set
        extra_deps = pred_set - gt_set

        total_gt_deps += len(gt_set)
        total_pred_deps += len(pred_set)
        total_missed_deps += len(missed_deps)
        total_extra_deps += len(extra_deps)

        if not common_deps and not missed_deps and not extra_deps:
            print(f"Warning: No dependencies found in {identifier} (pair {i})")
            skipped_pairs += 1
            continue

        # Create binary labels for all possible pairs we've seen
        all_possible_pairs = gt_set | pred_set
        
        if not all_possible_pairs:
            print(f"Warning: No dependencies to evaluate in {identifier} (pair {i})")
            skipped_pairs += 1
            continue

        y_true = [1 if pair in gt_set else 0 for pair in sorted(all_possible_pairs)]
        y_pred = [1 if pair in pred_set else 0 for pair in sorted(all_possible_pairs)]

        all_y_true.extend(y_true)
        all_y_pred.extend(y_pred)

        processed_pairs += 1
        per_metrics = compute_metrics(y_true, y_pred)
        results_per_pair.append({
            "identifier": identifier,
            "gt_count": len(gt_set),
            "pred_count": len(pred_set),
            "common": len(common_deps),
            "missed": len(missed_deps),
            "extra": len(extra_deps),
            "metrics": per_metrics,
        })

        print(f"Processed pair {i}: {identifier}")
        print(f"  GT dependencies:       {len(gt_set)}")
        print(f"  Pred dependencies:     {len(pred_set)}")
        print(f"  Matched:               {len(common_deps)}")
        print(f"  Missed (GT-only):      {len(missed_deps)}")
        print(f"  Extra (Pred-only):     {len(extra_deps)}")
        print(f"  Matched-sample TP/FP/FN/TN: {per_metrics['tp']}/{per_metrics['fp']}/{per_metrics['fn']}/{per_metrics['tn']}\n")

    if not all_y_true:
        raise ValueError("No dependencies found across all file pairs. Cannot compute metrics.")

    metrics = compute_metrics(all_y_true, all_y_pred)

    print()
    print_results(metrics)
    print(f"Total File Pairs Entered: {len(file_pairs)}")
    print(f"Pairs Processed:         {processed_pairs}")
    print(f"Pairs Skipped:           {skipped_pairs}")
    print(f"Total Evaluated Pairs:   {len(all_y_true)}\n")

    print("Coverage across datasets:")
    print(f"  Total GT dependencies:        {total_gt_deps}")
    print(f"  Total Pred dependencies:      {total_pred_deps}")
    print(f"  Total Missed dependencies:    {total_missed_deps}  (in GT, not in Pred)")
    print(f"  Total Extra dependencies:     {total_extra_deps}   (in Pred, not in GT)\n")

    # Save results
    output_path = Path(__file__).parent / "dependencies_evaluation_results.txt"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("=" * 50 + "\n")
        f.write("DEPENDENCIES EVALUATION RESULTS\n")
        f.write("MULTIPLE DATASETS\n")
        f.write("=" * 50 + "\n\n")

        f.write(f"Total File Pairs Entered: {len(file_pairs)}\n")
        f.write(f"Pairs Processed:         {processed_pairs}\n")
        f.write(f"Pairs Skipped:           {skipped_pairs}\n")
        f.write(f"Total Evaluated Pairs:   {len(all_y_true)}\n\n")

        f.write("Per-dataset Results:\n")
        f.write("-" * 50 + "\n")
        for result in results_per_pair:
            f.write(f"\nDataset: {result['identifier']}\n")
            f.write(f"  GT dependencies:       {result['gt_count']}\n")
            f.write(f"  Pred dependencies:     {result['pred_count']}\n")
            f.write(f"  Matched:               {result['common']}\n")
            f.write(f"  Missed (GT-only):      {result['missed']}\n")
            f.write(f"  Extra (Pred-only):     {result['extra']}\n")
            m = result['metrics']
            f.write(f"  TP/FP/FN/TN: {m['tp']}/{m['fp']}/{m['fn']}/{m['tn']}\n")

        f.write("\n" + "=" * 50 + "\n")
        f.write("OVERALL RESULTS\n")
        f.write("=" * 50 + "\n\n")

        f.write("Coverage across datasets:\n")
        f.write(f"  Total GT dependencies:        {total_gt_deps}\n")
        f.write(f"  Total Pred dependencies:      {total_pred_deps}\n")
        f.write(f"  Total Missed dependencies:    {total_missed_deps}\n")
        f.write(f"  Total Extra dependencies:     {total_extra_deps}\n\n")

        f.write(f"Accuracy:  {metrics['accuracy']:.4f}\n")
        f.write(f"Precision: {metrics['precision']:.4f}\n")
        f.write(f"Recall:    {metrics['recall']:.4f}\n")
        f.write(f"F1-Score:  {metrics['f1']:.4f}\n")
        f.write(f"F2-Score:  {metrics['f2']:.4f}\n")
        f.write(f"TP: {metrics['tp']}  FP: {metrics['fp']}  FN: {metrics['fn']}  TN: {metrics['tn']}\n")
        f.write("\nConfusion Matrix (labels=[False, True]):\n")
        f.write(str(metrics["confusion_matrix"]) + "\n")

    print(f"Results saved to: {output_path}")


if __name__ == "__main__":
    main()
