from .retrieve import *
import uuid
import requests
import pandas as pd


def summary(dataset_id=None):
    metadata = get(dataset_id=dataset_id)
    manifest = metadata["manifest"]
    df = pd.DataFrame(manifest)

    data = {}
    data["pretty_size"] = metadata["pretty_size"]
    data["size"] = metadata["size"]
    data["number_of_files"] = metadata["number_of_files"]

    grouped_data = df.groupby("extension")["size"].sum()
    data["files"] = {
        "frequencies": metadata["frequencies"],
        "types": metadata["file_types"],
        "sizes": grouped_data.to_dict(),
    }

    return data


def __generate_dataset_uuid(directory):
    if directory[-1] == "/":
        directory = directory[:-1]

    return str(uuid.uuid5(uuid.NAMESPACE_DNS, directory))


def get(dataset_id=None):
    metadata = by_id(dataset_id)
    directory = metadata["retjson"][0]["Dataset"][0]["bildirectory"]

    filename = f"{__generate_dataset_uuid(directory)}.json"
    url = f"https://download.brainimagelibrary.org/inventory/{filename}"

    try:
        response = requests.get(url)

        response = response.json()
        return response
    except requests.exceptions.RequestException as e:
        print(f"Error making API request: {e}")
        return None
