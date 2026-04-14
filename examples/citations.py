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
citations.py — Retrieve citation counts for a BIL dataset.

Queries DataCite, OpenCitations, Crossref, and Semantic Scholar in parallel
and returns the number of times the dataset has been cited in each source.

Usage:
    python examples/citations.py
"""

import brainimagelibrary as bil
from pprint import pprint

dataset_id = "act-bag"

print(f"Fetching citation counts for dataset: {dataset_id}")
citations = bil.get_number_of_citations(bildid=dataset_id)

if all(v is None for v in citations.values()):
    print(f"No DOI registered for dataset '{dataset_id}'.")
else:
    pprint(citations)
