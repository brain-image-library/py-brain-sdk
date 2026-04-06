"""
summary.py — Print a high-level summary of the BIL daily inventory.

Fetches today's inventory report and prints aggregate statistics:
    - Total number of datasets
    - Total number of files
    - Unique contributor, affiliation, and species counts
    - Metadata version breakdown

Usage:
    python examples/summary.py
"""

import brainimagelibrary as brainzzz

print("Fetching daily BIL summary...")
result = brainzzz.summary.daily()

if result is None:
    print("Summary not available.")
else:
    print(f"Number of datasets          : {result['number_of_datasets']}")
    print(f"Total files                 : {result['number_of_files']}")
    print(f"Unique contributors         : {result['number_of_unique_contributors']}")
    print(f"Unique affiliations         : {result['number_of_unique_affiliations']}")
    print(f"Unique species              : {result['number_of_unique_species']}")
    print()
    print("=== Metadata Versions ===")
    print(result["metadata_version"].to_string())
