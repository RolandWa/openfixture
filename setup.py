#!/usr/bin/env python3
"""Setup script for OpenFixture."""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_file = Path(__file__).parent / "README.md"
if readme_file.exists():
    with open(readme_file, "r", encoding="utf-8") as f:
        long_description = f.read()
else:
    long_description = "Automated laser-cuttable PCB test fixture generation for KiCAD"

setup(
    name="openfixture",
    version="1.0.0",
    author="Roland Wa",
    author_email="gitrepository Team",
    description="Automated laser-cuttable PCB test fixture generation for KiCAD",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/RolandWa/openfixture",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Manufacturing",
        "License :: OSI Approved :: Creative Commons Attribution-ShareAlike 4.0",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language:: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)",
    ],
    python_requires=">=3.8",
    install_requires=[
        # KiCAD provides pcbnew, no external deps required for core functionality
    ],
    extras_require={
        "toml": [
            "tomli>=1.2.0; python_version<'3.11'",  # TOML support for Python < 3.11
        ],
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.0.0",
            "black>=21.0.0",
            "flake8>=3.8.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "genfixture=openfixture_support.GenFixture:main",
        ],
    },
    include_package_data=True,
    package_data={
        "openfixture_support": [
            "*.scad",
            "*.dxf",
            "*.toml",
            "*.bat",
            "*.sh",
        ],
    },
    zip_safe=False,
)
