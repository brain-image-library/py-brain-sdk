import requests


def by_id(bildid=None, params=None, headers=None):
    """
    Retrieves metadata for a dataset by its Brain Image Library ID.

    This function sends a GET request to the Brain Image Library API to fetch
    metadata for a specified dataset using its unique `bildid`.

    Args:
        bildid (str, optional): The unique identifier for the dataset. If not provided,
            the function returns an empty dictionary.
        params (dict, optional): Query parameters to include in the API request. Defaults to None.
        headers (dict, optional): HTTP headers to include in the API request. Defaults to None.

    Returns:
        dict: The metadata for the dataset if the request is successful.
        dict: An empty dictionary if the dataset ID is invalid or not found.
        None: If the request fails or encounters an exception.

    Raises:
        requests.exceptions.RequestException: If an error occurs during the API request.

    Example:
        >>> from brainimagelibrary import retrieve
        >>> metadata = retrieve.by_id(bildid="act-bag")
        >>> print(type(metadata))
        <class 'dict'>
        >>> print("retjson" in metadata)
        True
    """
    if not bildid:
        return {}

    api_url = f"https://api.brainimagelibrary.org/retrieve?bildid={bildid}"

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


def by_directory(directory=None, params=None, headers=None):
    """
    Retrieves metadata for a dataset by its directory path.

    This function sends a GET request to the Brain Image Library API to fetch
    metadata for a specified dataset using its directory path.

    Args:
        directory (str, optional): The directory path of the dataset. If not provided,
            the function returns an empty dictionary.
        params (dict, optional): Query parameters to include in the API request. Defaults to None.
        headers (dict, optional): HTTP headers to include in the API request. Defaults to None.

    Returns:
        dict: The metadata for the dataset if the request is successful.
        dict: An empty dictionary if the directory path is invalid or not found.
        None: If the request fails or encounters an exception.

    Raises:
        requests.exceptions.RequestException: If an error occurs during the API request.

    Example:
        >>> from brainimagelibrary import retrieve
        >>> metadata = retrieve.by_directory(directory="/bil/data/2019/02/13/H19.28.012.MITU.01.05")
        >>> print(type(metadata))
        <class 'dict'>
        >>> print("retjson" in metadata)
        True
    """
    if not directory:
        return {}

    api_url = (
        f"https://api.brainimagelibrary.org/query/dataset?bildirectory={directory}"
    )

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


def by_url(url=None):
    if not url:
        return {}
    directory = url.replace("https://download.brainimagelibrary.org", "/bil/data")
    return by_directory(directory=directory)


def by_version(version="2.0"):
    """
    Retrieves dataset IDs based on metadata version.

    This function sends a GET request to the Brain Image Library API to fetch
    dataset IDs associated with a specific metadata version.

    Args:
        version (str, optional): The metadata version to query. Defaults to "2.0".

    Returns:
        list: A list of dataset IDs (`bildids`) if the request is successful.
        dict: An empty dictionary if no datasets are found for the specified version.
        None: If the request fails or encounters an exception.

    Raises:
        requests.exceptions.RequestException: If an error occurs during the API request.

    Example:
        >>> from brainimagelibrary import retrieve
        >>> ids = retrieve.by_version(version="1.0")
        >>> print(type(ids))
        <class 'list'>
        >>> print(len(ids) > 0)
        True
    """
    api_url = f"https://api.brainimagelibrary.org/query/submission?metadata={version}"

    try:
        response = requests.get(api_url)
        response = response.json()
        if (
            "message" in response.keys()
            and response["message"] == "GET failure, no entry found"
        ):
            return {}
        else:
            return response["bildids"]

    except requests.exceptions.RequestException as e:
        print(f"Error making API request: {e}")
        return None


def get_all_bildids():
    """
    Retrieves all dataset IDs from the Brain Image Library.

    Fetches dataset IDs for both metadata version 1.0 and 2.0, then returns
    the v2.0 list. The v1.0 list is fetched but currently unused.

    Returns:
        list: A list of dataset IDs (``bildids``) from metadata version 2.0.
        None: If the underlying API request fails.

    Example:
        >>> from brainimagelibrary import retrieve
        >>> ids = retrieve.get_all_bildids()
        >>> print(type(ids))
        <class 'list'>
        >>> print(len(ids) > 0)
        True
    """
    v2 = by_version(version="2.0")
    v1 = by_version(version="1.0")

    return v2
