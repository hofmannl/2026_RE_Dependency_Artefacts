from __future__ import annotations

from pathlib import Path
import csv
from typing import Optional

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    fbeta_score,
    confusion_matrix,
)

TRUTHY = {"true", "1", "yes", "y", "t"}
FALSY = {"false", "0", "no", "n", "f"}


def parse_bool(label: str) -> Optional[bool]:
    """Parse a boolean label. Returns None if unparsable."""
    v = (label or "").strip().lower()
    if v in TRUTHY:
        return True
    if v in FALSY:
        return False
    return None


def load_csv(file_path: str, separator: str = "|", skip_header: bool = True) -> list[dict]:
    """
    Load data from file with format: word1<sep>word2<sep>true/false

    Returns list of dicts:
      { 'word1': str, 'word2': str, 'prediction': bool }
    Skips rows with unparsable labels or wrong column count.
    """
    rows: list[dict] = []
    file_path = str(file_path)

    with open(file_path, "r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f, delimiter=separator)
        for idx, parts in enumerate(reader):
            if idx == 0 and skip_header:
                continue
            if not parts or all(not p.strip().lower() for p in parts):
                continue
            if len(parts) not in (3, 4):  # allow optional 4th column for comments, but ignore it
                continue
            
            if len(parts) == 4:
                parts = parts[:3]  # ignore extra columns
            word1, word2, label = parts
            word1 = word1.strip().lower()
            word2 = word2.strip().lower()
            b = parse_bool(label)
            if b is None:
                continue

            rows.append({"word1": word1, "word2": word2, "prediction": b})

    return rows


def load_predictions(file_path: str, separator: str = "|", skip_header: bool = True) -> list[dict]:
    return load_csv(file_path, separator, skip_header)


def load_ground_truth(file_path: str, separator: str = "|", skip_header: bool = True) -> list[dict]:
    return load_predictions(file_path, separator, skip_header)


def to_pair_dict_strict(items: list[dict], *, name: str) -> dict[tuple[str, str], bool]:
    """
    Convert list of items to dict keyed by (word1, word2).
    STRICT: raises on conflicting duplicates.
    """
    d: dict[tuple[str, str], bool] = {}
    for it in items:
        k = (it["word1"], it["word2"])
        v = it["prediction"]
        if k in d and d[k] != v:
            raise ValueError(f"Conflicting duplicate pair in {name}: {k} seen as both {d[k]} and {v}")
        d[k] = v
    return d


def to_pair_dict_predictions_resolve_with_gt(
    pred_items: list[dict],
    gt_dict: dict[tuple[str, str], bool],
    *,
    name: str,
) -> tuple[dict[tuple[str, str], bool], int, int, int]:
    """
    Build prediction dict keyed by (word1,word2), but if the prediction file contains
    conflicting duplicates for the same pair (both True and False), resolve like this:

    - If the pair exists in ground truth: choose the value that matches GT.
    - Else: fall back to the first seen value (keep stable behavior).

    Returns: (pred_dict, conflicts_total, conflicts_resolved_using_gt, conflicts_unresolved_no_gt)
    """
    seen_values: dict[tuple[str, str], set[bool]] = {}
    first_value: dict[tuple[str, str], bool] = {}

    for it in pred_items:
        k = (it["word1"], it["word2"])
        v = it["prediction"]

        if k not in first_value:
            first_value[k] = v
            seen_values[k] = {v}
        else:
            seen_values[k].add(v)

    pred_dict: dict[tuple[str, str], bool] = {}
    conflicts_total = 0
    conflicts_resolved_using_gt = 0
    conflicts_unresolved_no_gt = 0

    for k, vals in seen_values.items():
        if len(vals) == 1:
            pred_dict[k] = next(iter(vals))
            continue

        # conflicting duplicate
        conflicts_total += 1

        if k in gt_dict:
            gt_val = gt_dict[k]
            # pick the value that matches GT (must exist because vals={True,False} typically)
            pred_dict[k] = gt_val if gt_val in vals else first_value[k]
            conflicts_resolved_using_gt += 1
        else:
            # no GT available for this pair, keep first-seen value
            pred_dict[k] = first_value[k]
            conflicts_unresolved_no_gt += 1

    return pred_dict, conflicts_total, conflicts_resolved_using_gt, conflicts_unresolved_no_gt


def compute_metrics(y_true: list[bool], y_pred: list[bool]) -> dict:
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
    print("=" * 50)
    print("CLASSIFIER EVALUATION RESULTS")
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
    print("CLASSIFIER EVALUATION TOOL - MULTIPLE DATASETS")
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

    separator = input("Enter separator (default '|'): ").strip() or "|"
    skip_header_input = input("Skip header row (yes/no)? (default 'yes'): ").strip().lower() or "yes"
    skip_header = skip_header_input in {"yes", "y", "true", "1"}

    all_y_true: list[bool] = []
    all_y_pred: list[bool] = []

    processed_pairs = 0
    skipped_pairs = 0

    total_gt_pairs = 0
    total_pred_pairs = 0
    total_missed_pairs = 0
    total_extra_pairs = 0

    # tracking duplicates in predictions
    total_pred_conflicts = 0
    total_pred_conflicts_resolved = 0
    total_pred_conflicts_unresolved = 0

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

        ground_truth = load_ground_truth(str(gt_path_p), separator, skip_header)
        predictions = load_predictions(str(pred_path_p), separator, skip_header)
        identifier = pred_path_p.stem

        # Ground truth stays strict (if GT has conflicts, that's a data problem)
        gt_dict = to_pair_dict_strict(ground_truth, name=f"ground truth ({gt_path_p.name})")

        # Predictions: resolve conflicts using ground truth if possible
        pred_dict, c_total, c_resolved, c_unresolved = to_pair_dict_predictions_resolve_with_gt(
            predictions,
            gt_dict,
            name=f"predictions ({pred_path_p.name})",
        )

        total_pred_conflicts += c_total
        total_pred_conflicts_resolved += c_resolved
        total_pred_conflicts_unresolved += c_unresolved

        gt_pairs = set(gt_dict.keys())
        pred_pairs = set(pred_dict.keys())
        common_pairs = gt_pairs & pred_pairs

        missed_pairs = gt_pairs - pred_pairs
        extra_pairs = pred_pairs - gt_pairs

        total_gt_pairs += len(gt_pairs)
        total_pred_pairs += len(pred_pairs)
        total_missed_pairs += len(missed_pairs)
        total_extra_pairs += len(extra_pairs)

        if not common_pairs:
            print(f"Warning: No matching word pairs found in {identifier} (pair {i})")
            print(f"  GT pairs: {len(gt_pairs)} | Pred pairs: {len(pred_pairs)} | Missed: {len(missed_pairs)} | Extra: {len(extra_pairs)}")
            print(f"  Prediction duplicate conflicts: {c_total} (resolved using GT: {c_resolved}, unresolved(no GT): {c_unresolved})\n")
            skipped_pairs += 1
            continue

        common_sorted = sorted(common_pairs)
        y_true = [gt_dict[pair] for pair in common_sorted]
        y_pred = [pred_dict[pair] for pair in common_sorted]

        all_y_true.extend(y_true)
        all_y_pred.extend(y_pred)

        processed_pairs += 1
        per_metrics = compute_metrics(y_true, y_pred)

        print(f"Processed pair {i}: {identifier}")
        print(f"  GT pairs:     {len(gt_pairs)}")
        print(f"  Pred pairs:   {len(pred_pairs)}")
        print(f"  Matched:      {len(common_pairs)}")
        print(f"  Missed (GT-only):  {len(missed_pairs)}")
        print(f"  Extra (Pred-only): {len(extra_pairs)}")
        print(f"  Prediction duplicate conflicts: {c_total} (resolved using GT: {c_resolved}, unresolved(no GT): {c_unresolved})")
        print(f"  Matched-sample TP/FP/FN/TN: {per_metrics['tp']}/{per_metrics['fp']}/{per_metrics['fn']}/{per_metrics['tn']}\n")

    if not all_y_true:
        raise ValueError("No matched samples across all file pairs. Cannot compute metrics.")

    metrics = compute_metrics(all_y_true, all_y_pred)

    print_results(metrics)
    print(f"Total File Pairs Entered: {len(file_pairs)}")
    print(f"Pairs Processed:         {processed_pairs}")
    print(f"Pairs Skipped:           {skipped_pairs}")
    print(f"Total Matched Samples:   {len(all_y_true)}\n")

    print("Coverage across datasets (pair identity, order matters):")
    print(f"  Total GT pairs:        {total_gt_pairs}")
    print(f"  Total Pred pairs:      {total_pred_pairs}")
    print(f"  Total Missed pairs:    {total_missed_pairs}  (in GT, not in Pred)")
    print(f"  Total Extra pairs:     {total_extra_pairs}   (in Pred, not in GT)\n")

    print("Prediction duplicate conflict handling:")
    print(f"  Conflicting duplicate pairs total:      {total_pred_conflicts}")
    print(f"  Resolved using ground truth:            {total_pred_conflicts_resolved}")
    print(f"  Unresolved (pair not in ground truth):  {total_pred_conflicts_unresolved}\n")

    output_path = Path(__file__).parent / "generalisation_containment_evaluation_results.txt"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("=" * 50 + "\n")
        f.write("CLASSIFIER EVALUATION RESULTS - MULTIPLE DATASETS\n")
        f.write("=" * 50 + "\n\n")

        f.write(f"Total File Pairs Entered: {len(file_pairs)}\n")
        f.write(f"Pairs Processed:         {processed_pairs}\n")
        f.write(f"Pairs Skipped:           {skipped_pairs}\n")
        f.write(f"Total Matched Samples:   {len(all_y_true)}\n\n")

        f.write("Coverage across datasets (pair identity, order matters):\n")
        f.write(f"  Total GT pairs:        {total_gt_pairs}\n")
        f.write(f"  Total Pred pairs:      {total_pred_pairs}\n")
        f.write(f"  Total Missed pairs:    {total_missed_pairs}  (in GT, not in Pred)\n")
        f.write(f"  Total Extra pairs:     {total_extra_pairs}   (in Pred, not in GT)\n\n")

        f.write("Prediction duplicate conflict handling:\n")
        f.write(f"  Conflicting duplicate pairs total:      {total_pred_conflicts}\n")
        f.write(f"  Resolved using ground truth:            {total_pred_conflicts_resolved}\n")
        f.write(f"  Unresolved (pair not in ground truth):  {total_pred_conflicts_unresolved}\n\n")

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