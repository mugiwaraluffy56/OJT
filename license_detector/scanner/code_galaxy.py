import os
from typing import List

class CodeGalaxyScanner:
    def __init__(self, path: str):
        self.path = path
        print("Preparing to scan the code-galaxy...")

    def scan(self) -> List[str]:
        """
        Scans the codebase and returns a list of files that might contain licenses.
        """
        print(f"Scanning {self.path} for potential license files...")
        potential_files = []
        if os.path.isdir(self.path):
            for root, _, files in os.walk(self.path):
                for file in files:
                    file_path = os.path.join(root, file)
                    if file.upper() in ["LICENSE", "COPYING"]:
                        potential_files.append(file_path)
                    else:
                        try:
                            with open(file_path, "r", encoding="utf-8") as f:
                                content = f.read(1024) # Read first 1k to check for license
                                if "license" in content.lower():
                                    potential_files.append(file_path)
                        except (UnicodeDecodeError, IOError):
                            # Ignore files that can't be read as text
                            continue
        elif os.path.isfile(self.path):
            potential_files.append(self.path)

        return list(set(potential_files)) # Return unique files
