from . import reports


def daily(option="simple", overwrite=False):
    """
    Returns a summary of the daily Brain Image Library inventory report.

    Args:
        option (str, optional): Type of daily report to fetch. Options are:
            - ``"simple"``: Fetches the simple daily inventory (default).
            - ``"detailed"``: Fetches the detailed daily report.
        overwrite (bool, optional): If True, forces regeneration of the report
            even if a cached version exists. Defaults to False.

    Returns:
        dict: A dictionary with the following keys:
            - ``metadata_version``: Value counts of metadata versions.
            - ``number_of_datasets``: Total number of datasets (int).
            - ``number_of_unique_contributors``: Count of unique contributors (int).
            - ``contributors``: Value counts of contributor names.
            - ``number_of_unique_affiliations``: Count of unique affiliations (int).
            - ``affiliations``: Value counts of contributor affiliations.
            - ``number_of_unique_species``: Count of unique species (int).
            - ``species``: Value counts of species.
            - ``number_of_files``: Total number of files across all datasets (int or long int).

    Example:
        >>> from brainimagelibrary import summary
        >>> report = summary.daily(option="simple")
        >>> print(type(report))
        <class 'dict'>
        >>> print(list(report.keys()))
        ['metadata_version', 'number_of_datasets', 'number_of_unique_contributors', 'contributors', 'number_of_unique_affiliations', 'affiliations', 'number_of_unique_species', 'species', 'number_of_files']
        >>> print(report["number_of_datasets"] > 0)
        True
        >>> print(report["number_of_unique_contributors"] > 0)
        True
        >>> print(report["number_of_unique_affiliations"] > 0)
        True
        >>> print(report["number_of_unique_species"] > 0)
        True
        >>> print(report["number_of_files"] > 0)
        True
    """
    report = reports.daily(option=option, overwrite=overwrite)
    return {
        "metadata_version": report["metadata_version"].value_counts(),
        "number_of_datasets": len(report),
        "number_of_unique_contributors": report["contributor"].nunique(),
        "number_of_unique_affiliations": report["affiliation"].nunique(),
        "number_of_unique_species": report["species"].nunique(),
        "number_of_files": int(report["number_of_files"].sum()),
    }
