FROM python:3.9-slim

LABEL maintainer="enchant97"

EXPOSE 8080

# setup python environment
COPY requirements.txt requirements.txt

# build/add base-requirements
# also allow for DOCKER_BUILDKIT=1 to be used
RUN --mount=type=cache,target=/root/.cache \
    pip install -r requirements.txt

# add extra requirements
COPY optional-requirements.txt optional-requirements.txt
RUN --mount=type=cache,target=/root/.cache \
    pip install -r optional-requirements.txt

# copy the flask app files
COPY HomeTerminal HomeTerminal

CMD gunicorn -b 0.0.0.0:8080 -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker -w 1 'HomeTerminal:create_app()'
