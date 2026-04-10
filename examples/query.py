"""
query.py — Query Brain Image Library datasets using various lookup methods.

Demonstrates how to use the query module to retrieve dataset metadata by
BIL ID, directory path, download URL, affiliation, metadata version, and
free-text search.

Usage:
    python examples/query.py
"""

import brainimagelibrary.query as query
from pprint import pprint

# By BIL ID
print("=== by_id ===")
result = query.by_id(bildid="act-bag")
pprint(result)

# By directory path
print("\n=== by_directory ===")
result = query.by_directory(directory="/bil/data/2019/02/13/H19.28.012.MITU.01.05")
pprint(result)

# By download URL
print("\n=== by_url ===")
result = query.by_url("https://download.brainimagelibrary.org/2019/02/13/H19.28.012.MITU.01.05")
pprint(result)

# By affiliation
print("\n=== by_affiliation ===")
result = query.by_affiliation("Carnegie Mellon University")
pprint(result)

# By metadata version
print("\n=== by_version ===")
ids = query.by_version(version="2.0")
print(f"Found {len(ids)} dataset IDs")

# Full-text search
print("\n=== by_text ===")
result = query.by_text("mouse cortex")
pprint(result)
