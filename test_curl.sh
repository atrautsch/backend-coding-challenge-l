#!/bin/bash
curl --header "Content-Type: application/json" \
  --request POST \
  --data '{"username":"justdionysus","pattern":"import requests"}' \
  http://127.0.0.1:9876/api/v1/search
