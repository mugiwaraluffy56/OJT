from setuptools import setup, find_packages

setup(
    name="license-detect",
    version="3.0.0",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "license-detect = license_detector.cli:main",
        ],
    },
    install_requires=[
        "transformers",
        "torch",
        "accelerate>=0.26.0",
    ],
)
