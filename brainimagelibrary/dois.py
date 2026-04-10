import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from .retrieve import by_url as _retrieve_by_url

MAX_WORKERS = 8

DOI_PREFIX = "10.35077"


class Dataset:
    """DOI operations for individual BIL datasets."""

    def get(self, bildid="act-bag"):
        """
        Retrieves metadata for a specific dataset from the DataCite API.

        Args:
            bildid (str, optional): The unique identifier for the dataset.
                Defaults to "act-bag".

        Returns:
            dict or None: A dictionary containing the metadata for the dataset, as
                retrieved from the DataCite API, or None if the API request fails
                or the dataset is not found.

        Example:
            >>> from brainimagelibrary import dois
            >>> metadata = dois.dataset.get(bildid="act-bag")
            >>> print(type(metadata))
            <class 'dict'>
            >>> print("data" in metadata)
            True
        """
        return _get_datacite_metadata(bildid=bildid)

    def get_datacite_citations(self, bildid="act-bag"):
        """
        Retrieves citation metadata for a specific dataset from multiple sources.

        Args:
            bildid (str, optional): The unique identifier for the dataset.
                Defaults to "act-bag".

        Returns:
            dict: A dictionary with citation metadata from each source:
                - `datacite` (list): Citation records from DataCite, or None if unavailable.
                  Each record includes a `title` key extracted from `attributes.titles`.
                - `opencitations` (list): Citation records from OpenCitations, or None if unavailable.
                  Each record includes a `title` key fetched via the Crossref API.
                - `crossref` (list): Citation records from Crossref, or None if unavailable.
                  Each record includes a `title` key normalized from the `title` array.
                - `semanticscholar` (list): Citation records from Semantic Scholar, or None if unavailable.
                  Each record includes a `title` key extracted from `citingPaper`.

                Returns None for all keys if the DOI does not exist.

        Example:
            >>> from brainimagelibrary import dois
            >>> result = dois.dataset.get_datacite_citations(bildid="act-bag")
            >>> print(type(result))
            <class 'dict'>
            >>> print(list(result.keys()))
            ['datacite', 'opencitations', 'crossref', 'semanticscholar']
            >>> import pprint; pprint.pprint(result)  # doctest: +SKIP
            {'crossref': None,
             'datacite': None,
             'opencitations': [{'author_sc': 'no',
                                'cited': '10.35077/act-bag',
                                'citing': '10.1038/s41586-023-06808-9',
                                'creation': '2023-12-13',
                                'journal_sc': 'no',
                                'oci': '06320380336-06480144673',
                                'timespan': '',
                                'title': 'Molecularly defined and spatially resolved '
                                         'cell atlas of the whole mouse brain'},
                               {'author_sc': 'no',
                                'cited': '10.35077/act-bag',
                                'citing': '10.1101/2023.08.13.552987',
                                'creation': '2023-08-15',
                                'journal_sc': 'yes',
                                'oci': '06404413343-06480144673',
                                'timespan': '',
                                'title': 'Search and Match across Spatial Omics '
                                         'Samples at Single-cell Resolution'}],
             'semanticscholar': None}
        """
        if not _doi_exists(bildid=bildid):
            return {
                "datacite": None,
                "opencitations": None,
                "crossref": None,
                "semanticscholar": None,
            }

        sources = {
            "datacite": _get_citations_from_datacite,
            "opencitations": _get_citations_from_opencitations,
            "crossref": _get_citations_from_crossref,
            "semanticscholar": _get_citations_from_semanticscholar,
        }
        results = {}
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {executor.submit(fn, bildid=bildid): key for key, fn in sources.items()}
            for future in as_completed(futures):
                results[futures[future]] = future.result()
        return results

    def get_number_of_citations(self, bildid="act-bag"):
        """
        Retrieves the number of citations for a specific dataset.

        Args:
            bildid (str, optional): The unique identifier for the dataset.
                Defaults to "act-bag".

        Returns:
            dict: A dictionary containing citation counts from different sources:
                - `datacite` (int): Citation count from DataCite, or None if unavailable.
                - `opencitations` (int): Citation count from OpenCitations, or None if unavailable.
                - `crossref` (int): Citation count from Crossref, or None if unavailable.
                - `semanticscholar` (int): Citation count from Semantic Scholar, or None if unavailable.

                Returns None for all keys if the DOI does not exist.

        Example:
            >>> from brainimagelibrary import dois
            >>> citations = dois.dataset.get_number_of_citations(bildid="act-bag")
            >>> print(type(citations))
            <class 'dict'>
            >>> print(list(citations.keys()))
            ['datacite', 'opencitations', 'crossref', 'semanticscholar']
        """
        if not _doi_exists(bildid=bildid):
            return {
                "datacite": None,
                "opencitations": None,
                "crossref": None,
                "semanticscholar": None,
            }

        sources = {
            "datacite": _get_number_of_citations_from_datacite,
            "opencitations": _get_number_of_citations_from_opencitations,
            "crossref": _get_number_of_citations_from_crossref,
            "semanticscholar": _get_number_of_citations_from_semanticscholar,
        }
        results = {}
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {executor.submit(fn, bildid=bildid): key for key, fn in sources.items()}
            for future in as_completed(futures):
                results[futures[future]] = future.result()
        return results

    def exists(self, bildid="act-bag"):
        """
        Checks whether a dataset has a DOI registered in DataCite.

        Args:
            bildid (str, optional): The unique identifier for the dataset.
                Defaults to "act-bag".

        Returns:
            bool: True if the DOI exists in DataCite, False otherwise.

        Example:
            >>> from brainimagelibrary import dois
            >>> dois.dataset.exists(bildid="act-bag")
            True
            >>> dois.dataset.exists(bildid="nonexistent-id")
            False
        """
        return _doi_exists(bildid=bildid)


