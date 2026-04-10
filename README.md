![Status](https://github.com/brain-image-library/py-brain-sdk/actions/workflows/bump-version.yml/badge.svg)
![Issue](https://img.shields.io/github/issues/brain-image-library/py-brain-sdk)
![forks](https://img.shields.io/github/forks/brain-image-library/py-brain-sdk)
![Stars](https://img.shields.io/github/stars/brain-image-library/py-brain-sdk)
![License](https://img.shields.io/github/license/brain-image-library/py-brain-sdk)

# py-brain-sdk

py-brain-sdk is a Python library that simplifies interaction with the Brain Image Library (BIL), a national public resource for neuroscience research. BIL provides access to petabyte-scale brain microscopy datasets, including whole and partial brain images, neuron morphologies, connectivity data, and spatial transcriptomics. This SDK enables researchers, data scientists, and developers to programmatically query, download, and analyze BIL datasets, leveraging its APIs and integrated analysis ecosystem.

With py-brain-sdk, you can

* Search and retrieve brain imaging datasets and metadata.
* Query datasets by ID, directory path, contributor affiliation, or free-text search.
* Look up DOI metadata and citation counts from DataCite, OpenCitations, Crossref, and Semantic Scholar.
* Browse BIL collections and enumerate their constituent datasets.
* Download specific image files or subsets of large datasets.

## Installation

```bash
pip install brainimagelibrary
```

## Quick Start

### Retrieve dataset metadata

```python
import brainimagelibrary as bil

# By BIL dataset ID
metadata = bil.retrieve.by_id(bildid="act-bag")

# By directory path
metadata = bil.retrieve.by_directory(directory="/bil/data/2019/02/13/H19.28.012.MITU.01.05")

# Full-text search
results = bil.metadata.query("mouse cortex")

# By contributor affiliation
results = bil.metadata.by_affiliation("Carnegie Mellon University")
```

### List all dataset IDs

```python
import brainimagelibrary as bil

bildids = bil.get_all_bildids()
print(f"Total datasets: {len(bildids)}")
```

### DOI and citation lookup

```python
from brainimagelibrary import dois

# Check if a dataset has a registered DOI
dois.dataset.exists(bildid="act-bag")

# Get DataCite metadata
metadata = dois.dataset.get(bildid="act-bag")

# Get citation counts from multiple sources
citations = dois.dataset.get_number_of_citations(bildid="act-bag")
# {‘datacite’: 2, ‘opencitations’: 1, ‘crossref’: 0, ‘semanticscholar’: 3}

# Get full citation records
records = dois.dataset.get_datacite_citations(bildid="act-bag")
```

### Collection operations

```python
from brainimagelibrary import dois

# List all datasets in a collection
datasets = dois.collection.get_datasets(bildid="act-bag")
for entry in datasets:
    print(entry["bildid"], entry["url"])
```

---
Copyright © 2020-2025 Pittsburgh Supercomputing Center. All Rights Reserved.

The [Biomedical Applications Group](https://www.psc.edu/biomedical-applications/) at the [Pittsburgh Supercomputing Center](http://www.psc.edu) in the [Mellon College of Science](https://www.cmu.edu/mcs/) at [Carnegie Mellon University](http://www.cmu.edu).
