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
