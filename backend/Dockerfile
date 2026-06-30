FROM python:3.14-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        fonts-noto-cjk \
        libpq-dev \
        libreoffice-impress \
        libreoffice-writer \
        netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

COPY requirements/base.txt requirements/base.txt
RUN pip install -r requirements/base.txt

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

FROM base AS dev
COPY requirements/dev.txt requirements/dev.txt
RUN pip install -r requirements/dev.txt
COPY . /app

FROM base AS prod
COPY requirements/prod.txt requirements/prod.txt
RUN pip install -r requirements/prod.txt
COPY . /app