class Collection:
    """DOI operations for BIL collections."""

    def get(self, bildid="act-bag"):
        """
        Retrieves metadata for a specific collection from the DataCite API.

        Args:
            bildid (str, optional): The unique identifier for the collection.
                Defaults to "act-bag".

        Returns:
            dict or None: A dictionary containing the metadata for the collection, as
                retrieved from the DataCite API, or None if the API request fails
                or the collection is not found.

        Example:
            >>> from brainimagelibrary import dois
            >>> metadata = dois.collection.get(bildid="act-bag")
            >>> print(type(metadata))
            <class 'dict'>
            >>> print("data" in metadata)
            True
        """
        if not _doi_exists(bildid=bildid):
            return None
        return _get_datacite_metadata(bildid=bildid)

    def get_datasets(self, bildid="act-bag"):
        """
        Returns all download URLs for datasets in a collection.

        Calls collection.get to retrieve DataCite metadata, then walks all
        string values in the response and returns those that are URLs hosted
        on download.brainimagelibrary.org.

        Args:
            bildid (str, optional): The unique identifier for the collection.
                Defaults to "act-bag".

        Returns:
            list: A list of dicts with shape ``{"bildid": ..., "url": ...}``
                  for each URL found on download.brainimagelibrary.org.
                  Returns an empty list if no such URLs are found or if
                  metadata cannot be retrieved.

        Example:
            >>> from brainimagelibrary import dois
            >>> urls = dois.collection.get_datasets(bildid="act-bag")
            >>> print(type(urls))
            <class 'list'>
        """
        metadata = _get_datacite_metadata(bildid=bildid)
        if not metadata:
            return []

        urls = set()
        related = metadata.get("data", {}).get("attributes", {}).get("relatedIdentifiers", [])
        for item in related:
            identifier = item.get("relatedIdentifier", "")
            if "download.brainimagelibrary.org" in identifier:
                urls.add(identifier)

        results = []
        for url in urls:
            data = _retrieve_by_url(url)
            if data and "bildids" in data:
                for bildid in data["bildids"]:
                    results.append({"bildid": bildid, "url": url})
            elif data and "retjson" in data:
                bildid = data["retjson"][0].get("bildid")
                results.append({"bildid": bildid, "url": url})
            else:
                results.append({"bildid": None, "url": url})
        return results

    def exists(self, bildid="act-bag"):
        """
        Checks whether a collection has a DOI registered in DataCite.

        Args:
            bildid (str, optional): The unique identifier for the collection.
                Defaults to "act-bag".

        Returns:
            bool: True if the DOI exists in DataCite, False otherwise.

        Example:
            >>> from brainimagelibrary import dois
            >>> dois.collection.exists(bildid="act-bag")
            True
            >>> dois.collection.exists(bildid="nonexistent-id")
            False
        """
        return _doi_exists(bildid=bildid)


dataset = Dataset()
collection = Collection()


