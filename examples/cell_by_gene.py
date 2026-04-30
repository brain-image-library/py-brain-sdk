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
cell_by_genes.py — Find all BIL datasets that contain cell-by-gene files.

Fetches all known bildids via the query API, then checks each dataset's
inventory in parallel using pandarallel (16 workers) to determine which
datasets have a ``cell_by_gene`` file type.

Usage:
    python examples/cell_by_genes.py
"""

import pandas as pd
from pandarallel import pandarallel

import brainimagelibrary.inventory as inventory
from brainimagelibrary.reports import get_all_bildids

pandarallel.initialize(nb_workers=16, progress_bar=True)

print("Fetching all bildids...")
bildids = get_all_bildids()
if not bildids:
    print("No bildids found.")
    raise SystemExit(1)

print(f"Found {len(bildids)} datasets. Checking for cell_by_gene files...")

df = pd.DataFrame({"bildid": bildids})

df["has_cell_by_gene"] = df["bildid"].parallel_apply(
    lambda bildid: inventory.has(bildid=bildid, option="cell_by_gene")
)

matches = df[df["has_cell_by_gene"].fillna(False).astype(bool)]
print(f"\nDatasets with cell_by_gene files ({len(matches)} total):")
for bildid in sorted(matches["bildid"]):
    print(f"  {bildid}")

manifest_path = "cell_by_gene.manifest"
with open(manifest_path, "w") as f:
    for bildid in sorted(matches["bildid"]):
        f.write(bildid + "\n")
print(f"\nResults saved to {manifest_path}")

tsv_path = "cell_by_gene.tsv"
matches.to_csv(tsv_path, sep="\t", index=False)
print(f"Results saved to {tsv_path}")
