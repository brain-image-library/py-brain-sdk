"""
citations.py — Retrieve citation counts for a BIL dataset.

Queries DataCite and Google Scholar to return the number of times the
dataset has been cited in the literature.

Usage:
    python examples/citations.py
"""

import brainimagelibrary as brainzzz
from pprint import pprint

dataset_id = "act-bag"

print(f"Fetching citation counts for dataset: {dataset_id}")
citations = brainzzz.get_number_of_citations(dataset_id=dataset_id)

if citations is None:
    print(f"No citation data found for dataset '{dataset_id}'.")
else:
    pprint(citations)
