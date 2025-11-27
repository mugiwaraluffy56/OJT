import argparse
import os
from .scanner.code_galaxy import CodeGalaxyScanner
from .models.soul_reader import SoulReader

def main():
    parser = argparse.ArgumentParser(description="The AI License Soul-Reader™. Gaze into the legal soul of your codebase.")
    parser.add_argument("path", help="Path to a file or directory to analyze.")
    args = parser.parse_args()

    print(f"Analyzing path: {args.path}")
    print("The AI License Soul-Reader™ is awakening...")

    scanner = CodeGalaxyScanner(args.path)
    license_files = scanner.scan()

    if not license_files:
        print("No potential license files found in the code-galaxy.")
        return

    # Construct the absolute path to the data directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, "..", "data") # data is in project root

    # Load training data from the data directory
    X_train = []
    y_train = []
    
    # Dynamically scan the data directory for license files
    # and map filenames to canonical license names.
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
                canonical_name = filename_to_canonical[filename_base]
                with open(filepath, "r", encoding="utf-8") as f:
                    X_train.append(f.read())
                    y_train.append(canonical_name)
            else:
                print(f"Warning: No canonical name mapping found for '{filename}'. Skipping.")

    
    if not X_train:
        print("Error: No training data found. Cannot initialize Soul-Reader.")
        return

    soul_reader = SoulReader()
    soul_reader.train(X_train, y_train)

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