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
daily.py — Fetch the BIL daily inventory report.

Downloads today's inventory summary for all datasets in the Brain Image
Library and prints it as a Markdown table.  Falls back to building the
report locally when the remote file is unavailable.

Options passed to ``daily()``:
    "simple"   (default) — today's TSV from download.brainimagelibrary.org
    "detailed" — pre-built detailed report from the same host

Usage:
    python examples/daily.py
"""

import brainimagelibrary as bil

df = bil.reports.daily()

if df is None or df.empty:
    print("Daily report could not be retrieved.")
else:
    print(df.to_markdown(index=False))
