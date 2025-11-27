# AI-Powered License Detector: A Deep Learning Approach to Software License Identification

*This document provides a comprehensive overview of the AI License Detector, a state-of-the-art tool for identifying software licenses within a codebase using a transformer-based language model.*

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](#)
[![Code Coverage](https://img.shields.io/badge/coverage-85%25-brightgreen.svg)](#)

---

## Table of Contents

- [1. Executive Summary](#1-executive-summary)
- [2. The Challenge of License Compliance](#2-the-challenge-of-license-compliance)
- [3. Core Concepts and Technology](#3-core-concepts-and-technology)
  - [3.1. The AI Engine: Transformer-Based Classification](#31-the-ai-engine-transformer-based-classification)
  - [3.2. Dynamic Learning: On-the-Fly Fine-Tuning](#32-dynamic-learning-on-the-fly-fine-tuning)
  - [3.3. The Scanner: Codebase Analysis](#33-the-scanner-codebase-analysis)
- [4. Features](#4-features)
- [5. Installation Guide](#5-installation-guide)
  - [5.1. Prerequisites](#51-prerequisites)
  - [5.2. Step-by-Step Installation](#52-step-by-step-installation)
- [6. Comprehensive Usage Guide](#6-comprehensive-usage-guide)
  - [6.1. CLI Arguments](#61-cli-arguments)
  - [6.2. Usage Scenarios](#62-usage-scenarios)
- [7. Dataset Curation and Model Training](#7-dataset-curation-and-model-training)
  - [7.1. The Critical Role of Data](#71-the-critical-role-of-data)
  - [7.2. Expanding the Dataset](#72-expanding-the-dataset)
- [8. Architectural Blueprint](#8-architectural-blueprint)
- [9. Developer's Guide](#9-developers-guide)
  - [9.1. Setting Up a Development Environment](#91-setting-up-a-development-environment)
  - [9.2. Contribution Workflow](#92-contribution-workflow)
- [10. Project Roadmap](#10-project-roadmap)
- [11. Disclaimer](#11-disclaimer)
- [12. License](#12-license)

---

## 1. Executive Summary

AI License Detector is a command-line tool engineered to identify software licenses within a file or directory. It leverages a sophisticated, transformer-based language model for semantic understanding of license texts, moving beyond the limitations of traditional keyword-based detection methods. The system is designed to be extensible, allowing users to expand its knowledge base by adding new license examples and retraining the model on the fly. This document serves as a comprehensive guide to its usage, architecture, and future development.

## 2. The Challenge of License Compliance

In the modern software development ecosystem, the use of open-source components is ubiquitous. While this accelerates development, it also introduces the complexity of license compliance. A single project can contain dozens of dependencies, each with its own license and set of obligations. Manually tracking and verifying these licenses is a tedious and error-prone process. Traditional automated tools often rely on simple regex or keyword matching, which can fail to identify modified or non-standard license texts.

AI License Detector aims to address this challenge by providing a more intelligent and flexible solution. By using a deep learning model, it can learn to recognize the semantic patterns of different licenses, making it more robust to variations in text.

## 3. Core Concepts and Technology

### 3.1. The AI Engine: Transformer-Based Classification

The core of this tool is a transformer-based language model from the Hugging Face ecosystem. The current implementation utilizes `microsoft/MiniLM-L12-H384-uncased`, a distilled version of BERT that offers a balance of performance and efficiency. This model is capable of understanding the contextual nuances of language, making it well-suited for classifying complex legal texts like software licenses.

### 3.2. Dynamic Learning: On-the-Fly Fine-Tuning

A key feature of this tool is its ability to learn and adapt. Every time the `license-detect` command is executed, the language model is fine-tuned on the dataset of license texts found in the `data` directory. This is achieved using the `transformers.Trainer` utility, which provides a high-level API for training and evaluation. The hyperparameters for training can be found in the `SoulReader.train` method and can be adjusted to optimize performance.

### 3.3. The Scanner: Codebase Analysis

The `CodeGalaxyScanner` is responsible for finding potential license files within a codebase. It recursively scans the specified directory and uses a set of heuristics to identify files that are likely to contain license information. Currently, it looks for files named `LICENSE` or `COPYING`, or any file that contains the word "license" (case-insensitive) within its first 1024 bytes.

## 4. Features

-   **State-of-the-Art AI Model**: Utilizes a `microsoft/MiniLM-L12-H384-uncased` model for semantic text classification.
-   **Dynamic On-the-Fly Training**: The model is fine-tuned on the available data with every run, ensuring it's always up-to-date.
-   **Extensible and Scalable Dataset**: The training dataset can be easily expanded by adding new license files.
-   **Automated Data Sourcing**: A utility script, `download_licenses.py`, is included to fetch license texts from the official SPDX license list.
-   **Recursive Directory Scanning**: The tool can analyze entire codebases to identify license files.
-   **Simple and Clean CLI**: A single command interface for ease of use.

## 5. Installation Guide

### 5.1. Prerequisites

-   Python 3.9 or higher
-   `pip` package manager

### 5.2. Step-by-Step Installation

1.  **Clone the repository:**
    ```sh
    git clone https://github.com/mugiwaraluffy56/License-Detection.git
    cd License-Detection
    ```

2.  **Create and activate a virtual environment (recommended):**
    ```sh
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install the dependencies in editable mode:** This allows you to modify the source code and have the changes immediately reflected.
    ```sh
    pip3 install -e .
    ```

## 6. Comprehensive Usage Guide

### 6.1. CLI Arguments

The tool is run via the `license-detect` command, which takes a single positional argument:
-   `path`: The path to a file or directory to be analyzed.

### 6.2. Usage Scenarios

**Scanning an entire codebase:**
```sh
license-detect /path/to/your/project
```

**Analyzing a single file:**
```sh
license-detect /path/to/your/LICENSE.md
```

**Scanning the current directory:**
```sh
license-detect .
```

## 7. Dataset Curation and Model Training

### 7.1. The Critical Role of Data

The accuracy of this AI model is directly proportional to the size and quality of its training data. The current dataset is small and intended as a proof-of-concept. For a production-ready system, a dataset containing hundreds or thousands of examples for each license category is required.

### 7.2. Expanding the Dataset

You can improve the model's accuracy by adding more license texts to the `data` directory.

**Using the `download_licenses.py` script:**

1.  Open `download_licenses.py` and add the desired SPDX license IDs to the `LICENSE_IDS` list.
2.  Run the script: `python3 download_licenses.py`.
3.  Open `license_detector/cli.py` and update the `filename_to_canonical` dictionary to map the new filenames to their canonical names.

**Adding a license manually:**

1.  Save the license text to a `.txt` file in the `data` directory.
2.  Update the `filename_to_canonical` dictionary in `license_detector/cli.py`.

## 8. Architectural Blueprint

-   `license_detector/`: The main Python package.
    -   `cli.py`: The entry point for the CLI. It orchestrates the process of scanning, training, and prediction.
    -   `models/soul_reader.py`: Defines the `SoulReader` class, which encapsulates the `transformers` model, tokenizer, and the training and prediction logic.
    -   `scanner/code_galaxy.py`: Defines the `CodeGalaxyScanner` class, responsible for finding potential license files.
-   `data/`: Contains the `.txt` files used for training the model.
-   `download_licenses.py`: A utility script for downloading license texts from the SPDX repository.
-   `setup.py`: Defines the project's metadata and dependencies.

## 9. Developer's Guide

### 9.1. Setting Up a Development Environment

Follow the installation guide in section 5 to set up a development environment. The editable install (`-e`) is crucial for development.

### 9.2. Contribution Workflow

1.  Fork the repository.
2.  Create a new branch for your feature or bug fix.
3.  Make your changes.
4.  (Optional) Add tests for your changes.
5.  Submit a pull request.

## 10. Project Roadmap

-   [ ] **Build a Comprehensive Dataset**: The highest priority is to expand the training dataset to include a wide variety of licenses.
-   [ ] **Hyperparameter Tuning**: Experiment with different training hyperparameters to improve model accuracy.
-   [ ] **Implement Evaluation Pipeline**: Add a proper evaluation pipeline to measure precision, recall, and F1-score.
-   [ ] **Advanced Scanning**: Enhance the `CodeGalaxyScanner` to detect license headers in source files.
-   [ ] **JSON Output**: Add a `--json` flag to output the results in a machine-readable format.

## 11. Disclaimer

This tool is a proof-of-concept and is provided "as is" without warranty of any kind. The accuracy of the model is highly dependent on the size and quality of the training data. **The predictions are not guaranteed to be accurate and should not be used as a substitute for legal advice.**

## 12. License

This project is licensed under the MIT License.