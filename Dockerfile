FROM python:3.14-slim-bookworm

# Grab the uv binary from Astral's official image (handles dependency
# install/resolution much faster than plain pip).
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy ONLY the dependency files first. Docker caches each layer, so as
# long as pyproject.toml/uv.lock don't change, this layer is reused on
# every rebuild instead of reinstalling deps every time you edit code.
COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-install-project --no-dev

# Now copy the rest of the project (source code + data/*.json files).
COPY . .

RUN uv sync --frozen --no-dev

EXPOSE 8000

# We pass --host 0.0.0.0 explicitly - main.py's default is still
# "localhost", which is unreachable from outside the container. If this
# flag ever gets dropped, you're back to the "builds fine, can't connect"
# problem.
CMD ["uv", "run", "python", "main.py", "--host", "0.0.0.0", "--port", "8000"]