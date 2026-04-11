"""
datecite.py — Fetch citation counts for all BIL datasets.

Iterates over every dataset in the Brain Image Library, queries citation
counts from DataCite, OpenCitations, Crossref, and Semantic Scholar in
parallel, then writes a TSV of datasets that have at least one citation.

Usage:
    python examples/datecite.py
"""

import brainimagelibrary as bil
import pandas as pd
from pandarallel import pandarallel
from tqdm import tqdm

pandarallel.initialize(progress_bar=True)
tqdm.pandas()

bildids = bil.get_all_bildids()
df = pd.DataFrame(bildids, columns=["bildid"])

df["citations"] = df["bildid"].parallel_apply(bil.datecite.get_number_of_citations)

df["total"] = df["citations"].progress_apply(
    lambda d: sum(v if v is not None else 0 for v in d.values()) if isinstance(d, dict) else 0
)

df = df[df["total"] > 0].sort_values("total", ascending=False).reset_index(drop=True)

print(df)

df.to_csv("datecite.tsv", sep="\t", index=False)
