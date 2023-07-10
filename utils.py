import json
from constants import tags_df, DATA_BASE, pd, nlp
from flask import Response


def response_structure(code):
    """
    Determine the response status based on the status code.

    Args:
        code (int): The status code.

    Returns:
        str: The response status.

    """
    return "success" if 200 <= code < 400 else "error"


def create_response(message, status_code):
    """
    Create the JSON response structure.

    Args:
        message (str): The response message.
        message (list): The sorted list.
        status_code (int): The status code.

    Returns:
        dict: The JSON response.

    """

    if status_code >= 200 and status_code < 400:
        response = {
            "status": response_structure(status_code),
            "data": list(message),
            "message": "Experts got succesfully",
            "status_code": status_code,
        }
    else:
        response = {
            "status": response_structure(status_code),
            "message": message,
            "status_code": status_code,
        }

    response_str = json.dumps(response)
    response = Response(
        response_str, status=status_code, content_type="application/json"
    )
    return response


def get_relevant_tags(prompt):
    """
    Get the relevant tags based on the prompt.

    Args:
        prompt (str): The user prompt.

    Returns:
        list: The list of matching tags.

    """
    keywords = extract_keywords(prompt)
    matching_tags = []
    for index, row in tags_df.iterrows():
        tag_name = row["Tag name"]
        description = row["description"]
        if any(
            keyword.lower() in tag_name.lower()
            or (not pd.isnull(description) and keyword.lower() in description.lower())
            for keyword in keywords
        ):
            matching_tags.append({"tag_name": tag_name, "emoji": row["emoji"]})
    return matching_tags


def get_relevant_platforms(keywords):
    """
    Get the relevant platforms based on the keywords.

    Args:
        keywords (list): The extracted keywords.

    Returns:
        list: The list of matching platforms.

    """
    platforms_df = pd.read_csv(DATA_BASE + "Platforms.csv")
    matching_platforms = []
    for index, row in platforms_df.iterrows():
        platform_name = row["Name"]
        description = row["Description"]
        if any(
            keyword.lower() in platform_name.lower()
            or (not pd.isnull(description) and keyword.lower() in description.lower())
            for keyword in keywords
        ):
            matching_platforms.append({"platform_name": platform_name})
    return matching_platforms


def extract_keywords(prompt):
    """
    Extract relevant keywords from the prompt.

    Args:
        prompt (str): The user prompt.

    Returns:
        list: The extracted keywords.

    """
    doc = nlp(prompt)
    keywords = [token.lemma_ for token in doc if token.pos_ in ["NOUN", "PROPN"]]
    return keywords


def generate_json_response(tags, platforms):
    """
    Generate a JSON response based on the matching tags and platforms.

    Args:
        tags (list): The matching tags.
        platforms (list): The matching platforms.

    Returns:
        str: The JSON response.

    """
    response = {"tags": tags, "platforms": platforms}
    return json.dumps(response)


def get_matching_developers(json_response):
    """
    Get the matching developers based on the JSON response.

    Args:
        json_response (str): The JSON response.

    Returns:
        dict: The response dictionary containing the status and the data.

    """
    developers_df = pd.read_csv("Data/Developers.csv")
    response_dict = json.loads(json_response)
    tag_names = [tag["tag_name"] for tag in response_dict["tags"]]
    platform_names = [
        platform["platform_name"] for platform in response_dict["platforms"]
    ]

    developers_df["match_count"] = developers_df.apply(
        lambda row: sum(tag_name in row["list_tags"] for tag_name in tag_names)
        + sum(
            platform_name in row["list_platforms"] for platform_name in platform_names
        ),
        axis=1,
    )

    # Convert the comma-separated strings to arrays of strings
    developers_df["list_tags"] = developers_df["list_tags"].str.split(",")
    developers_df["list_platforms"] = developers_df["list_platforms"].str.split(",")

    matching_developers = developers_df[developers_df["match_count"] > 1]

    sorted_developers = matching_developers.sort_values(
        by=["match_count", "score"], ascending=[False, False]
    )
    response = {
        "status": "success",
        "data": json.loads(sorted_developers.to_json(orient="records")),
    }
    return response
