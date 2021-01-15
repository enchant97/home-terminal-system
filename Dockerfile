FROM python:3.8.6-buster

LABEL maintainer="enchant97"

EXPOSE 8080

# setup python environment
COPY requirements.txt requirements.txt

# build/add base-requirements
RUN ["pip", "install", "-r", "requirements.txt"]

# add extra requirements
COPY optional-requirements.txt optional-requirements.txt
RUN ["pip", "install", "-r", "optional-requirements.txt"]

# copy the flask app files
COPY HomeTerminal HomeTerminal

CMD gunicorn --log-level info -b 0.0.0.0:8080 -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker -w 1 'HomeTerminal:create_app()'
HEALTHCHECK CMD curl --fail http://localhost:8080/api/is-healthy || exit 1
