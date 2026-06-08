"""
Script to compute evaluation metrics from confusion matrix values (TP, FP, FN, TN)
"""

def calculate_metrics(tp, fp, fn, tn):
    """
    Calculate evaluation metrics from confusion matrix values.
    
    Args:
        tp (float): True Positives
        fp (float): False Positives
        fn (float): False Negatives
        tn (float): True Negatives
    
    Returns:
        dict: Dictionary containing all calculated metrics
    """
    
    # Calculate metrics
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    sensitivity = recall  # Sensitivity is the same as Recall
    
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    f2 = (5 * precision * recall) / (4 * precision + recall) if (4 * precision + recall) > 0 else 0
    
    prevalence = (tp + fn) / (tp + fp + tn + fn) if (tp + fp + tn + fn) > 0 else 0
    
    # Accuracy (bonus metric)
    accuracy = (tp + tn) / (tp + fp + tn + fn) if (tp + fp + tn + fn) > 0 else 0
    
    return {
        'Precision': precision,
        'Recall': recall,
        'F1': f1,
        'F2': f2,
        'Sensitivity': sensitivity,
        'Prevalence': prevalence,
        'Accuracy': accuracy
    }


if __name__ == "__main__":
    # Example usage
    print("=" * 50)
    print("Metrics Calculator from Confusion Matrix")
    print("=" * 50)
    
    # Get input from user
    tp = float(input("Enter TP (True Positives): "))
    fp = float(input("Enter FP (False Positives): "))
    fn = float(input("Enter FN (False Negatives): "))
    tn = float(input("Enter TN (True Negatives): "))
    
    # Calculate metrics
    metrics = calculate_metrics(tp, fp, fn, tn)
    
    # Display results
    print("\n" + "=" * 50)
    print("RESULTS")
    print("=" * 50)
    for metric_name, value in metrics.items():
        print(f"{metric_name:.<25} {value:.4f}")
    print("=" * 50)
