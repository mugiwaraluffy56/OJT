# AI License Detector

*A modern, AI-powered tool for identifying software licenses within a codebase.*

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## Table of Contents

- [Introduction](#introduction)
- [Core Concepts](#core-concepts)
  - [AI-Powered Classification](#ai-powered-classification)
  - [On-the-Fly Fine-Tuning](#on-the-fly-fine-tuning)
  - [Codebase Scanning](#codebase-scanning)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Training and Dataset Expansion](#training-and-dataset-expansion)
  - [The Importance of Data](#the-importance-of-data)
  - [Adding New Licenses](#adding-new-licenses)
- [Architecture Deep Dive](#architecture-deep-dive)
- [Development and Contribution](#development-and-contribution)
- [Roadmap](#roadmap)
- [Disclaimer](#disclaimer)

## Introduction

AI License Detector is a command-line tool designed to identify software licenses within a given file or directory. In the complex landscape of open-source software, license compliance is crucial. This tool aims to provide a modern, AI-driven solution to the problem of license detection, moving beyond simple keyword matching to a more nuanced understanding of license texts.

This project was rebuilt from the ground up to leverage the power of modern transformer-based language models for more accurate and flexible license classification. It serves as a foundation for a powerful and scalable license detection engine.

## Core Concepts

### AI-Powered Classification

At the heart of this tool is a sophisticated language model from the Hugging Face `transformers` library. The current implementation uses `microsoft/MiniLM-L12-H384-uncased`, a smaller, faster, yet powerful model that is well-suited for this kind of classification task. This allows the tool to understand the semantic content of a license text, rather than just relying on keywords.

### On-the-Fly Fine-Tuning

Instead of using a pre-trained, general-purpose model, this tool employs an "on-the-fly" fine-tuning approach. Every time the `license-detect` command is run, the AI model is fine-tuned on the license dataset found in the `data` directory. This means the model is always up-to-date with the latest licenses you've added, and its knowledge can be easily expanded.

### Codebase Scanning

The tool can scan an entire directory to find potential license files. The current scanning mechanism looks for files named `LICENSE` or `COPYING`, or any file containing the word "license". This allows the tool to find license information even when it's not in a standard file.

## Features

-   **Transformer-Based Model**: Utilizes a state-of-the-art language model for classification.
-   **Dynamic Training**: The model is retrained on the available data every time it's run.
-   **Extensible Dataset**: Easily add new licenses to the training data.
-   **Automated Data Gathering**: A helper script is included to download license texts from the SPDX license list.
-   **Directory Scanning**: Recursively scans directories to find potential license files.
-   **Simple CLI**: A clean and easy-to-use command-line interface.

## Installation

It is recommended to install the tool in a virtual environment.

1.  **Clone the repository:**
    ```sh
    git clone https://github.com/mugiwaraluffy56/License-Detection.git
    cd License-Detection
    ```

2.  **Create and activate a virtual environment:**
    ```sh
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install the dependencies in editable mode:**
    ```sh
    pip3 install -e .
    ```

## Usage

The primary command is `license-detect`. It takes a single argument: the path to a file or directory.

**To scan an entire codebase:**
```sh
license-detect /path/to/your/project
```

**To analyze a single file:**
```sh
license-detect /path/to/your/LICENSE.md
```

## Training and Dataset Expansion

### The Importance of Data

The accuracy of the AI model is highly dependent on the size and quality of the training dataset. The current dataset is small and serves as a proof-of-concept. For production-level accuracy, the dataset in the `data` directory needs to be significantly expanded.

### Adding New Licenses

The power of this tool lies in its ability to learn from new data. You can expand the dataset by adding new license texts to the `data` directory.

**1. The Automated Way (Recommended):**

Use the `download_licenses.py` script to automatically download license texts from the official SPDX license list.

1.  **Add a license ID**: Open `download_licenses.py` and add the official SPDX ID of the license you want to the `LICENSE_IDS` list.
2.  **Run the script**:
    ```sh
    python3 download_licenses.py
    ```
3.  **Update the mapping**: Open `license_detector/cli.py` and add a mapping from the new filename (which is the lowercase SPDX ID) to the canonical license name in the `filename_to_canonical` dictionary.

**2. The Manual Way:**

1.  Save the full license text as a `.txt` file in the `data` directory (e.g., `my-license.txt`).
2.  Open `license_detector/cli.py` and add a mapping for your new license in the `filename_to_canonical` dictionary.

The model will automatically retrain with the new data the next time you run `license-detect`.

## Architecture Deep Dive

-   `license_detector/`: The main Python package.
    -   `cli.py`: The entry point for the command-line interface. It handles argument parsing, orchestrates the training and prediction process.
    -   `models/soul_reader.py`: Contains the `SoulReader` class, which encapsulates the `transformers` model, the tokenizer, and the training and prediction logic.
    -   `scanner/code_galaxy.py`: Contains the `CodeGalaxyScanner` class, responsible for scanning directories to find potential license files.
-   `data/`: The dataset directory. Contains `.txt` files, each with the text of a license.
-   `download_licenses.py`: A utility script to download license texts from the SPDX repository.
-   `setup.py`: Defines the project's metadata and dependencies.

## Development and Contribution

Contributions are welcome. Please open an issue to discuss any changes.

**To run tests (placeholder):**
```sh
pytest tests/
```

## Roadmap

-   [ ] **Expand the Dataset**: The most critical next step is to build a large and comprehensive dataset of license texts.
-   [ ] **Improve Prediction Accuracy**: Experiment with different models, hyperparameters, and training techniques.
-   [ ] **Add Evaluation Pipeline**: Implement a proper evaluation pipeline to measure the model's accuracy (e.g., precision, recall, F1-score).
-   [ ] **Enhance the Scanner**: Make the `CodeGalaxyScanner` more intelligent (e.g., by looking for license headers in source files).
-   [ ] **Output Formats**: Add options to output the results in different formats, such as JSON.

## Disclaimer

This tool is a proof-of-concept for an AI-driven license detector. The accuracy of the model is highly dependent on the size and quality of the training data. The current dataset is very small, and as a result, **the predictions are not guaranteed to be accurate.** For production use, a much larger and more comprehensive training dataset is required.
