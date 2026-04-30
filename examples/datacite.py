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
datacite.py — Retrieve DataCite metadata for a BIL dataset.

Queries the DataCite REST API (https://api.datacite.org) using the BIL
DOI prefix (10.35077) and the dataset ID to return full DOI metadata,
including title, authors, publication date, and citation count.

Usage:
    python examples/datacite.py
"""

import brainimagelibrary as bil
from pprint import pprint

dataset_id = "act-bag"

print(f"Fetching DataCite metadata for dataset: {dataset_id}")
metadata = bil.get_datacite_metadata(bildid=dataset_id)

if metadata is None:
    print(f"No DataCite record found for dataset '{dataset_id}'. DOI may not be registered.")
else:
    pprint(metadata)
