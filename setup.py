from setuptools import setup, find_packages

setup(
    name="waters-data-tool",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.20.0",
        "pandas>=1.3.0",
        "matplotlib>=3.4.0",
        "seaborn>=0.11.0",
        "rdkit>=2022.3.1",
        "PySide6>=6.4.0",
        "pytest>=7.0.0",
        "pymzml>=2.5.0",
        "pymsfilereader>=1.0.0",
        "psutil>=5.8.0",
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="A tool for processing Waters LC-MS data",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    python_requires=">=3.8",
) 