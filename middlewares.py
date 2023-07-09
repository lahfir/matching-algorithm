from flask import request
from better_profanity import profanity
from CustomErrors import ForbiddenWordsError


def forbidden_words_middleware():
    prompt = request.args.get("prompt")

    if prompt and profanity.contains_profanity(prompt):
        raise ForbiddenWordsError()
