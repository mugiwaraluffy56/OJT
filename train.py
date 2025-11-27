import os
from license_detector.models.soul_reader import SoulReader

def main():
    """
    This script trains the AI License Soul-Reader model on the dataset in the `data` directory
    and saves the fine-tuned model to disk.
    """
    print("Starting the training process for the AI License Soul-Reader...")

    # Construct the absolute path to the data directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, "data")

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
        print("Error: No training data found. Cannot train the model.")
        return

    # Initialize and train the model
    soul_reader = SoulReader()
    soul_reader.train(X_train, y_train)

    # Save the fine-tuned model
    print("Saving the fine-tuned model...")
    soul_reader.save_model("fine-tuned-model")
    print("Model saved to 'fine-tuned-model' directory.")

if __name__ == "__main__":
    main()