def get_datacite_metadata(bildid="act-bag"):
    """
    Retrieves metadata for a specific dataset from the DataCite API.

    Args:
        bildid (str, optional): The unique identifier for the dataset.
            Defaults to "act-bag".

    Returns:
        dict or None: A dictionary containing the metadata for the dataset, as retrieved
            from the DataCite API, or None if the API request fails or the dataset
            is not found.

    Example:
        >>> from brainimagelibrary import dois
        >>> metadata = dois.get_datacite_metadata(bildid="act-bag")
        >>> print(type(metadata))
        <class 'dict'>
        >>> print("data" in metadata)
        True
    """
    return _get_datacite_metadata(bildid=bildid)


def get_datacite_citations(bildid="act-bag"):
    """
    Retrieves citation metadata for a specific dataset from multiple sources.

    Args:
        bildid (str, optional): The unique identifier for the dataset.
            Defaults to "act-bag".

    Returns:
        dict: A dictionary with citation metadata from each source:
            - `datacite` (list): Citation records from DataCite, or None if unavailable.
              Each record includes a `title` key extracted from `attributes.titles`.
            - `opencitations` (list): Citation records from OpenCitations, or None if unavailable.
              Each record includes a `title` key fetched via the Crossref API.
            - `crossref` (list): Citation records from Crossref, or None if unavailable.
              Each record includes a `title` key normalized from the `title` array.
            - `semanticscholar` (list): Citation records from Semantic Scholar, or None if unavailable.
              Each record includes a `title` key extracted from `citingPaper`.

            Returns None for all keys if the DOI does not exist.

    Example:
        >>> from brainimagelibrary import dois
        >>> result = dois.get_datacite_citations(bildid="act-bag")
        >>> print(type(result))
        <class 'dict'>
        >>> print(list(result.keys()))
        ['datacite', 'opencitations', 'crossref', 'semanticscholar']
        >>> import pprint; pprint.pprint(result)  # doctest: +SKIP
        {'crossref': None,
         'datacite': None,
         'opencitations': [{'author_sc': 'no',
                            'cited': '10.35077/act-bag',
                            'citing': '10.1038/s41586-023-06808-9',
                            'creation': '2023-12-13',
                            'journal_sc': 'no',
                            'oci': '06320380336-06480144673',
                            'timespan': '',
                            'title': 'Molecularly defined and spatially resolved '
                                     'cell atlas of the whole mouse brain'},
                           {'author_sc': 'no',
                            'cited': '10.35077/act-bag',
                            'citing': '10.1101/2023.08.13.552987',
                            'creation': '2023-08-15',
                            'journal_sc': 'yes',
                            'oci': '06404413343-06480144673',
                            'timespan': '',
                            'title': 'Search and Match across Spatial Omics '
                                     'Samples at Single-cell Resolution'}],
         'semanticscholar': None}
    """
    return dataset.get_datacite_citations(bildid=bildid)


def get_number_of_citations(bildid="act-bag"):
    """
    Retrieves the number of citations for a specific dataset.

    Args:
        bildid (str, optional): The unique identifier for the dataset.
            Defaults to "act-bag".

    Returns:
        dict: A dictionary containing citation counts from different sources:
            - `datacite` (int): Citation count from DataCite, or None if unavailable.
            - `opencitations` (int): Citation count from OpenCitations, or None if unavailable.
            - `crossref` (int): Citation count from Crossref, or None if unavailable.
            - `semanticscholar` (int): Citation count from Semantic Scholar, or None if unavailable.

            Returns None for all keys if the DOI does not exist.

    Example:
        >>> from brainimagelibrary import dois
        >>> citations = dois.get_number_of_citations(bildid="act-bag")
        >>> print(type(citations))
        <class 'dict'>
        >>> print(list(citations.keys()))
        ['datacite', 'opencitations', 'crossref', 'semanticscholar']
    """
    return dataset.get_number_of_citations(bildid=bildid)


def _doi_exists(bildid="act-bag"):
    """Returns True if the DOI exists in DataCite, False otherwise."""
    url = f"https://api.datacite.org/dois/{DOI_PREFIX}/{bildid}"
    try:
        response = requests.get(url, timeout=30)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False


def _get_datacite_metadata(bildid="act-bag"):
    """
    Retrieves metadata for a dataset from the DataCite API.

    Args:
        bildid (str, optional): The unique identifier for the dataset.
            Defaults to "act-bag".

    Returns:
        dict: A dictionary containing the dataset's metadata if the request is successful.
        None: If the request fails or the API returns an error.
    """
    url = f"https://api.datacite.org/dois/{DOI_PREFIX}/{bildid}"

    response = requests.get(url)

    if response.status_code == 200:
        return response.json()

    return None


