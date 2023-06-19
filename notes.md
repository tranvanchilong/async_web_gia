# Docker

## Test moi truong docker

docker run --name crawl_findthisbest -p 5001:8000 -it -v ${PWD}/app:/app:rw python:3.10.6-slim-bullseye /bin/bash

## Build image sau khi test ok, va day len gitlab

docker login registry.gitlab.com
docker build -t registry.gitlab.com/q347/crawl_findthisbest:v0.3 .

## Test image tren gitlab

docker run --name crawl_findthisbest -p 5001:8000 -it -v ${PWD}/app:/app:rw registry.gitlab.com/q347/crawl_findthisbest:v0.3 /bin/bash

## Test docker-compose

docker-compose -f docker-compose-test.yml up

## Push image len gitlab

docker push registry.gitlab.com/q347/crawl_findthisbest:v0.3

# Run starlette

uvicorn app:app --reload --host 0.0.0.0 --port 8000

vvZ2b&5z!nw9Le
