import requests
from scholarly import scholarly


def get_number_of_citations(dataset_id="act-bag"):
    """
    Retrieves the number of citations for a specific dataset.

    This function gathers citation data for a given dataset by querying multiple
    sources, such as DataCite and Google Scholar.

    Args:
        dataset_id (str, optional): The unique identifier for the dataset.
            Defaults to "act-bag".

    Returns:
        dict: A dictionary containing citation counts from different sources:
            - `datacite` (int): Citation count from DataCite.
            - `gscholar` (int): Citation count from Google Scholar.

    Example:
        >>> citations = get_number_of_citations(dataset_id="my-dataset")
        >>> print(citations)
        {'datacite': 12, 'gscholar': 5}
    """
    data = {}
    data["datacite"] = __get_number_of_citations_from_datacite(dataset_id=dataset_id)
    data["gscholar"] = __get_number_of_citations_from_gscholar(dataset_id=dataset_id)

    return data


def get_metadata(dataset_id="act-bag"):
    """
    Retrieves metadata for a specific dataset.

    This function fetches metadata for a given dataset by querying the DataCite API.

    Args:
        dataset_id (str, optional): The unique identifier for the dataset.
            Defaults to "act-bag".

    Returns:
        dict: A dictionary containing the metadata for the dataset, as retrieved
              from the DataCite API.

    Example:
        >>> metadata = get_metadata(dataset_id="my-dataset")
        >>> print(metadata)
        {'title': 'Dataset Title', 'authors': ['Author A', 'Author B'], ...}
    """
    return __get_datacite_metadata(dataset_id=dataset_id)


def __get_number_of_citations_from_gscholar(dataset_id="act-bag"):
    """
    Retrieves the number of citations for a dataset from Google Scholar.

    This function queries Google Scholar to fetch the number of citations for a
    given dataset using its DOI prefix and dataset ID.

    Args:
        dataset_id (str, optional): The unique identifier for the dataset.
            Defaults to "act-bag".

    Returns:
        int: The number of citations if the dataset is found on Google Scholar.
        None: If no citation data is found or if an error occurs.

    Raises:
        StopIteration: If the query does not return any results.
        Exception: If an unexpected error occurs during the query.

    Example:
        >>> citations = __get_number_of_citations_from_gscholar(dataset_id="my-dataset")
        >>> print(citations)
        42
    """
    brain = "10.35077"
    query = f"{brain}/{dataset_id}"

    try:
        search_query = scholarly.search_pubs(query)
        metadata = next(search_query)
        return metadata["num_citations"]
    except:
        return None


def __get_number_of_citations_from_datacite(dataset_id="act-bag"):
    """
    Retrieves the number of citations for a dataset from DataCite.

    This function fetches metadata for a given dataset from the DataCite API and
    extracts the citation count.

    Args:
        dataset_id (str, optional): The unique identifier for the dataset.
            Defaults to "act-bag".

    Returns:
        int: The number of citations for the dataset if available.
        None: If no citation data is found or if an error occurs.

    Raises:
        KeyError: If the expected fields are missing in the DataCite metadata.
        Exception: If an unexpected error occurs during the metadata retrieval.

    Example:
        >>> citations = __get_number_of_citations_from_datacite(dataset_id="my-dataset")
        >>> print(citations)
        25
    """
    metadata = __get_datacite_metadata(dataset_id=dataset_id)

    try:
        return metadata["data"]["attributes"]["citationCount"]
    except:
        # print(f'Unable to retrieve metadata for {dataset_id}')
        return None


def __get_datacite_metadata(dataset_id="act-bag"):
    """
    Retrieves metadata for a dataset from the DataCite API.

    This function sends a GET request to the DataCite API to fetch metadata
    for a dataset using its DOI prefix and dataset ID.

    Args:
        dataset_id (str, optional): The unique identifier for the dataset.
            Defaults to "act-bag".

    Returns:
        dict: A dictionary containing the dataset's metadata if the request is successful.
        None: If the request fails or the API returns an error.

    Raises:
        requests.exceptions.RequestException: If there is a network issue during the API request.

    Example:
        >>> metadata = __get_datacite_metadata(dataset_id="my-dataset")
        >>> print(metadata)
        {'data': {'type': 'dois', 'attributes': {...}}}
    """
    brain = "10.35077"
    url = f"https://api.datacite.org/dois/{brain}/{dataset_id}"

    # Send GET request to the API
    response = requests.get(url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the JSON response
        metadata = response.json()

        # Display the metadata
        return metadata
    else:
        # Print an error message if the request was not successful
        return None
