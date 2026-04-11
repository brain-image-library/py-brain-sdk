"""
inventory.py — Retrieve the full file inventory for a BIL dataset.

Downloads and decompresses the per-dataset ``.json.gz`` inventory file from
``download.brainimagelibrary.org`` and prints the parsed contents, which
include the file manifest, sizes, types, and frequency counts.

Usage:
    python examples/inventory.py
"""

import brainimagelibrary as bil
from pprint import pprint

dataset_id = "act-bag"

print(f"Fetching inventory for dataset: {dataset_id}")
inventory = bil.inventory.get(bildid=dataset_id)

if inventory is None:
    print(f"Inventory not available for dataset '{dataset_id}'.")
else:
    # Print summary fields only — the manifest list can be very large
    summary = {k: v for k, v in inventory.items() if k != "manifest"}
    pprint(summary)
    print(f"manifest: [{len(inventory.get('manifest', []))} entries]")
