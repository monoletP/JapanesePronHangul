#!/usr/bin/env python3
"""
Setup script for Japanese to Hangul Converter
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="japanese-hangul-converter",
    version="1.0.0",
    author="monoletP",
    description="일본어 가사를 한글로 변환하는 웹 애플리케이션",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/monoletP/RomajiConverter.WinUI",
    py_modules=["japanese_pron", "hangul_helper", "app"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: OS Independent",
        "Topic :: Text Processing :: Linguistic",
        "Natural Language :: Japanese",
        "Framework :: FastAPI",
    ],
    python_requires=">=3.7",
    install_requires=[
        "fastapi>=0.109.0",
        "uvicorn[standard]>=0.27.0",
        "jinja2>=3.1.3",
        "python-multipart>=0.0.6",
        "mecab-python3>=1.0.6",
        "unidic-lite>=1.0.8",
    ],
    entry_points={
        "console_scripts": [
            "japanese-hangul=japanese_pron:main",
        ],
    },
)