def _get_number_of_citations_from_opencitations(bildid="act-bag"):
    doi = f"{DOI_PREFIX}/{bildid}"
    url = f"https://opencitations.net/index/coci/api/v1/citation-count/{doi}"

    try:
        response = requests.get(url, timeout=30)
        if response.status_code != 200:
            return None
        data = response.json()
        count = int(data[0]["count"])
        return count
    except (IndexError, KeyError, ValueError, requests.exceptions.RequestException):
        return None


def _get_number_of_citations_from_datacite(bildid="act-bag"):
    metadata = _get_datacite_metadata(bildid=bildid)

    if metadata is None:
        return None

    try:
        return metadata["data"]["attributes"]["citationCount"]
    except (KeyError, TypeError):
        return None


def _get_number_of_citations_from_crossref(bildid="act-bag"):
    doi = f"{DOI_PREFIX}/{bildid}"
    url = f"https://api.crossref.org/works/{doi}"

    try:
        response = requests.get(url, timeout=30)
        if response.status_code != 200:
            return None
        data = response.json()
        count = data["message"]["is-referenced-by-count"]
        return count
    except (KeyError, TypeError, ValueError, requests.exceptions.RequestException):
        return None


def _get_number_of_citations_from_semanticscholar(bildid="act-bag"):
    doi = f"{DOI_PREFIX}/{bildid}"
    url = f"https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}?fields=citationCount"

    try:
        response = requests.get(url, timeout=30)
        if response.status_code != 200:
            return None
        data = response.json()
        count = data["citationCount"]
        return count
    except (KeyError, TypeError, ValueError, requests.exceptions.RequestException):
        return None


def _get_title_for_doi(doi):
    """Fetches the title for a given DOI via the Crossref API. Returns None on failure."""
    url = f"https://api.crossref.org/works/{doi}"
    try:
        response = requests.get(url, timeout=30)
        if response.status_code != 200:
            return None
        titles = response.json().get("message", {}).get("title", [])
        return titles[0] if titles else None
    except (IndexError, KeyError, TypeError, requests.exceptions.RequestException):
        return None


def _get_citations_from_datacite(bildid="act-bag"):
    """Returns list of citing works from DataCite, or None on failure."""
    doi = f"{DOI_PREFIX}/{bildid}"
    url = f"https://api.datacite.org/dois/{doi}/citations"
    try:
        response = requests.get(url, timeout=30)
        if response.status_code != 200:
            return None
        records = response.json().get("data", None)
        if records is None:
            return None
        for record in records:
            titles = record.get("attributes", {}).get("titles", [])
            record["title"] = titles[0]["title"] if titles else None
        return records
    except requests.exceptions.RequestException:
        return None


def _get_citations_from_opencitations(bildid="act-bag"):
    """Returns list of citing works from OpenCitations, or None on failure."""
    doi = f"{DOI_PREFIX}/{bildid}"
    url = f"https://opencitations.net/index/coci/api/v1/citations/{doi}"
    try:
        response = requests.get(url, timeout=30)
        if response.status_code != 200:
            return None
        records = response.json()
        if not records:
            return records
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {
                executor.submit(_get_title_for_doi, record.get("citing", "")): i
                for i, record in enumerate(records)
            }
            for future in as_completed(futures):
                records[futures[future]]["title"] = future.result()
        return records
    except requests.exceptions.RequestException:
        return None


def _get_citations_from_crossref(bildid="act-bag"):
    """Returns list of citing works from Crossref, or None on failure."""
    doi = f"{DOI_PREFIX}/{bildid}"
    url = f"https://api.crossref.org/works?filter=cites:{doi}"
    try:
        response = requests.get(url, timeout=30)
        if response.status_code != 200:
            return None
        items = response.json().get("message", {}).get("items", None)
        if items is None:
            return None
        for item in items:
            titles = item.get("title", [])
            item["title"] = titles[0] if titles else None
        return items
    except (KeyError, TypeError, requests.exceptions.RequestException):
        return None


def _get_citations_from_semanticscholar(bildid="act-bag"):
    """Returns list of citing works from Semantic Scholar, or None on failure."""
    doi = f"{DOI_PREFIX}/{bildid}"
    url = f"https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}/citations?fields=title,authors,year,externalIds"
    try:
        response = requests.get(url, timeout=30)
        if response.status_code != 200:
            return None
        records = response.json().get("data", None)
        if records is None:
            return None
        for record in records:
            record["title"] = record.get("citingPaper", {}).get("title")
        return records
    except (KeyError, TypeError, requests.exceptions.RequestException):
        return None
