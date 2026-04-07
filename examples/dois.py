import brainimagelibrary as bil
import pandas as pd
from pandarallel import pandarallel
from tqdm import tqdm

pandarallel.initialize(progress_bar=True)
tqdm.pandas()

bildids = bil.retrieve.get_all_bildids()
df = pd.DataFrame(bildids, columns=["bildid"])

df["DOIS"] = df["bildid"].parallel_apply(bil.dois.get_number_of_citations)

df["total"] = df["DOIS"].progress_apply(
    lambda d: sum(v if v is not None else 0 for v in d.values()) if isinstance(d, dict) else 0
)

df = df[df["total"] > 0].sort_values("total", ascending=False).reset_index(drop=True)

print(df)

df.to_csv("dois.tsv", sep="\t", index=False)
