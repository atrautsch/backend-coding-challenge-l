# TODO

- Add configurations for linter and formatter that the team agreed on
- Clean up fixtures in tests
- We could deploy the Docker container to a cloud environment. We could deploy Flask to a Container/VM and use uwsgi to run it and NGinx as a reverse proxy for SSL termination.
- Pagination is currently only implemented to test it. As we are searching we do not really need it as we always have to look at every gist.
- We could add rate limiting to the API, e.g., using flask-limiter
- We could cache responses from the Github API
- We could extend the /ping endpoint with more information and collect the data with Prometheus (or write a dedicated /metrics endpoint in OpenMetrics format)

