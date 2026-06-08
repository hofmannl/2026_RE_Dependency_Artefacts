from pathlib import Path
import csv
from typing import Optional, List, Dict, Tuple

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
    v = (label or "").strip().lower()
    if v in TRUTHY:
        return True
    if v in FALSY:
        return False
    return None


def normalize_pair(word1: str, word2: str) -> Tuple[str, str]:
    """
    Unordered key for semantic equivalence: (a,b) == (b,a)
    Lowercase + strip + lexicographic ordering.
    """
    a = (word1 or "").strip().lower()
    b = (word2 or "").strip().lower()
    return (a, b) if a <= b else (b, a)


def load_csv(file_path: str, separator: str = "|", skip_header: bool = True) -> List[Dict]:
    """
    Load data from file with format: word1<sep>word2<sep>true/false
    Allows optional 4th column (comments) which will be ignored.
    Skips rows with unparsable labels, empty rows, or wrong column count.
    """
    rows: List[Dict] = []
    with open(str(file_path), "r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f, delimiter=separator)
        for idx, parts in enumerate(reader):
            if idx == 0 and skip_header:
                continue
            if not parts or all(not p.strip() for p in parts):
                continue
            if len(parts) not in (3, 4):
                continue
            if len(parts) == 4:
                parts = parts[:3]

            word1, word2, label = parts
            b = parse_bool(label)
            if b is None:
                continue

            rows.append(
                {
                    "word1": (word1 or "").strip().lower(),
                    "word2": (word2 or "").strip().lower(),
                    "prediction": b,
                }
            )
    return rows


def load_predictions(file_path: str, separator: str = "|", skip_header: bool = True) -> List[Dict]:
    return load_csv(file_path, separator, skip_header)


def load_ground_truth(file_path: str, separator: str = "|", skip_header: bool = True) -> List[Dict]:
    return load_predictions(file_path, separator, skip_header)


def to_pair_dict_strict_unordered(items: List[Dict], *, name: str) -> Dict[Tuple[str, str], bool]:
    """
    Convert list of items to dict keyed by normalized unordered pair.
    STRICT: raises on conflicting duplicates, including opposite-direction duplicates.
    """
    d: Dict[Tuple[str, str], bool] = {}
    for it in items:
        k = normalize_pair(it["word1"], it["word2"])
        v = it["prediction"]
        if k in d and d[k] != v:
            raise ValueError(f"Conflicting duplicate pair in {name}: {k} seen as both {d[k]} and {v}")
        d[k] = v
    return d


def to_pair_dict_predictions_resolve_with_gt_unordered(
    pred_items: List[Dict],
    gt_dict: Dict[Tuple[str, str], bool],
    *,
    name: str,
) -> Tuple[Dict[Tuple[str, str], bool], int, int, int, int, int]:
    """
    Build prediction dict keyed by normalized unordered pair.

    If predictions contain conflicting duplicates for the same normalized pair, resolve:
      - If pair exists in ground truth: choose the value that matches GT.
      - Else: keep first seen value.

    Also counts duplicate rows (LLM may output both directions or repeats).

    Returns:
      pred_dict,
      conflicts_total_keys,
      conflicts_resolved_using_gt,
      conflicts_unresolved_no_gt,
      extra_duplicate_rows,
      extra_conflicting_rows
    """
    values_by_key: Dict[Tuple[str, str], List[bool]] = {}

    for it in pred_items:
        k = normalize_pair(it["word1"], it["word2"])
        values_by_key.setdefault(k, []).append(it["prediction"])

    pred_dict: Dict[Tuple[str, str], bool] = {}

    conflicts_total_keys = 0
    conflicts_resolved = 0
    conflicts_unresolved = 0
    extra_duplicate_rows = 0
    extra_conflicting_rows = 0

    for k, vals in values_by_key.items():
        if len(vals) > 1:
            extra_duplicate_rows += len(vals) - 1

        unique_vals = set(vals)

        if len(unique_vals) == 1:
            chosen = vals[0]
        else:
            conflicts_total_keys += 1
            if k in gt_dict and gt_dict[k] in unique_vals:
                chosen = gt_dict[k]
                conflicts_resolved += 1
            else:
                chosen = vals[0]
                conflicts_unresolved += 1

        pred_dict[k] = chosen

        if len(vals) > 1:
            extra_conflicting_rows += sum(1 for v in vals[1:] if v != chosen)

    return (
        pred_dict,
        conflicts_total_keys,
        conflicts_resolved,
        conflicts_unresolved,
        extra_duplicate_rows,
        extra_conflicting_rows,
    )


def compute_metrics(y_true: List[bool], y_pred: List[bool]) -> Dict:
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


def format_results(
    metrics: Dict,
    *,
    total_file_pairs: int,
    processed_pairs: int,
    skipped_pairs: int,
    total_matched_samples: int,
    total_gt_pairs: int,
    total_pred_pairs: int,
    total_missed_pairs: int,
    total_extra_pairs: int,
    total_pred_conflicts: int,
    total_pred_conflicts_resolved: int,
    total_pred_conflicts_unresolved: int,
    # optional extra row stats (printed but not in your example header)
    total_extra_duplicate_rows: int,
    total_extra_conflicting_rows: int,
) -> str:
    lines = []
    lines.append("=" * 50)
    lines.append("CLASSIFIER EVALUATION RESULTS - MULTIPLE DATASETS")
    lines.append("=" * 50)
    lines.append("")
    lines.append(f"Total File Pairs Entered: {total_file_pairs}")
    lines.append(f"Pairs Processed:         {processed_pairs}")
    lines.append(f"Pairs Skipped:           {skipped_pairs}")
    lines.append(f"Total Matched Samples:   {total_matched_samples}")
    lines.append("")
    lines.append("Coverage across datasets (pair identity, order matters):")
    lines.append(f"  Total GT pairs:        {total_gt_pairs}")
    lines.append(f"  Total Pred pairs:      {total_pred_pairs}")
    lines.append(f"  Total Missed pairs:    {total_missed_pairs}  (in GT, not in Pred)")
    lines.append(f"  Total Extra pairs:     {total_extra_pairs}   (in Pred, not in GT)")
    lines.append("")
    lines.append("Prediction duplicate conflict handling:")
    lines.append(f"  Conflicting duplicate pairs total:      {total_pred_conflicts}")
    lines.append(f"  Resolved using ground truth:            {total_pred_conflicts_resolved}")
    lines.append(f"  Unresolved (pair not in ground truth):  {total_pred_conflicts_unresolved}")
    lines.append("")
    # Keep your requested format; also include extra duplicate-row stats (LLM-friendly).
    # If you truly want EXACTLY your sample output, delete this block.
    lines.append("Prediction duplicate row handling (LLM output):")
    lines.append(f"  Extra duplicate prediction rows total:  {total_extra_duplicate_rows}")
    lines.append(f"  Conflicting extra rows vs chosen label: {total_extra_conflicting_rows}")
    lines.append("")
    lines.append(f"Accuracy:  {metrics['accuracy']:.4f}")
    lines.append(f"Precision: {metrics['precision']:.4f}")
    lines.append(f"Recall:    {metrics['recall']:.4f}")
    lines.append(f"F1-Score:  {metrics['f1']:.4f}")
    lines.append(f"F2-Score:  {metrics['f2']:.4f}")
    lines.append(f"TP: {metrics['tp']}  FP: {metrics['fp']}  FN: {metrics['fn']}  TN: {metrics['tn']}")
    lines.append("")
    lines.append("Confusion Matrix (labels=[False, True]):")
    lines.append(str(metrics["confusion_matrix"]))
    return "\n".join(lines) + "\n"


def main() -> None:
    print("=" * 50)
    print("CLASSIFIER EVALUATION TOOL - MULTIPLE DATASETS")
    print("=" * 50)

    file_pairs: List[Tuple[str, str]] = []
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

    all_y_true: List[bool] = []
    all_y_pred: List[bool] = []

    processed_pairs = 0
    skipped_pairs = 0

    total_gt_pairs = 0
    total_pred_pairs = 0
    total_missed_pairs = 0
    total_extra_pairs = 0

    total_pred_conflicts = 0
    total_pred_conflicts_resolved = 0
    total_pred_conflicts_unresolved = 0

    total_extra_duplicate_rows = 0
    total_extra_conflicting_rows = 0

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

        # GT strict: if GT has conflicts for same unordered pair, that's a data issue.
        gt_dict = to_pair_dict_strict_unordered(ground_truth, name=f"ground truth ({gt_path_p.name})")

        # Predictions: resolve conflicts using GT when possible; also count duplicate rows
        (
            pred_dict,
            c_total,
            c_resolved,
            c_unresolved,
            extra_dup_rows,
            extra_conf_rows,
        ) = to_pair_dict_predictions_resolve_with_gt_unordered(
            predictions, gt_dict, name=f"predictions ({pred_path_p.name})"
        )

        total_pred_conflicts += c_total
        total_pred_conflicts_resolved += c_resolved
        total_pred_conflicts_unresolved += c_unresolved
        total_extra_duplicate_rows += extra_dup_rows
        total_extra_conflicting_rows += extra_conf_rows

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
            skipped_pairs += 1
            continue

        common_sorted = sorted(common_pairs)
        y_true = [gt_dict[pair] for pair in common_sorted]
        y_pred = [pred_dict[pair] for pair in common_sorted]

        all_y_true.extend(y_true)
        all_y_pred.extend(y_pred)

        processed_pairs += 1

    if not all_y_true:
        raise ValueError("No matched samples across all file pairs. Cannot compute metrics.")

    metrics = compute_metrics(all_y_true, all_y_pred)

    output_text = format_results(
        metrics,
        total_file_pairs=len(file_pairs),
        processed_pairs=processed_pairs,
        skipped_pairs=skipped_pairs,
        total_matched_samples=len(all_y_true),
        total_gt_pairs=total_gt_pairs,
        total_pred_pairs=total_pred_pairs,
        total_missed_pairs=total_missed_pairs,
        total_extra_pairs=total_extra_pairs,
        total_pred_conflicts=total_pred_conflicts,
        total_pred_conflicts_resolved=total_pred_conflicts_resolved,
        total_pred_conflicts_unresolved=total_pred_conflicts_unresolved,
        total_extra_duplicate_rows=total_extra_duplicate_rows,
        total_extra_conflicting_rows=total_extra_conflicting_rows,
    )

    print(output_text)

    output_path = Path(__file__).parent / "semantic_equivalence_evaluation_results.txt"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(output_text)

    print(f"Results saved to: {output_path}")


if __name__ == "__main__":
    main()
