from flask import Flask, request, jsonify
import pandas as pd
import spacy
import json

app = Flask(__name__)

# Load the language model
nlp = spacy.load("en_core_web_sm")

# Load the Developers.csv file into a pandas DataFrame
developers_df = pd.read_csv("Developers.csv")


class EmptyPromptError(Exception):
    """Exception raised when the prompt is empty."""

    def __init__(self):
        self.message = "Empty prompt provided."


class NoMatchingDevelopersError(Exception):
    """Exception raised when no matching developers are found."""

    def __init__(self):
        self.message = "No matching developers found."


def get_relevant_tags(prompt):
    # Load the tags.csv file into a pandas DataFrame
    tags_df = pd.read_csv("tags.csv")

    # Extract relevant keywords using the language model
    keywords = extract_keywords(prompt)

    # Search for matching tags based on the extracted keywords
    matching_tags = []
    for index, row in tags_df.iterrows():
        tag_name = row["Tag name"]
        description = row["description"]
        if any(
            keyword.lower() in tag_name.lower()
            or (not pd.isnull(description) and keyword.lower() in description.lower())
            for keyword in keywords
        ):
            matching_tags.append(
                {
                    "tag_name": tag_name,
                    "emoji": row["emoji"],
                }
            )

    return matching_tags


def get_relevant_platforms(prompt):
    # Load the platforms.csv file into a pandas DataFrame
    platforms_df = pd.read_csv("platforms.csv")

    # Extract relevant keywords using the language model
    keywords = extract_keywords(prompt)

    # Search for matching platforms based on the extracted keywords
    matching_platforms = []
    for index, row in platforms_df.iterrows():
        platform_name = row["Name"]
        description = row["Description"]
        if any(
            keyword.lower() in platform_name.lower()
            or (not pd.isnull(description) and keyword.lower() in description.lower())
            for keyword in keywords
        ):
            matching_platforms.append(
                {
                    "platform_name": platform_name,
                }
            )

    return matching_platforms


def extract_keywords(prompt):
    # Use the language model to extract relevant keywords from the prompt
    doc = nlp(prompt)

    # Extract noun phrases and lemmatize them as keywords
    keywords = [token.lemma_ for token in doc if token.pos_ in ["NOUN", "PROPN"]]

    return keywords


def generate_json_response(tags, platforms):
    response = {"tags": tags, "platforms": platforms}
    return json.dumps(response)


def get_matching_developers(json_response):
    # Convert the JSON response to a dictionary
    response_dict = json.loads(json_response)

    # Get the tag names and platform names from the JSON response
    tag_names = [tag["tag_name"] for tag in response_dict["tags"]]
    platform_names = [
        platform["platform_name"] for platform in response_dict["platforms"]
    ]

    # Create a column to store the number of matching tags and platforms for each developer
    developers_df["match_count"] = developers_df.apply(
        lambda row: sum(tag_name in row["list_tags"] for tag_name in tag_names)
        + sum(
            platform_name in row["list_platforms"] for platform_name in platform_names
        ),
        axis=1,
    )

    # Filter the developers who have at least one matching tag or platform
    matching_developers = developers_df[developers_df["match_count"] > 1]

    # Sort the matching developers based on the number of matches and scores
    sorted_developers = matching_developers.sort_values(
        by=["match_count", "score"], ascending=[False, False]
    )

    # Create the response dictionary
    response = {
        "status": "success",
        "data": sorted_developers.to_dict(orient="records"),
    }

    return response


@app.route("/match_developers", methods=["POST"])
def match_developers():
    prompt = request.json.get("prompt")

    try:
        if not prompt:
            raise EmptyPromptError()

        relevant_tags = get_relevant_tags(prompt)
        relevant_platforms = get_relevant_platforms(prompt)

        json_response = generate_json_response(relevant_tags, relevant_platforms)

        matching_developers = get_matching_developers(json_response)

        if not matching_developers["data"]:
            raise NoMatchingDevelopersError()

        response = {
            "status": "success",
            "data": matching_developers["data"],
        }
        status_code = 200

    except EmptyPromptError as e:
        response = {
            "status": "error",
            "message": str(e.message),
        }
        status_code = 400

    except NoMatchingDevelopersError as e:
        response = {
            "status": "error",
            "message": str(e.message),
        }
        status_code = 404

    return jsonify(response), status_code


if __name__ == "__main__":
    app.run()
