import argparse
import os
from .scanner.code_galaxy import CodeGalaxyScanner
from .models.soul_reader import SoulReader

def main():
    parser = argparse.ArgumentParser(description="The AI License Soul-Reader™. Gaze into the legal soul of your codebase.")
    parser.add_argument("path", help="Path to a file or directory to analyze.")
    args = parser.parse_args()

    print(f"Analyzing path: {args.path}")
    
    model_path = "fine-tuned-model"
    if not os.path.exists(model_path):
        print(f"Error: Fine-tuned model not found at '{model_path}'.")
        print("Please run the training script first: python3 train.py")
        return

    print("The AI License Soul-Reader™ is awakening...")
    soul_reader = SoulReader.from_pretrained(model_path)

    scanner = CodeGalaxyScanner(args.path)
    license_files = scanner.scan()

    if not license_files:
        print("No potential license files found in the code-galaxy.")
        return
        
    print("\n--- Found Potential Licenses ---\n")
    for file_path in license_files:
        display_path = file_path
        if os.path.isdir(args.path): # Only use relpath if the input was a directory
            display_path = os.path.relpath(file_path, args.path)
        print(f"File: {display_path}")
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
            
            if not text.strip():
                print("  License: (empty file)")
                continue

            predicted_license = soul_reader.predict(text)
            print(f"  Predicted License: {predicted_license}")
        except Exception as e:
            print(f"  Error reading or predicting file: {e}")
        print("-" * 20)

if __name__ == "__main__":
    main()