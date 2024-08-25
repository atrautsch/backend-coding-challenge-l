import json
import unittest

from unittest.mock import patch, Mock

from gistapi.gistapi import app, gists_for_user

# todo: load fixtures before
def mock_responses(*args, **kwargs):
    """We load responses from the fixtures here."""
    m = Mock()
    # pagination test with headers
    if args[0].endswith(
        "https://api.github.com/users/monalisa/gists?page=1&per_page=1"
    ):
        with open("./tests/fixtures/list_gists1.json", "r", encoding="utf-8") as f:
            m.return_value.json.return_value = json.load(f)
            m.return_value.status_code = 200
            m.return_value.ok = True
            m.return_value.headers = {
                "link": '<https://api.github.com/users/monalisa/gists?page=2&per_page=1>; rel="next", <https://api.github.com/users/monalisa/gists?page=2&per_page=1>; rel="last"'
            }
    elif args[0].endswith(
        "https://api.github.com/users/monalisa/gists?page=2&per_page=1"
    ):
        with open("./tests/fixtures/list_gists2.json", "r", encoding="utf-8") as f:
            m.return_value.json.return_value = json.load(f)
            m.return_value.status_code = 200
            m.return_value.ok = True
            m.return_value.headers = {
                "link": '<https://api.github.com/users/monalisa/gists?page=1&per_page=1>; rel="prev", <https://api.github.com/users/monalisa/gists?page=1&per_page=1>; rel="first"'
            }
    # raw content return
    elif args[0].startswith("https://gist.githubusercontent.com/"):
        with open("./tests/fixtures/raw_content.text", "rb") as f:
            m.return_value.content = f.read()
            m.return_value.ok = True
            m.return_value.status_code = 200
    # just list of gists
    elif args[0].startswith("https://api.github.com/users/monalisa/gists"):
        with open("./tests/fixtures/list_gists.json", "r", encoding="utf-8") as f:
            m.return_value.json.return_value = json.load(f)
            m.return_value.status_code = 200
            m.return_value.ok = True
            m.return_value.headers = {
                "link": '<https://api.github.com/users/monalisa/gists?page=1&per_page=1>; rel="first"'
            }
    # wrong user
    elif args[0].startswith("https://api.github.com/users/aaaaaaabbc33sdf/gists"):
        m.return_value.status_code = 404
        m.return_value.ok = False
        m.return_value.json.return_value = {'message': 'No such user'}
    return m.return_value


class TestApp(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_ping(self):
        """Test our simple ping/pong."""
        response = self.client.get("/ping")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, "pong")

    @patch("gistapi.gistapi.requests.get", side_effect=mock_responses)
    def test_search_gists(self, _mock_list_gist):
        """Test searching for patterns in gists."""
        response = self.client.post(
            "/api/v1/search",
            json={"username": "monalisa", "pattern": ".*port requests.*"},
        )
        data = response.json

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["status"], "success")
        self.assertEqual(len(data["matches"]), 1)
        # todo: use data from the fixture
        self.assertEqual(
            data["matches"][0]["raw_url"],
            "https://gist.githubusercontent.com/octocat/6cad326836d38bd3a7ae/raw/db9c55113504e46fa076e7df3a04ce592e2e86d8/hello_world.rb",
        )

    def test_search_gists_empty_pattern(self):
        """Search with empty pattern."""
        response = self.client.post(
            "/api/v1/search",
            json={"username": "monalisa", "pattern": ""},
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['status'], 'error')


    def test_search_gists_empty_username(self):
        """Search with empty username."""
        response = self.client.post(
            "/api/v1/search",
            json={"username": "", "pattern": ".*"},
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['status'], 'error')


    @patch("gistapi.gistapi.requests.get", side_effect=mock_responses)
    def test_search_wrong_username(self, _mock_list_gist):
        """Search with non existant username."""
        response = self.client.post(
            "/api/v1/search",
            json={"username": "aaaaaaabbc33sdf", "pattern": ".*"},
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json['status'], 'error')

    @patch("gistapi.gistapi.requests.get", side_effect=mock_responses)
    def test_pagination(self, _mock_list_gist):
        """Paginate use in ."""
        gists = gists_for_user('monalisa', per_page=1, page=1)
        self.assertEqual(len(gists), 2)

if __name__ == "__main__":
    unittest.main()
