"""
Exposes a simple HTTP API to search a users Gists via a regular expression.

Github provides the Gist service as a pastebin analog for sharing code and
other develpment artifacts.  See http://gist.github.com for details.  This
module implements a Flask server exposing two endpoints: a simple ping
endpoint to verify the server is up and responding and a search endpoint
providing a search across all public Gists for a given Github account.
"""

import re

import requests
from flask import Flask, jsonify, request

app = Flask(__name__)


class GistApiException(Exception):
    """Simple Exception so that we get the status code we want."""

    def __init__(self, status_code, message):
        super().__init__(message)
        self.status_code = status_code


@app.route("/ping")
def ping():
    """Provide a static response to a simple GET request."""
    return "pong"


def get_next_link(link: str) -> str:
    """Get next link of pagination header from the Github API."""
    match = re.match(r'<(.*)>; rel="next",', link)
    next_link = ""
    if match:
        next_link = match.group(1)
    return next_link


def gists_for_user(username: str, per_page: int = 100, page: int = 1) -> list:
    """Provides the list of gist metadata for a given user.

    This abstracts the /users/:username/gist endpoint from the Github API.
    See https://developer.github.com/v3/gists/#list-a-users-gists for
    more information.

    Args:
        username (string): the user to query gists for
        page (int): current page for pagination
        per_page (int): number of items per page for pagination

    Returns:
        A list from the json response from the Github API.  See
        the above URL for details of the expected structure.
    """
    gists = []
    gists_url = (
        f"https://api.github.com/users/{username}/gists?page={page}&per_page={per_page}"
    )
    response = requests.get(gists_url, timeout=60)
    if not response.ok:
        raise GistApiException(response.status_code, response.content)

    gists.extend(response.json())
    next_link = get_next_link(response.headers.get("link", ""))
    while next_link:
        response = requests.get(next_link, timeout=60)
        gists.extend(response.json())
        next_link = get_next_link(response.headers.get("link", ""))
    return gists


def raw_gist(raw_url: str) -> str:
    """Return full gist if content is truncated."""
    response = requests.get(raw_url, timeout=60)
    if not response.ok:
        raise GistApiException(response.status_code, response.content)
    return response.content.decode('utf-8')


@app.route("/api/v1/search", methods=["POST"])
def search():
    """Provides matches for a single pattern across a single users gists.

    Pulls down a list of all gists for a given user and then searches
    each gist for a given regular expression.

    Returns:
        A Flask Response object of type application/json.  The result
        object contains the list of matches along with a 'status' key
        indicating any failure conditions.
    """
    post_data = request.get_json()

    username = post_data["username"]
    pattern = post_data["pattern"]
    if not username or not pattern:
        return jsonify({"status": "error", "message": "No username or pattern"}), 400

    result = {}
    gists = gists_for_user(username)

    matches = []
    cpattern = re.compile(pattern)
    for gist in gists:
        for _file, fgist in gist["files"].items():
            content = raw_gist(fgist["raw_url"])
            match = re.search(cpattern, content)
            if match:
                matches.append({"raw_url": fgist["raw_url"]})
                continue  # we only need one content match for the whole gist

    result["status"] = "success"
    result["username"] = username
    result["pattern"] = pattern
    result["matches"] = matches

    return jsonify(result)


@app.errorhandler(Exception)
def handle_exception(e):
    """We just want to quickly get errors here without handling."""
    return jsonify({"status": "error", "message": str(e)}), 500


@app.errorhandler(GistApiException)
def handle_gistapi_exception(e):
    """Just to get the status_code."""
    return jsonify({"status": "error", "message": str(e)}), e.status_code


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=9876)
