from .retrieve import *
from tqdm import tqdm
from pathlib import Path
from datetime import datetime
import pandas as pd


def __get_did(bildid):
    metadata = by_id(bildid=bildid)
    metadata = metadata["retjson"][0]

    data = {}
    data["metadata_version"] = metadata["Submission"]["metadata"]
    data["bildid"] = bildid
    data["bildate"] = metadata["Submission"]["bildate"]

    try:
        data["contributor"] = metadata["Contributors"][0]["contributorname"]
    except:
        data["contributor"] = None

    try:
        data["affiliation"] = metadata["Contributors"][0]["affiliation"]
    except:
        data["affiliation"] = None

    try:
        data["award_number"] = metadata["Funders"][0]["award_number"]
    except:
        data["award_number"] = None

    try:
        data["project"] = metadata["Submission"]["project"]
    except:
        data["project"] = None

    try:
        data["consortium"] = metadata["Submission"]["consortium"]
    except:
        data["consortium"] = None

    try:
        data["bildirectory"] = metadata["Dataset"][0]["bildirectory"]
    except:
        data["bildirectory"] = None

    try:
        data["generalmodality"] = metadata["Dataset"][0]["generalmodality"]
    except:
        data["generalmodality"] = None

    try:
        data["technique"] = metadata["Dataset"][0]["technique"]
    except:
        data["technique"] = None

    try:
        data["species"] = metadata["Specimen"][0]["species"]
    except:
        data["species"] = None

    try:
        data["taxonomy"] = metadata["Specimen"][0]["ncbitaxonomy"]
    except:
        data["taxonomy"] = None

    try:
        data["genotype"] = metadata["Specimen"][0]["genotype"]
    except:
        data["genotype"] = None

    try:
        data["samplelocalid"] = metadata["Specimen"][0]["samplelocalid"]
    except:
        data["samplelocalid"] = None

    return data


def daily():
    df = pd.DataFrame()
    return df


def __create_daily_report():
    directory = "reports"
    today = datetime.today().strftime("%Y%m%d")
    output_filename = f"{directory}/{today}.tsv"

    if Path(output_filename).exists():
        print(f"Daily report {output_filename} found on disk.")
        df = pd.read_csv(output_filename, sep="\t")
        return df

    data = []

    print(f"Processing datasets in metadata version 1.0")
    v1 = by_version(version="1.0")
    for dataset in tqdm(v1):
        data.append(__get_did(dataset))

    print(f"Processing datasets in metadata version 2.0")
    v1 = by_version(version="2.0")
    for dataset in tqdm(v1):
        data.append(__get_did(dataset))

    df = pd.DataFrame(data)

    directory = "reports"
    if not Path(directory).exists():
        Path(directory).mkdir()

    today = datetime.today().strftime("%Y%m%d")
    output_filename = f"{directory}/{today}.tsv"

    if not Path(directory).exists():
        Path(directory).mkdir()
    df.to_csv(output_filename, sep="\t", index=False)

    return df
