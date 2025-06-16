#!/usr/bin/env python3
"""
Setup script for AugmentCode Free
Fallback setup for environments where pyproject.toml doesn't work
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

setup(
    name="augment-free",
    version="0.2.0",
    description="Free AugmentCode - A tool for cleaning AugmentCode related data with modern GUI (Modified by UntaDotMy)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="vagmr, UntaDotMy",
    author_email="42847931+UntaDotMy@users.noreply.github.com",
    url="https://github.com/UntaDotMy/Augment-Code-free",
    project_urls={
        "Homepage": "https://github.com/UntaDotMy/Augment-Code-free",
        "Repository": "https://github.com/UntaDotMy/Augment-Code-free",
        "Issues": "https://github.com/UntaDotMy/Augment-Code-free/issues",
        "Original": "https://github.com/vagmr/Augment-Code-free",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    package_data={
        "augment_free": ["web/**/*"],
    },
    include_package_data=True,
    python_requires=">=3.10",
    install_requires=[
        "pywebview>=5.0.0",
        "jinja2>=3.1.0",
    ],
    extras_require={
        "dev": [
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
        ],
        "build": [
            "pyinstaller>=6.0.0",
            "pillow>=10.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "augment-free=augment_free.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Tools",
        "Topic :: Utilities",
    ],
    license="MIT",
    keywords="augmentcode, vscode, jetbrains, ide, cleaner, tool",
)
