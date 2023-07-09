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
    create_response,
)
from middlewares import forbidden_words_middleware

app = Flask(__name__)


@app.before_request
def before_request():
    try:
        forbidden_words_middleware()
    except ForbiddenWordsError as e:
        return create_response(str(e.message), 403)


@app.route("/match_developers", methods=["GET"])
def match_developers():
    prompt = request.args.get("prompt")

    try:
        if not prompt:
            raise EmptyPromptError()

        keywords = extract_keywords(prompt)

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

        return create_response(matching_developers["data"], 200)

    except (EmptyPromptError, NoMatchingDevelopersError, IncompletePromptError) as e:
        status_code = (
            400
            if isinstance(e, EmptyPromptError)
            else 404
            if isinstance(e, NoMatchingDevelopersError)
            else 422
        )
        return create_response(str(e.message), status_code)


if __name__ == "__main__":
    app.run()
