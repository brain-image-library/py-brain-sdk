from pathlib import Path
from setuptools import setup, find_packages

long_description = Path("README.md").read_text(encoding="utf-8")

setup(
    name="brainimagelibrary",
    version="0.0.11",
    description="Brain Image Library API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/brain-image-library/py-brain-sdk",
    project_urls={
        "Bug Tracker": "https://github.com/brain-image-library/py-brain-sdk/issues",
        "Documentation": "https://www.brainimagelibrary.org",
    },
    author="Ivan Cao-Berg",
    author_email="icaoberg@psc.edu",
    license="GPL-3.0",
    keywords=["neuroscience", "brain", "microscopy", "image", "library"],
    python_requires=">=3.9",
    install_requires=[
        "pandas>=1.3",
        "requests>=2.25",
        "tabulate>=0.8",
        "python-magic>=0.4",
        "tqdm>=4.60",
        "scholarly>=1.7",
        "humanize>=3.0",
    ],
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
)
