"""
citations.py — Retrieve citation counts for a BIL dataset.

Queries DataCite, OpenCitations, Crossref, and Semantic Scholar in parallel
and returns the number of times the dataset has been cited in each source.

Usage:
    python examples/citations.py
"""

import brainimagelibrary as bil
from pprint import pprint

dataset_id = "act-bag"

print(f"Fetching citation counts for dataset: {dataset_id}")
citations = bil.get_number_of_citations(bildid=dataset_id)

if all(v is None for v in citations.values()):
    print(f"No DOI registered for dataset '{dataset_id}'.")
else:
    pprint(citations)
