"""
summary.py — Print a high-level summary of a BIL dataset's inventory.

Fetches the dataset inventory and computes aggregate statistics:
    - Human-readable total size
    - Total file count
    - File-type frequencies and per-extension size breakdown

Usage:
    python examples/summary.py
"""

import brainimagelibrary as brainzzz
from pprint import pprint

dataset_id = "act-bag"

print(f"Fetching inventory summary for dataset: {dataset_id}")
result = brainzzz.inventory.summary(dataset_id=dataset_id)

if result is None:
    print(f"Summary not available for dataset '{dataset_id}'.")
else:
    pprint(result)
