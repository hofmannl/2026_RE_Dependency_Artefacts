from pathlib import Path
import pandas as pd
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix, classification_report
import matplotlib.pyplot as plt
import seaborn as sns

# Get ground truth and prediction file pairs
file_pairs = []
pair_num = 1

print("Enter ground truth and prediction file pairs:")
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

separator = input("Enter the separator (default '|'): ").strip() or '|'

# Map CRUD abbreviations to full words
crud_mapping = {'c': 'create', 'r': 'read', 'u': 'update', 'd': 'delete'}

def expand_crud(value):
    """Convert single letter CRUD abbreviations to full words"""
    return crud_mapping.get(value, value)

def load_and_clean(file_path, separator):
    """Load CSV and clean columns"""
    df = pd.read_csv(file_path, sep=separator)
    df['story'] = df['story'].str.strip().str.replace('"', '').str.replace("'", '').str.lower()
    df['action'] = df['action'].str.strip().str.replace('"', '').str.replace("'", '').str.lower()
    df['classified_action'] = df['classified_action'].str.strip().str.replace('"', '').str.replace("'", '').str.lower().apply(expand_crud)
    return df

# Accumulate all predictions and ground truth across all pairs
all_y_pred = []
all_y_true = []
classes = ['create', 'read', 'update', 'delete']

# Process each ground truth and prediction file pair
for gt_path, pred_path in file_pairs:
    ground_truth_df = load_and_clean(gt_path, separator)
    results_df = load_and_clean(pred_path, separator)
    filename_identifier = Path(pred_path).stem
    
    # Merge based on substring matching: predicted story contained in ground truth story and same action
    matches = []
    matched_predictions = set()

    i: int = 0
    
    for idx, pred_row in results_df.iterrows():
        found_match = False
        for _, gt_row in ground_truth_df.iterrows():
            # Check if predicted story is contained in ground truth story AND actions match
            if (gt_row['story'] in pred_row['story'] and pred_row['action'] == gt_row['action']):
                matches.append({
                    'story': gt_row['story'],
                    'action': pred_row['action'],
                    'classified_action_x': pred_row['classified_action'],
                    'classified_action_y': gt_row['classified_action'],
                })
                matched_predictions.add(idx)
                found_match = True
                break  # Only match first occurrence for each prediction
        
        # if sentence + action match not found, try to match only based on action
        if not found_match:
            for _, gt_row in ground_truth_df.iterrows():
                if pred_row['action'] == gt_row['action']:
                    matches.append({
                        'story': gt_row['story'],
                        'action': pred_row['action'],
                        'classified_action_x': pred_row['classified_action'],
                        'classified_action_y': gt_row['classified_action'],
                    })
                    matched_predictions.add(idx)
                    found_match = True
                    break

    eval_df = pd.DataFrame(matches)

    # Extract predicted and true labels
    y_pred = eval_df['classified_action_x'].tolist()
    y_true = eval_df['classified_action_y'].tolist()
    
    # Accumulate for overall metrics
    all_y_pred.extend(y_pred)
    all_y_true.extend(y_true)
    
    print(f"\nProcessed pair {pair_num - len(file_pairs)}: {filename_identifier} ({len(eval_df)} samples)")

# Calculate overall metrics across all pairs
accuracy = accuracy_score(all_y_true, all_y_pred)
precision, recall, f1, support = precision_recall_fscore_support(all_y_true, all_y_pred, average=None, labels=classes)

print(all_y_true)
print("---")
print(all_y_pred)

cm = confusion_matrix(all_y_true, all_y_pred, labels=classes)

# Print overall results
print("\n" + "=" * 60)
print("OVERALL CRUD CLASSIFIER EVALUATION RESULTS")
print("=" * 60)
print(f"\nTotal Pairs Processed: {len(file_pairs)}")
print(f"Overall Accuracy: {accuracy:.4f}")
print(f"Total Samples: {len(all_y_true)}")
print("\nPer-Class Metrics:")
print("-" * 60)

