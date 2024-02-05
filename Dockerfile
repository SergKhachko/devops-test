FROM python:3.10-alpine
RUN apk add curl
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false
WORKDIR /app
COPY pyproject.toml poetry.lock* /app/
RUN poetry install --no-root --only main
ADD . .
ENTRYPOINT ["uvicorn"]
CMD ["main:app", "--host", "0.0.0.0"]
