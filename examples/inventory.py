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
