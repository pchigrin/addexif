from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="addexif",
    version="0.1.0",
    author="Pavel Chigrin",
    author_email="pchigrin@gmail.com",
    description="Console utility for managing EXIF metadata in JPEG images",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pchigrin/addexif",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Console Scripts",
    ],
    python_requires=">=3.10",
    install_requires=[
        "Pillow>=10.0.0",
        "piexif>=1.1.3",
        "PyYAML>=6.0",
        "python-dateutil>=2.8.0",
    ],
    entry_points={
        "console_scripts": [
            "addexif=addexif.cli:main",
        ],
    },
)
