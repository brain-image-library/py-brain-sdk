import requests


def by_affiliation(affiliation, params=None, headers=None):
    """
    Retrieves datasets associated with a contributor's affiliation.

    Queries the Brain Image Library API for datasets whose contributors
    belong to the specified affiliation.

    Args:
        affiliation (str): The affiliation name to search for (e.g. a university
            or research institute).
        params (dict, optional): Additional query parameters to include in the
            API request. Defaults to None.
        headers (dict, optional): HTTP headers to include in the API request.
            Defaults to None.

    Returns:
        dict: The API response containing matching contributor/dataset records.
        dict: An empty dictionary if no records are found for the affiliation.
        None: If the request fails or encounters an exception.

    Raises:
        requests.exceptions.RequestException: If an error occurs during the
            API request.

    Example:
        >>> from brainimagelibrary import metadata
        >>> results = metadata.by_affiliation("Carnegie Mellon University")
        >>> print(type(results))
        <class 'dict'>
        >>> print(len(results) > 0)
        True
    """
    api_url = f"https://api.brainimagelibrary.org/query/contributors?affiliation={affiliation}"

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


def retrieve(bildid, params=None, headers=None):
    """
    Retrieves metadata for a dataset by its Brain Image Library ID.

    Sends a GET request to the Brain Image Library API to fetch metadata
    for the specified dataset.

    Args:
        bildid (str): The unique Brain Image Library identifier for the
            dataset (e.g. ``"act-bag"``).
        params (dict, optional): Additional query parameters to include in the
            API request. Defaults to None.
        headers (dict, optional): HTTP headers to include in the API request.
            Defaults to None.

    Returns:
        dict: The metadata for the dataset if the request is successful.
        dict: An empty dictionary if the dataset is not found.
        None: If the request fails or encounters an exception.

    Raises:
        requests.exceptions.RequestException: If an error occurs during the
            API request.

    Example:
        >>> from brainimagelibrary import metadata
        >>> data = metadata.retrieve("act-bag")
        >>> print(type(data))
        <class 'dict'>
        >>> print("retjson" in data)
        True
    """
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


def query(query_string, params=None, headers=None):
    """
    Performs a full-text search across Brain Image Library datasets.

    Sends a GET request to the Brain Image Library full-text search endpoint
    and returns all matching records.

    Args:
        query_string (str): The search string to query against the BIL index.
        params (dict, optional): Additional query parameters to include in the
            API request. Defaults to None.
        headers (dict, optional): HTTP headers to include in the API request.
            Defaults to None.

    Returns:
        dict: The API response containing matching dataset records.
        dict: An empty dictionary if no results are found.
        None: If the request fails or encounters an exception.

    Raises:
        requests.exceptions.RequestException: If an error occurs during the
            API request.

    Example:
        >>> from brainimagelibrary import metadata
        >>> results = metadata.query("mouse cortex")
        >>> print(type(results))
        <class 'dict'>
        >>> print(len(results) > 0)
        True
    """
    api_url = f"https://api.brainimagelibrary.org/query/fulltext?text={query_string}"

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
