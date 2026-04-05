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
            - ``contributors``: Value counts of contributor names.
            - ``affiliations``: Value counts of contributor affiliations.
            - ``species``: Value counts of species.
            - ``number_of_files``: Placeholder (None); not yet implemented.
    """
    report = reports.daily(option=option, overwrite=overwrite)
    return {
        "metadata_version": report["metadata_version"].value_counts(),
        "number_of_datasets": len(report),
        "contributors": report["contributor"].value_counts(),
        "affiliations": report["affiliation"].value_counts(),
        "species": report["species"].value_counts(),
        "number_of_files": None,
    }
