FROM python:3.12-slim
LABEL maintainer="orbik.rumlom22@gmail.com"

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      build-essential \
      libjpeg62-turbo \
      zlib1g \
 && rm -rf /var/lib/apt/lists/*

ARG INSTALL_DEV=false

COPY requirements.txt requirements.txt
COPY requirements.dev.txt requirements.dev.txt

RUN if [ "$INSTALL_DEV" = "true" ]; then \
        pip install -r requirements.dev.txt ; \
    else \
        pip install -r requirements.txt ; \
    fi

COPY . .