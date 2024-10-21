ARG ALPINE_MAJ_MIN_VERSION="3.20"
ARG PYTHON_MAJ_MIN_VERSION="3.12"

ARG BASE_IMAGE=python:${PYTHON_MAJ_MIN_VERSION}-alpine${ALPINE_MAJ_MIN_VERSION}

# ------------------------------------------------------------------------
FROM ${BASE_IMAGE} AS poetry-image

RUN pip install poetry

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY --link poetry.lock pyproject.toml README.md /app/

RUN poetry install --no-root && rm -rf /tmp/poetry_cache


FROM ${BASE_IMAGE} AS runtime

ENV VIRTUAL_ENV=/app/.venv PATH="/app/.venv/bin:$PATH"

COPY --from=poetry-image ${VIRTUAL_ENV} ${VIRTUAL_ENV}
COPY --link validation_framework/ ./validation_framework
COPY --link conf/targets ./conf/targets

ENTRYPOINT ["python", "-m", "validation_framework"]
