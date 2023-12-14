import requests


def by_id(bildid=None, params=None, headers=None):
    if not bildid:
        return {}

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


def by_directory(directory=None, params=None, headers=None):
    if not directory:
        return {}

    api_url = (
        f"https://api.brainimagelibrary.org/query/dataset?bildirectory={directory}"
    )

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


def by_version(version="2.0"):
    api_url = f"https://api.brainimagelibrary.org/query/submission?metadata={version}"

    try:
        response = requests.get(api_url)

        response = response.json()
        if (
            "message" in response.keys()
            and response["message"] == "GET failure, no entry found"
        ):
            return {}
        else:
            return response["bildids"]

    except requests.exceptions.RequestException as e:
        print(f"Error making API request: {e}")
        return None


def get_all_bildids():
    v2 = by_version(version="2.0")
    v1 = by_version(version="1.0")

    return v2
