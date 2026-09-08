# syntax=docker/dockerfile:1.7
FROM python:3.14-slim AS base

ARG DEBIAN_MIRROR=http://mirrors.cloud.tencent.com/debian
ARG DEBIAN_SECURITY_MIRROR=http://mirrors.cloud.tencent.com/debian-security
ARG PIP_INDEX_URL=https://mirrors.cloud.tencent.com/pypi/simple

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=120 \
    PIP_RETRIES=5 \
    PIP_INDEX_URL=${PIP_INDEX_URL}

WORKDIR /app

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    sed -i \
        -e "s|http://deb.debian.org/debian-security|${DEBIAN_SECURITY_MIRROR}|g" \
        -e "s|http://deb.debian.org/debian|${DEBIAN_MIRROR}|g" \
        /etc/apt/sources.list.d/debian.sources \
    && apt-get -o Acquire::Retries=5 -o Acquire::http::Timeout=60 update \
    && apt-get -o Acquire::Retries=5 -o Acquire::http::Timeout=60 install -y --no-install-recommends \
        fonts-noto-cjk \
        libreoffice-impress \
        libreoffice-writer \
        netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

COPY requirements/base.txt requirements/base.txt
RUN --mount=type=cache,target=/root/.cache/pip,sharing=locked \
    pip install -r requirements/base.txt

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

FROM base AS dev
COPY requirements/dev.txt requirements/dev.txt
RUN --mount=type=cache,target=/root/.cache/pip,sharing=locked \
    pip install -r requirements/dev.txt
COPY . /app

FROM base AS prod
COPY requirements/prod.txt requirements/prod.txt
RUN --mount=type=cache,target=/root/.cache/pip,sharing=locked \
    pip install -r requirements/prod.txt
COPY . /app
