"""
datacite.py — Retrieve DataCite metadata for a BIL dataset.

Queries the DataCite REST API (https://api.datacite.org) using the BIL
DOI prefix (10.35077) and the dataset ID to return full DOI metadata,
including title, authors, publication date, and citation count.

Usage:
    python examples/datacite.py
"""

import brainimagelibrary as brainzzz
from pprint import pprint

dataset_id = "act-bag"

print(f"Fetching DataCite metadata for dataset: {dataset_id}")
metadata = brainzzz.get_metadata(dataset_id=dataset_id)

if metadata is None:
    print(f"No DataCite metadata found for dataset '{dataset_id}'.")
else:
    pprint(metadata)
