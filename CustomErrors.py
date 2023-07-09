class IncompletePromptError(Exception):
    """Exception raised when the prompt is Incomplete."""

    def __init__(self):
        self.message = "Seems like you've given less information. Can you elaborate and give some keywords related to your need and we can find the best match for you!"


class EmptyPromptError(Exception):
    """Exception raised when the prompt is empty."""

    def __init__(self):
        self.message = "Empty prompt provided."


class NoMatchingDevelopersError(Exception):
    """Exception raised when no matching developers are found."""

    def __init__(self):
        self.message = "No matching developers found."


class ForbiddenWordsError(Exception):
    def __init__(
        self,
        message="Your request contains forbidden words. Please remove them and try again.",
    ):
        self.message = message
        super().__init__(self.message)