for cls, p, r, f, s in zip(classes, precision, recall, f1, support):
    # Calculate per-class accuracy (one-vs-all) from confusion matrix
    class_accuracy = accuracy_score(
        [1 if x == cls else 0 for x in all_y_true],
        [1 if x == cls else 0 for x in all_y_pred]
    )
    print(f"{cls.upper():10} | Precision: {p:.4f} | Recall: {r:.4f} | Accuracy: {class_accuracy:.4f} | F1: {f:.4f} | Support: {int(s)}")

print("\n" + classification_report(all_y_true, all_y_pred, labels=classes))

# Print confusion matrix
print("\n" + "=" * 60)
print("CONFUSION MATRIX")
print("=" * 60)
cm_df = pd.DataFrame(cm, index=classes, columns=classes)
print(cm_df)

# Save overall results to text file
output_path = Path(__file__).parent / f'overall_evaluation_results.txt'
with open(output_path, 'w') as f:
    f.write("=" * 60 + "\n")
    f.write("OVERALL CRUD CLASSIFIER EVALUATION RESULTS\n")
    f.write("=" * 60 + "\n\n")
    f.write(f"Total Pairs Processed: {len(file_pairs)}\n")
    f.write(f"Overall Accuracy: {accuracy:.4f}\n")
    f.write(f"Total Samples: {len(all_y_true)}\n\n")
    f.write("Per-Class Metrics:\n")
    f.write("-" * 60 + "\n")
    
    for cls, p, r, f_score, s in zip(classes, precision, recall, f1, support):
        class_accuracy = accuracy_score(
            [1 if x == cls else 0 for x in all_y_true],
            [1 if x == cls else 0 for x in all_y_pred]
        )
        f.write(f"{cls.upper():10} | Precision: {p:.4f} | Recall: {r:.4f} | Accuracy: {class_accuracy:.4f} | F1: {f_score:.4f} | Support: {int(s)}\n")
    
    f.write("\n" + classification_report(all_y_true, all_y_pred, labels=classes))
    f.write("\n\nConfusion Matrix:\n")
    f.write(cm_df.to_string())
    f.write("\n")

# # Generate confusion matrix visualization
# plt.figure(figsize=(10, 8))
# sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=classes, yticklabels=classes, cbar_kws={'label': 'Count'})
# plt.title('Confusion Matrix - CRUD Classification', fontsize=16, fontweight='bold')
# plt.ylabel('True Label', fontsize=12)
# plt.xlabel('Predicted Label', fontsize=12)
# plt.tight_layout()

# # Save confusion matrix plot
# cm_plot_path = Path(__file__).parent / 'confusion_matrix.png'
# plt.savefig(cm_plot_path, dpi=300, bbox_inches='tight')

def plot_confmat_ieee_single(cm, classes, title=None, outfile="confmat.pdf"):
    plt.rcParams.update({
        "font.size": 9,
        "axes.titlesize": 8,
        "axes.labelsize": 8,
        "xtick.labelsize": 8,
        "ytick.labelsize": 8,
        "figure.dpi": 300,
        "savefig.dpi": 300
    })

    plt.figure(figsize=(2.3, 2.3))

    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        annot_kws={"size": 8},     
        xticklabels=classes,
        yticklabels=classes,
        cbar=False,
        cbar_kws={"label": "Count"},
        square=True,
        linewidths=0.4,
        linecolor="white"
    )

    if title is not None:
        plt.title(title, pad=2, fontweight="bold")

    plt.xlabel("Predicted")
    plt.ylabel("True")

    plt.xticks(rotation=0)
    plt.yticks(rotation=90)

    plt.tight_layout()
    plt.savefig(outfile, bbox_inches="tight")
    plt.close()

plot_confmat_ieee_single(cm, classes, title=None, outfile=Path(__file__).parent / 'confusion_matrix.png')
print(f"Confusion matrix visualization saved to: {Path(__file__).parent / 'confusion_matrix.png'}")

plt.show()

print(f"\nOverall results saved to: {output_path}")

print("GT rows:", len(ground_truth_df))
print("Pred rows:", len(results_df))
print("Matched rows:", len(eval_df))