ARG PYTHON_VERSION=3.10

FROM python:${PYTHON_VERSION} as builder

    WORKDIR /app

    RUN apt-get update && apt-get install -y libpq-dev && rm -rf /var/lib/apt/lists/*

    COPY requirements.txt .
    COPY optional-requirements.txt .

    RUN python -m venv .venv
    ENV PATH="/app/.venv/bin:$PATH"

    RUN --mount=type=cache,target=/root/.cache pip install -r requirements.txt -r optional-requirements.txt

FROM python:${PYTHON_VERSION}-slim

    WORKDIR /app
    EXPOSE 8080
    ENV PATH="/app/.venv/bin:$PATH"

    RUN apt-get update && apt-get install -y libpq5 && rm -rf /var/lib/apt/lists/*

    COPY --from=builder /app/.venv .venv

    COPY hts hts

    CMD gunicorn -b 0.0.0.0:8080 -w 1 --worker-class gevent 'hts:create_app()'
