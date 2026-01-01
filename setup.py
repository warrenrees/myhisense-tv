#!/usr/bin/env python3
"""Setup script for hisense_tv package."""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="myhisense-tv",
    version="1.5.9",
    author="Warren Rees",
    author_email="",
    description="Control Hisense/Vidaa Smart TVs via MQTT",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/warrenrees/myhisense-tv",
    project_urls={
        "Bug Tracker": "https://github.com/warrenrees/myhisense-tv/issues",
        "Documentation": "https://github.com/warrenrees/myhisense-tv#readme",
        "Source Code": "https://github.com/warrenrees/myhisense-tv",
        "Changelog": "https://github.com/warrenrees/myhisense-tv/blob/main/CHANGELOG.md",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Home Automation",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="hisense myhisense vidaa tv mqtt smart-tv home-automation",
    install_requires=[
        "paho-mqtt>=1.6.0",
        "pyyaml>=6.0",
    ],
    entry_points={
        "console_scripts": [
            "tv=hisense_tv.cli:main",
            "myhisense-tv=hisense_tv.cli:main",
        ],
    },
    python_requires=">=3.8",
)
