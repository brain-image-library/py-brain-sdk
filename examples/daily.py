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

import brainimagelibrary as brainzzz

df = brainzzz.reports.daily()

if df is None or df.empty:
    print("Daily report could not be retrieved.")
else:
    print(df.to_markdown(index=False))
