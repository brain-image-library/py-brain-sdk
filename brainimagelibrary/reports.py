from .retrieve import *
from tqdm import tqdm
from pathlib import Path
from datetime import datetime
import pandas as pd


def __get_did(dataset_id):
    """
    Retrieves detailed metadata for a dataset by its ID.

    Args:
        dataset_id (str): The unique identifier of the dataset.

    Returns:
        dict: A dictionary containing the dataset metadata, including:
            - `metadata_version`: Version of the metadata.
            - `bildid`: The dataset ID.
            - `bildate`: The submission date of the dataset.
            - `contributor`: Name of the primary contributor.
            - `affiliation`: Affiliation of the primary contributor.
            - `award_number`: Award number associated with the funding.
            - `project`: Name of the project.
            - `consortium`: Name of the consortium.
            - `bildirectory`: Directory path of the dataset.
            - `generalmodality`: General modality of the dataset.
            - `technique`: Technique used in the dataset.
            - `species`: Species in the dataset.
            - `taxonomy`: NCBI taxonomy ID of the species.
            - `genotype`: Genotype information of the specimen.
            - `samplelocalid`: Local ID of the specimen sample.
    """

    def safe_get(data, keys, default=None):
        """Helper function to safely retrieve nested dictionary values."""
        try:
            for key in keys:
                data = data[key]
            return data
        except (KeyError, IndexError, TypeError):
            return default

    metadata = by_id(bildid=dataset_id)
    metadata = metadata.get("retjson", [{}])[0]

    return {
        "metadata_version": safe_get(metadata, ["Submission", "metadata"]),
        "bildid": dataset_id,
        "bildate": safe_get(metadata, ["Submission", "bildate"]),
        "contributor": safe_get(metadata, ["Contributors", 0, "contributorname"]),
        "affiliation": safe_get(metadata, ["Contributors", 0, "affiliation"]),
        "award_number": safe_get(metadata, ["Funders", 0, "award_number"]),
        "project": safe_get(metadata, ["Submission", "project"]),
        "consortium": safe_get(metadata, ["Submission", "consortium"]),
        "bildirectory": safe_get(metadata, ["Dataset", 0, "bildirectory"]),
        "generalmodality": safe_get(metadata, ["Dataset", 0, "generalmodality"]),
        "technique": safe_get(metadata, ["Dataset", 0, "technique"]),
        "species": safe_get(metadata, ["Specimen", 0, "species"]),
        "taxonomy": safe_get(metadata, ["Specimen", 0, "ncbitaxonomy"]),
        "genotype": safe_get(metadata, ["Specimen", 0, "genotype"]),
        "samplelocalid": safe_get(metadata, ["Specimen", 0, "samplelocalid"]),
    }


def daily(option="simple", overwrite=False):
    """
    Retrieves the daily inventory report from the Brain Image Library.

    Depending on the `option` parameter, this function downloads either the
    simple daily inventory or the detailed daily report. If the download fails,
    it returns a locally created or empty DataFrame.

    Args:
        option (str, optional): The type of daily report to fetch. Options are:
            - `"simple"`: Fetches the simple daily inventory (default).
            - `"detailed"`: Fetches the detailed daily report.

    Returns:
        pd.DataFrame: A DataFrame containing the inventory data. Returns an
                      empty DataFrame if the download fails.
    """

    def fetch_and_load_csv(url, file_path,overwrite=False):
        """Helper function to download and load a TSV file as a DataFrame."""
        try:
            if overwrite:
                return None
            response = requests.get(url)
            if response.status_code == 200:
                with open(file_path, "wb") as file:
                    file.write(response.content)
                return pd.read_csv(file_path, sep="\t")
            else:
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error fetching URL {url}: {e}")
            return None

    if option == "simple":
        base_url = "https://download.brainimagelibrary.org/inventory/daily"
        today = datetime.today().strftime("%Y%m%d")
        url = f"{base_url}/{today}.tsv"
        file_path = f"/tmp/{today}.tsv"
        df = fetch_and_load_csv(url, file_path, overwrite)
        if df is None:
            print("Failed to fetch simple daily report. Creating local report...")
            df = __create_daily_report(overwrite)
    elif option == "detailed":
        url = "https://download.brainimagelibrary.org/inventory/daily/reports/today.tsv"
        file_path = "/tmp/today.tsv"
        df = fetch_and_load_csv(url, file_path, overwrite)
        if df is None:
            print("Failed to fetch detailed daily report. Returning empty DataFrame...")
            df = pd.DataFrame()
    else:
        raise ValueError(f"Invalid option '{option}'. Choose 'simple' or 'detailed'.")

    return df


def __create_daily_report(overwrite=False):
    """
    Creates or retrieves the daily inventory report.

    This function checks for the existence of a daily inventory report in
    predefined directories. If the report exists, it is loaded and returned
    as a DataFrame. If not, the function generates the report by processing
    datasets in metadata versions 1.0 and 2.0, saves it to disk, and returns
    it as a DataFrame.

    Returns:
        pd.DataFrame: The daily inventory report as a DataFrame.

    Side Effects:
        - Reads daily report files from disk if they exist.
        - Creates and saves the daily report to disk if it does not exist.
        - Saves the report to the BRAIN filesystem if available.

    Raises:
        FileNotFoundError: If directories or files are missing in non-standard cases.
    """
    directory = "/bil/data/inventory/daily"
    today = datetime.today().strftime("%Y%m%d")
    output_filename = f"{directory}/{today}.tsv"

    if overwrite == False and Path(output_filename).exists():
        print(f"Daily report {output_filename} found on disk.")
        df = pd.read_csv(output_filename, sep="\t")
        return df

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

    # save to BRAIN file system
    directory = "/bil/data/inventory/daily"
    if Path(directory).exists():
        output_filename = f"{directory}/{today}.tsv"
        df.to_csv(output_filename, sep="\t", index=False)

    return df
