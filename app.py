from flask import Flask, request, jsonify
from CustomErrors import (
    EmptyPromptError,
    IncompletePromptError,
    NoMatchingDevelopersError,
    ForbiddenWordsError,
)
from utils import (
    extract_keywords,
    generate_json_response,
    get_matching_developers,
    get_relevant_tags,
    get_relevant_platforms,
)
from middlewares import forbidden_words_middleware

app = Flask(__name__)


@app.before_request
def before_request():
    try:
        forbidden_words_middleware()
    except ForbiddenWordsError as e:
        return jsonify({"status": "error", "message": str(e.message)}), 403


@app.route("/match_developers", methods=["GET"])
def match_developers():
    prompt = request.args.get("prompt")

    try:
        if not prompt:
            raise EmptyPromptError()

        # Extract keywords from the prompt
        keywords = extract_keywords(prompt)

        # Check if the keywords are empty or contain generic phrases
        if not keywords or all(
            keyword.lower() in ["i want", "i need"] for keyword in keywords
        ):
            raise IncompletePromptError()

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

    except IncompletePromptError as e:
        response = {
            "status": "error",
            "message": str(e.message),
        }
        status_code = 422

    return jsonify(response), status_code


if __name__ == "__main__":
    app.run(debug=True)
