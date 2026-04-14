# Copyright (C) 2026  Ivan Cao-Berg
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
summary.py — Print a high-level summary of the BIL daily inventory.

Demonstrates two summary utilities:

1. summary.daily()  — Fetch today's inventory and print aggregate statistics.
2. summary.load()   — Load the inventory report for a specific date (YYYYMMDD).

Usage:
    python examples/summary.py
"""

import brainimagelibrary as bil

# --- Example 1: today's summary -------------------------------------------

print("Fetching daily BIL summary...")
result = bil.summary.daily()

print(f"Number of datasets          : {result['number_of_datasets']}")
print(f"Total files                 : {result['number_of_files']}")
print(f"Unique contributors         : {result['number_of_unique_contributors']}")
print(f"Unique affiliations         : {result['number_of_unique_affiliations']}")
print(f"Unique species              : {result['number_of_unique_species']}")
print()
print("=== Metadata Versions ===")
print(result["metadata_version"].to_string())

# --- Example 2: load inventory for a specific date -------------------------

print()
date = "20240101"
print(f"Loading inventory report for {date}...")
df = bil.summary.load(date)

if df is not None:
    print(f"Loaded {len(df)} records.")
    print(df.head())
else:
    print(f"No data available for {date}.")
