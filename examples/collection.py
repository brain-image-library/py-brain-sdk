"""
collection.py — List datasets belonging to a BIL collection.

Looks up a collection by its BIL ID, fetches its DataCite metadata, and
prints the dataset IDs and download URLs that belong to it.

Usage:
    python examples/collection.py
"""

import brainimagelibrary
from pprint import pprint

collection_id = "g.19"

if brainimagelibrary.datecite.collection.exists(bildid=collection_id):
    metadata = brainimagelibrary.datecite.collection.get(bildid=collection_id)
    datasets = brainimagelibrary.datecite.collection.get_datasets(bildid=collection_id)
    pprint(datasets)
else:
    print(f"No DOI registered for collection '{collection_id}'.")
