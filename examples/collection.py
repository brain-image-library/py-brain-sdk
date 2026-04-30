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
collection.py — List datasets belonging to a BIL collection.

Looks up a collection by its BIL ID, fetches its DataCite metadata, and
prints the dataset IDs and download URLs that belong to it.

Usage:
    python examples/collection.py
"""

import brainimagelibrary
from pprint import pprint

collection_id = "g.19"

if brainimagelibrary.datecite.collection.exists(bildid=collection_id):
    metadata = brainimagelibrary.datecite.collection.get(bildid=collection_id)
    datasets = brainimagelibrary.datecite.collection.get_datasets(bildid=collection_id)
    pprint(datasets)
else:
    print(f"No DOI registered for collection '{collection_id}'.")
