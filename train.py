import os
import numpy as np
from sklearn.model_selection import train_test_split
import evaluate
from license_detector.models.soul_reader import SoulReader

def compute_metrics(predictions, labels):
    """
    Computes accuracy, precision, recall, and F1-score for the model's predictions.
    """
    precision_metric = evaluate.load("precision")
    recall_metric = evaluate.load("recall")
    f1_metric = evaluate.load("f1")
    accuracy_metric = evaluate.load("accuracy")

    return {
        'accuracy': accuracy_metric.compute(predictions=predictions, references=labels)["accuracy"],
        'precision': precision_metric.compute(predictions=predictions, references=labels, average='weighted')["precision"],
        'recall': recall_metric.compute(predictions=predictions, references=labels, average='weighted')["recall"],
        'f1': f1_metric.compute(predictions=predictions, references=labels, average='weighted')["f1"],
    }

def main():
    """
    This script trains and evaluates the AI License Soul-Reader model.
    """
    print("Starting the training and evaluation process...")

    # Load data
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, "data")
    X = []
    y = []
    filename_to_canonical = {
        "mit": "MIT",
        "apache-2.0": "Apache-2.0",
        "bsd-3-clause": "BSD-3-Clause",
        "bsd-2-clause": "BSD-2-Clause",
        "isc": "ISC",
        "gpl-3.0-only": "GPL-3.0-only",
        "gpl-2.0-only": "GPL-2.0-only",
        "lgpl-3.0-only": "LGPL-3.0-only",
        "mpl-2.0": "MPL-2.0",
        "cc-by-4.0": "CC-BY-4.0",
    }
    for filename in os.listdir(data_dir):
        if filename.endswith(".txt"):
            filepath = os.path.join(data_dir, filename)
            filename_base = os.path.splitext(filename)[0]
            if filename_base in filename_to_canonical:
                with open(filepath, "r", encoding="utf-8") as f:
                    X.append(f.read())
                    y.append(filename_to_canonical[filename_base])

    if not X:
        print("Error: No training data found.")
        return

    # Split data into training and validation sets
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Initialize and train the model
    soul_reader = SoulReader()
    soul_reader.train(X_train, y_train)

    # Evaluate the model
    print("\n--- Evaluation Results ---")
    metrics = soul_reader.evaluate(X_val, y_val, compute_metrics)
    for key, value in metrics.items():
        print(f"{key.capitalize()}: {value:.4f}")
    print("------------------------\n")

    # Save the fine-tuned model
    print("Saving the fine-tuned model...")
    soul_reader.save_model("fine-tuned-model")
    print("Model saved to 'fine-tuned-model' directory.")

if __name__ == "__main__":
    main()
