import requests

DOI_PREFIX = "10.35077"


def get_number_of_citations(bildid="act-bag"):
    """
    Retrieves the number of citations for a specific dataset.

    This function gathers citation data for a given dataset by querying multiple
    sources, such as DataCite and OpenCitations.

    Args:
        bildid (str, optional): The unique identifier for the dataset.
            Defaults to "act-bag".

    Returns:
        dict: A dictionary containing citation counts from different sources:
            - `datacite` (int): Citation count from DataCite, or None if unavailable.
            - `opencitations` (int): Citation count from OpenCitations, or None if unavailable.
        None: If both sources fail to return citation data.

    Example:
        >>> from brainimagelibrary import dois
        >>> citations = dois.get_number_of_citations(bildid="act-bag")
        >>> print(type(citations))
        <class 'dict'>
        >>> print(list(citations.keys()))
        ['datacite', 'opencitations']
    """
    datacite = __get_number_of_citations_from_datacite(bildid=bildid)
    opencitations = __get_number_of_citations_from_opencitations(bildid=bildid)

    if datacite is None and opencitations is None:
        return None

    return {"datacite": datacite, "opencitations": opencitations}


def get_metadata(bildid="act-bag"):
    """
    Retrieves metadata for a specific dataset from the DataCite API.

    Args:
        bildid (str, optional): The unique identifier for the dataset.
            Defaults to "act-bag".

    Returns:
        dict: A dictionary containing the metadata for the dataset, as retrieved
              from the DataCite API.
        None: If the API request fails or the dataset is not found.

    Example:
        >>> from brainimagelibrary import dois
        >>> metadata = dois.get_metadata(bildid="act-bag")
        >>> print(type(metadata))
        <class 'dict'>
        >>> print("data" in metadata)
        True
    """
    return __get_datacite_metadata(bildid=bildid)


def __get_number_of_citations_from_opencitations(bildid="act-bag"):
    """
    Retrieves the number of citations for a dataset from OpenCitations.

    Queries the OpenCitations COCI REST API using the dataset's DOI.

    Args:
        bildid (str, optional): The unique identifier for the dataset.
            Defaults to "act-bag".

    Returns:
        int: The number of citations if the dataset is found on OpenCitations.
        None: If no citation data is found or if an error occurs.

    Example:
        >>> from brainimagelibrary import dois
        >>> citations = dois.__get_number_of_citations_from_opencitations(bildid="act-bag")
        >>> print(type(citations))
        <class 'int'>
        >>> print(citations >= 0)
        True
    """
    doi = f"{DOI_PREFIX}/{bildid}"
    url = f"https://opencitations.net/index/coci/api/v1/citation-count/{doi}"

    try:
        response = requests.get(url, timeout=30)
        if response.status_code != 200:
            return None
        data = response.json()
        return int(data[0]["count"])
    except (IndexError, KeyError, ValueError, requests.exceptions.RequestException):
        return None


def __get_number_of_citations_from_datacite(bildid="act-bag"):
    """
    Retrieves the number of citations for a dataset from DataCite.

    This function fetches metadata for a given dataset from the DataCite API and
    extracts the citation count.

    Args:
        bildid (str, optional): The unique identifier for the dataset.
            Defaults to "act-bag".

    Returns:
        int: The number of citations for the dataset if available.
        None: If no citation data is found or if an error occurs.

    Example:
        >>> from brainimagelibrary import dois
        >>> citations = dois.__get_number_of_citations_from_datacite(bildid="act-bag")
        >>> print(type(citations))
        <class 'int'>
        >>> print(citations >= 0)
        True
    """
    metadata = __get_datacite_metadata(bildid=bildid)

    if metadata is None:
        return None

    try:
        return metadata["data"]["attributes"]["citationCount"]
    except (KeyError, TypeError):
        return None


def __get_datacite_metadata(bildid="act-bag"):
    """
    Retrieves metadata for a dataset from the DataCite API.

    This function sends a GET request to the DataCite API to fetch metadata
    for a dataset using its DOI prefix and dataset ID.

    Args:
        bildid (str, optional): The unique identifier for the dataset.
            Defaults to "act-bag".

    Returns:
        dict: A dictionary containing the dataset's metadata if the request is successful.
        None: If the request fails or the API returns an error.

    Raises:
        requests.exceptions.RequestException: If there is a network issue during the API request.

    Example:
        >>> from brainimagelibrary import dois
        >>> metadata = dois.__get_datacite_metadata(bildid="act-bag")
        >>> print(type(metadata))
        <class 'dict'>
        >>> print("data" in metadata)
        True
    """
    url = f"https://api.datacite.org/dois/{DOI_PREFIX}/{bildid}"

    response = requests.get(url)

    if response.status_code == 200:
        return response.json()

    return None
