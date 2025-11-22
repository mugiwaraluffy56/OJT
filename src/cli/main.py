import argparse
import os

from src.classifier.main import LicenseClassifier

def main():
    parser = argparse.ArgumentParser(description="Detect license from a file.")
    parser.add_argument("file_path", help="Path to the file to analyze.")
    args = parser.parse_args()

    if not os.path.exists(args.file_path):
        print(f"Error: File not found at {args.file_path}")
        return

    with open(args.file_path, "r", encoding="utf-8") as f:
        text = f.read()

    # Load training data from the data directory
    X_train = []
    y_train = []
    data_dir = "data"
    for filename in os.listdir(data_dir):
        if filename.endswith(".txt"):
            filepath = os.path.join(data_dir, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                X_train.append(f.read())
                y_train.append(os.path.splitext(filename)[0])

    classifier = LicenseClassifier()
    classifier.train(X_train, y_train)
    
    predicted_license = classifier.predict(text)
    print(f"Predicted License: {predicted_license}")

if __name__ == "__main__":
    main()
