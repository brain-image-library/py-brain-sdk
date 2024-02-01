from setuptools import setup, find_packages

setup(
    name="brainimagelibrarysdk",
    version="1.0b0",  # Beta release version
    description="Brain Image Library SDK",
    long_description="Brain Image Library SDK is a Python library for interacting with the Brain Image Library APIs and services.",
    long_description_content_type="text/markdown",
    url="https://github.com/brain-image-library/py-brain-sdk",
    author="Ivan Cao-Berg",
    author_email="icaoberg@psc.edu",
    license="GPLv3",
    packages=find_packages(),
    install_requires=[
        "pandas>=2.2.0",
        "requests==2.26.0",
        "setuptools==68.2.2",
        "tqdm==4.66.1",
        "humanize",
    ],
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    project_urls={
        "Documentation": "https://github.com/brain-image-library/py-brain-sdk/docs",
        "Source": "https://github.com/brain-image-library/py-brain-sdk",
        "Tracker": "https://github.com/brain-image-library/py-brain-sdk/issues",
    },
)
