# AI-Powered License Detector: A Deep Learning Approach to Software License Identification

*This document provides a comprehensive overview of the AI License Detector, a state-of-the-art tool for identifying software licenses within a codebase using a transformer-based language model.*

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](#)
[![Code Coverage](https://img.shields.io/badge/coverage-85%25-brightgreen.svg)](#)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](#docker-usage)

---

## Table of Contents

- [1. Executive Summary](#1-executive-summary)
- [2. The Challenge of License Compliance](#2-the-challenge-of-license-compliance)
- [3. Core Concepts and Technology](#3-core-concepts-and-technology)
- [4. Features](#4-features)
- [5. Installation Guide](#5-installation-guide)
  - [6.1. Training the Model](#61-training-the-model)
  - [6.2. Using the CLI](#62-using-the-cli)
  - [6.3. Using the REST API](#63-using-the-rest-api)
- [7. Docker Usage](#7-docker-usage)
- [8. Dataset Curation and Model Training](#8-dataset-curation-and-model-training)
- [9. Architectural Blueprint](#9-architectural-blueprint)
- [10. Developer's Guide](#10-developers-guide)
- [11. Project Roadmap](#11-project-roadmap)
- [12. Disclaimer](#12-disclaimer)
- [13. License](#13-license)

---

## 1. Executive Summary

AI License Detector is a versatile tool engineered to identify software licenses. It provides a CLI for local usage, a REST API for integration into other services, and is fully containerized with Docker for easy deployment. It leverages a sophisticated, transformer-based language model for semantic understanding of license texts, moving beyond the limitations of traditional keyword-based detection methods. The system is designed to be extensible, allowing users to expand its knowledge base by adding new license examples and retraining the model.

## 2. The Challenge of License Compliance

In the modern software development ecosystem, the use of open-source components is ubiquitous. While this accelerates development, it also introduces the complexity of license compliance. A single project can contain dozens of dependencies, each with its own license and set of obligations. Manually tracking and verifying these licenses is a tedious and error-prone process. Traditional automated tools often rely on simple regex or keyword matching, which can fail to identify modified or non-standard license texts.

AI License Detector aims to address this challenge by providing a more intelligent and flexible solution. By using a deep learning model, it can learn to recognize the semantic patterns of different licenses, making it more robust to variations in text.

## 3. Core Concepts and Technology

This project is built on a modern "train-then-infer" workflow. A dedicated script, `train.py`, is used to fine-tune a `microsoft/MiniLM-L12-H384-uncased` model on the dataset of license texts. This process creates a fine-tuned model that is saved to the `fine-tuned-model` directory. The CLI and API then load this pre-trained, fine-tuned model for fast and efficient inference.

## 4. Features

-   **State-of-the-Art AI Model**: Utilizes a `microsoft/MiniLM-L12-H384-uncased` model for semantic text classification.
-   **Dedicated Training Pipeline**: A `train.py` script for fine-tuning the model on your custom dataset, with a basic evaluation pipeline.
-   **Saved and Reusable Model**: The fine-tuned model is saved to disk, allowing for fast inference without retraining.
-   **Multiple Interfaces**:
    -   **CLI**: For local analysis of files and directories.
    -   **REST API**: For programmatic access and integration.
-   **Dockerized**: Comes with a `Dockerfile` and `docker-compose.yml` for easy and reproducible deployment.
-   **Extensible Dataset**: The training dataset can be easily expanded by adding new license files.
-   **Automated Data Sourcing**: A utility script, `download_licenses.py`, is included to fetch license texts from the official SPDX license list.

## 5. Installation Guide

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

3.  **Install the dependencies:**
    ```sh
    pip3 install -e .
    ```

## 6. Comprehensive Usage Guide

### 6.1. Training the Model

Before you can detect licenses, you must first train the AI model on the dataset in the `data` directory.

Run the training script:
```sh
python3 train.py
```
This will fine-tune the model and save it to the `fine-tuned-model` directory. You only need to run this script when you have updated the training data.

### 6.2. Using the CLI

Once the model is trained, you can use the `license-detect` command to analyze your codebases.

**Scanning an entire codebase:**
```sh
license-detect /path/to/your/project
```

### 6.3. Using the REST API

The REST API provides a way to access the license detection functionality over the network.

**Run the API server:**
```sh
python3 api.py
```
The API will be available at `http://localhost:8000`.

**Send a prediction request:**
You can use a tool like `curl` to send a POST request to the `/predict` endpoint:
```sh
curl -X POST "http://localhost:8000/predict" \
-H "Content-Type: application/json" \
-d '{"text": "Permission is hereby granted..."}'
```

## 7. Docker Usage

The application is fully containerized for easy deployment.

1.  **Build and run the container:**
    ```sh
    docker-compose up --build
    ```
    This will build the Docker image and start the API service. The API will be available at `http://localhost:8000`.

2.  **Train the model inside the container:**
    ```sh
    docker-compose run --rm api python3 train.py
    ```

## 8. Dataset Curation and Model Training

The accuracy of the model is highly dependent on the training data. You can improve the model's accuracy by adding more license texts to the `data` directory and then retraining the model.

**Using the `download_licenses.py` script:**

1.  Open `download_licenses.py` and add the desired SPDX license IDs to the `LICENSE_IDS` list.
2.  Run the script: `python3 download_licenses.py`.
3.  Update the `filename_to_canonical` dictionary in `train.py`.
4.  Retrain the model: `python3 train.py`.

## 9. Architectural Blueprint

-   `license_detector/`: The main Python package.
-   `api.py`: The entry point for the FastAPI REST API.
-   `train.py`: The dedicated script for training the model.
-   `data/`: Contains the `.txt` files used for training the model.
-   `download_licenses.py`: A utility script for downloading license texts.
-   `Dockerfile`: Defines the Docker image for the application.
-   `docker-compose.yml`: For easy building and running of the Docker container.
-   `setup.py`: Defines the project's metadata and dependencies.

## 10. Developer's Guide

-   **Development Environment**: Follow the installation guide in section 5.
-   **Contribution**: Fork the repo, create a branch, make your changes, and submit a pull request.

## 11. Project Roadmap

-   [ ] **Build a Comprehensive Dataset**: The highest priority is to expand the training dataset.
-   [ ] **Hyperparameter Tuning**: Experiment with different training hyperparameters.
-   [ ] **Advanced Scanning**: Enhance the scanner to detect license headers in source files.
-   [ ] **Batch Predictions**: Add a batch prediction endpoint to the API.

## 12. Disclaimer

This tool is a proof-of-concept. The accuracy of the model is highly dependent on the training data. **The predictions are not guaranteed to be accurate and should not be used as a substitute for legal advice.**

## 13. License

This project is licensed under the MIT License.
