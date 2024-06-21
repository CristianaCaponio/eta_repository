ARG PYTHON_VERSION=3.12
FROM python:${PYTHON_VERSION} as runner-image


ARG POETRY_VERSION=1.8.3
# python
ENV PYTHONUNBUFFERED=1 \
    # prevents python creating .pyc files
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_HOME="/.poetry" \
    POETRY_VERSION=${POETRY_VERSION} \
    POETRY_CACHE_DIR="~/.poetry_cache" \
    POETRY_VIRTUALENVS_IN_PROJECT=true

# make poetry available
ENV PATH="$POETRY_HOME/bin:$PATH"

RUN apt-get update && apt-get install --no-install-recommends -y \
    curl \
    git \
    nano \
    ssh \
    build-essential

RUN rm -rf /var/lib/apt/lists/*
RUN curl -sSL https://install.python-poetry.org | python3 -


FROM runner-image as test-image
WORKDIR /usr/src/app
COPY pyproject.toml .
COPY poetry.lock .
COPY . .
RUN poetry install

FROM test-image as main-image
CMD ["poetry", "run", "python", "eta_to_notification_develop/main.py"]