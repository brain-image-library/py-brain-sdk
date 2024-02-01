import requests

def get_number_of_citations(dataset_id="act-bag"):
    data = {}
    data["datacite"] = __get_number_of_citations_from_datacite(dataset_id=dataset_id)

    return data


def get_metadata(dataset_id="act-bag"):
    return __get_datacite_metadata(dataset_id=dataset_id)

def __get_number_of_citations_from_datacite(dataset_id="act-bag"):
    metadata = __get_datacite_metadata(dataset_id=dataset_id)

    try:
        return metadata["data"]["attributes"]["citationCount"]
    except:
        # print(f'Unable to retrieve metadata for {dataset_id}')
        return None


def __get_datacite_metadata(dataset_id="act-bag"):
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
