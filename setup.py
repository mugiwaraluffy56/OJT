from setuptools import setup, find_packages

setup(
    name="license-detect",
    version="4.0.0",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "license-detect = license_detector.cli:main",
        ],
    },
    install_requires=[
        "transformers>=4.20.0",
        "torch",
        "accelerate>=0.26.0",
        "evaluate",
        "scikit-learn",
    ],
)
