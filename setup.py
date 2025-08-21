from setuptools import setup

setup(
    name="brainimagelibrary",
    version="0.0.3",
    description="Brain Image Library API",
    url="https://github.com/brain-image-library/",
    author="Ivan Cao-Berg",
    author_email="icaoberg@psc.edu",
    install_requires=[
        "pandas",
        "requests",
        "tabulate",
        "python-magic",
        "tqdm",
        "scholarly",
        "humanize",
    ],
    packages=["brainimagelibrary"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
)
