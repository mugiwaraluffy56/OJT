from setuptools import setup, find_packages

setup(
    name="license-detect",
    version="0.1.0",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "license-detect = src.cli.main:main",
        ],
    },
    install_requires=[
        "scikit-learn",
    ],
)
