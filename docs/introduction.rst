Introduction
============

What is the Brain Image Library?
---------------------------------

The `Brain Image Library <https://www.brainimagelibrary.org>`_ (BIL) is a national public resource for neuroscience research,
funded by the National Institutes of Health. It provides long-term storage, management, and access to petabyte-scale
brain microscopy datasets submitted by researchers across the United States.

BIL hosts a wide range of data types, including:

* Whole and partial brain image volumes
* Neuron morphologies and connectivity maps
* Spatial transcriptomics data
* Multi-resolution light-sheet and electron microscopy images

All datasets are citable via registered DOIs and are freely accessible to the research community.
The library is operated by the `Pittsburgh Supercomputing Center <https://www.psc.edu>`_ at Carnegie Mellon University.

What is the Python SDK?
-----------------------

``brainimagelibrary`` is a Python SDK that provides a programmatic interface to BIL's APIs and data holdings.
It is designed for researchers, data scientists, and developers who want to search, retrieve, and analyze
BIL datasets without manually navigating the web portal or writing raw HTTP requests.

The SDK exposes five modules, each focused on a specific area of functionality:

.. list-table::
   :widths: 20 80
   :header-rows: 1

   * - Module
     - Description
   * - ``retrieve``
     - Fetch dataset metadata by BIL dataset ID, directory path, URL, affiliation, or version.
   * - ``query``
     - Query datasets by BIL ID, directory path, URL, affiliation, version, or free-text search.
   * - ``metadata``
     - Retrieve raw dataset metadata by BIL dataset ID.
   * - ``inventory``
     - Download and parse per-dataset file inventories, with support for manifest export
       and parallel file download.
   * - ``datecite``
     - Look up DOI registration, citation counts, and citation records from DataCite,
       OpenCitations, Crossref, and Semantic Scholar.
   * - ``reports`` / ``summary``
     - Generate summary statistics and reports across the BIL catalog.

Quick example
-------------

The following snippet retrieves metadata for a dataset by its BIL dataset ID and performs a
keyword search::

    import brainimagelibrary as bil

    # Fetch metadata for a specific dataset
    metadata = bil.retrieve.by_id(bildid="act-bag")

    # Full-text search across all datasets
    results = bil.query.by_text("mouse cortex")

    # Look up citation counts from multiple sources
    citations = bil.datecite.dataset.get_number_of_citations(bildid="act-bag")
    # {'datacite': 2, 'opencitations': 1, 'crossref': 0, 'semanticscholar': 3}

See the :doc:`installation` page to get started, and the API Reference for full module documentation.

Interactive example
-------------------

Click the button below to launch a live Python environment (via `Binder <https://mybinder.org>`_)
and run the code directly in your browser.

.. thebe-button:: Launch interactive session

.. code-block:: python
   :class: thebe
   :caption: Retrieve citation records for dataset ``act-bag``

   import subprocess, sys
   subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "brainimagelibrary"])

   import brainimagelibrary as bil
   import pprint

   result = bil.datecite.get_datacite_citations(bildid="act-bag")
   pprint.pprint(result)
