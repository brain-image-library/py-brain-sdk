from .retrieve import *
import uuid
import requests


def __generate_dataset_uuid(directory):
    if directory[-1] == "/":
        directory = directory[:-1]

    return str(uuid.uuid5(uuid.NAMESPACE_DNS, directory))


def get(bildid=None):
    metadata = by_id(bildid)
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
