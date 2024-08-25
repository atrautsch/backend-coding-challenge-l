# gistapi

## Create venv, install dependencies
```bash
python -m venv .
source bin/activate
pip install -r requirements.txt
```

## Run app
```bash
source bin/activate
python gistapi/gistapi.py
```

## Tooling and tests

### Run tests
```bash
source bin/activate
python -m unittest

# run single test
# python -m unittest tests.test_gist_search.TestApp.test_ping
```

### Run tests with coverage
```bash
source bin/activate
python -m coverage run -m unittest
python -m coverage report
```

### Run pylint
```bash
source bin/activate
python -m pylint gistapi
```

### Run black
```bash
source bin/activate
python -m black gistapi
```

## Docker

## Build image
```bash
docker build -t gistapi .
```

## Run from image
```bash
docker run -p 9876:9876 gistapi
```
