# Small runtime image with Python and required libs
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install build deps for scikit-learn
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential git curl gcc g++ libatlas-base-dev \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /action

# Copy code
COPY entrypoint.py /action/entrypoint.py
COPY README.md /action/README.md

# Install python deps (small, CI-friendly)
RUN pip install --no-cache-dir scikit-learn==1.2.2 rapidfuzz==2.9.1 numpy==1.26.0

# Make entrypoint executable
RUN chmod +x /action/entrypoint.py

ENTRYPOINT ["/usr/local/bin/python", "/action/entrypoint.py"]
