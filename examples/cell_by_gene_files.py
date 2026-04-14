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
cell_by_gene_files.py — Extract full paths of cell-by-gene files for each BIL dataset.

Reads bildids from cell_by_gene.manifest, fetches each dataset's inventory in
parallel (16 workers), and collects all manifest entries where is_cell_by_gene
is True. Saves a TSV with columns bildid and fullpath to cell_by_gene.files.tsv.

Usage:
    python examples/cell_by_gene_files.py
"""

import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

import brainimagelibrary.inventory as inventory

MANIFEST = "/Users/icaoberg/Desktop/py-brain-sdk/examples/cell_by_gene.manifest"
OUTPUT = "/Users/icaoberg/Desktop/py-brain-sdk/examples/cell_by_gene.files.tsv"
N_WORKERS = 16


def get_cell_by_gene_files(bildid: str) -> list[tuple[str, str]]:
    """Return (bildid, fullpath) pairs for all is_cell_by_gene entries."""
    data = inventory.get(bildid=bildid)
    if data is None:
        return []
    return [
        (bildid, entry["fullpath"])
        for entry in data.get("manifest", [])
        if entry.get("is_cell_by_gene") is True and entry.get("fullpath")
    ]


with open(MANIFEST) as f:
    bildids = [line.strip() for line in f if line.strip()]

print(f"Processing {len(bildids)} datasets with {N_WORKERS} workers...")

rows = []
with ThreadPoolExecutor(max_workers=N_WORKERS) as executor:
    futures = {executor.submit(get_cell_by_gene_files, bid): bid for bid in bildids}
    with tqdm(total=len(futures), unit="dataset") as pbar:
        for future in as_completed(futures):
            rows.extend(future.result())
            pbar.update(1)

df = pd.DataFrame(rows, columns=["bildid", "fullpath"])
df.sort_values(["bildid", "fullpath"], inplace=True)
df.to_csv(OUTPUT, sep="\t", index=False)
print(f"Saved {len(df)} file entries to {OUTPUT}")
