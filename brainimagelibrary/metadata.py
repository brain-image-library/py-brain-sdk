import requests


def retrieve(dataset_id, params=None, headers=None):
    """
    Retrieves detailed metadata for a dataset using its ID.

    This function sends a GET request to the Brain Image Library API
    to fetch detailed metadata for the specified dataset.

    Args:
        dataset_id (str): The unique identifier for the dataset.
        params (dict, optional): Query parameters to include in the API request. Defaults to None.
        headers (dict, optional): HTTP headers to include in the API request. Defaults to None.

    Returns:
        dict: A dictionary containing the dataset metadata if the request is successful.

        dict: An empty dictionary if the API response indicates no entry was found.

        None: If the request fails or encounters an exception.

    Raises:
        requests.exceptions.RequestException: If an error occurs during the API request.
    """
    api_url = f"https://api.brainimagelibrary.org/retrieve?bildid={dataset_id}"

    try:
        response = requests.get(api_url, params=params, headers=headers)

        response = response.json()
        if (
            "message" in response.keys()
            and response["message"] == "GET failure, no entry found"
        ):
            return {}
        else:
            return response

    except requests.exceptions.RequestException as e:
        print(f"Error making API request: {e}")
        return None


def search(dataset_id, params=None, headers=None):
    """
    Searches for metadata of a dataset using its ID.

    This function sends a GET request to the Brain Image Library API
    to search for metadata associated with the specified dataset.

    Args:
        dataset_id (str): The unique identifier for the dataset.
        params (dict, optional): Query parameters to include in the API request. Defaults to None.
        headers (dict, optional): HTTP headers to include in the API request. Defaults to None.

    Returns:
        dict: A dictionary containing the dataset metadata if the request is successful.

        dict: An empty dictionary if the API response indicates no entry was found.

        None: If the request fails or encounters an exception.

    Raises:
        requests.exceptions.RequestException: If an error occurs during the API request.
    """
    api_url = f"https://api.brainimagelibrary.org/retrieve?bildid={dataset_id}"

    try:
        response = requests.get(api_url, params=params, headers=headers)

        response = response.json()
        if (
            "message" in response.keys()
            and response["message"] == "GET failure, no entry found"
        ):
            return {}
        else:
            return response

    except requests.exceptions.RequestException as e:
        print(f"Error making API request: {e}")
        return None
