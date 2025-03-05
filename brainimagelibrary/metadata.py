import requests

def by_affiliation(affiliation, params=None, headers=None):
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

def retrieve(dataset_id, params=None, headers=None):
    api_url = f"https://api.brainimagelibrary.org/retrieve?bildid={dataset_id}"

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
    api_url = f"https://api.brainimagelibrary.org/query/metadatadivision?metadataelement={query_string}"

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
