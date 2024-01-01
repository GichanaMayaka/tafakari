FROM  python:3.10.6-slim-bullseye

ARG ENV

ENV ENV=${ENV} \
    FLASK_APP=tafakari \
    PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.2.2 \
    WORKING_DIR=/usr/src/app/tafakari/

RUN apt-get update \
    && apt-get install -y libpq-dev \
    && apt-get install -y gcc

WORKDIR $WORKING_DIR

COPY . .

# System deps:
RUN pip install "poetry==$POETRY_VERSION" && \
    poetry config virtualenvs.create false  \
    && poetry install $(test "$ENV" == prod && echo "--no-dev") --no-interaction --no-ansi

EXPOSE 8000

RUN chmod +x init.sh

ENTRYPOINT ["sh", "init.sh"]
