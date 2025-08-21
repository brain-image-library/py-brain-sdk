from .retrieve import *
import uuid
import requests
import pandas as pd


def summary(dataset_id=None):
    """
    Summarizes dataset metadata.

    This function retrieves metadata for a dataset and computes summary
    statistics, including file sizes, counts, and types.

    Args:
        dataset_id (str, optional): The unique identifier of the dataset. Defaults to None.

    Returns:
        dict: A dictionary containing the following keys:
            - `pretty_size` (str): Human-readable size of the dataset.
            - `size` (int): Total size of the dataset in bytes.
            - `number_of_files` (int): Number of files in the dataset.
            - `files` (dict): Detailed file information, including:
                - `frequencies` (dict): Frequency of file extensions.
                - `types` (list): Types of files in the dataset.
                - `sizes` (dict): Size of files grouped by extension.
    """
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
    """
    Generates a UUID for a dataset based on its directory path.

    This function computes a consistent UUID for a dataset using the
    directory path as the seed. The UUID is generated using the UUIDv5
    algorithm with the DNS namespace.

    Args:
        directory (str): The absolute or relative path to the dataset directory.

    Returns:
        str: A string representation of the generated UUID.
    """
    if directory[-1] == "/":
        directory = directory[:-1]

    return str(uuid.uuid5(uuid.NAMESPACE_DNS, directory))


def get(dataset_id=None):
    """
    Retrieves metadata for a dataset by its ID.

    This function fetches metadata for a dataset from a remote server
    using its unique identifier. The metadata is retrieved as a JSON
    response from the Brain Image Library's API.

    Args:
        dataset_id (str, optional): The unique identifier for the dataset. Defaults to None.

    Returns:
        dict: A dictionary containing the dataset metadata if the request is successful.

        None: If the request fails or encounters an exception.

    Raises:
        requests.exceptions.RequestException: If an error occurs during the API request.
    """
    
    filename = f"{dataset_id}.json"
    url = f"https://download.brainimagelibrary.org/inventory/datasets/{filename}"

    try:
        response = requests.get(url)

        response = response.json()
        return response
    except requests.exceptions.RequestException as e:
        print(f"Error making API request: {e}")
        return None
