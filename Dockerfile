FROM python:3.14-slim

# UV_PYTHON_DOWNLOADS=never: use the image's Python. One downloaded by uv would land in /root, unreadable by the app user.
ENV UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=never PYTHONUNBUFFERED=1
RUN pip install --no-cache-dir uv==0.12.5

WORKDIR /app
COPY pyproject.toml uv.lock .python-version ./
RUN uv sync --frozen --no-dev --no-install-project
COPY . .

RUN useradd --create-home app
USER app

EXPOSE 8501
HEALTHCHECK --interval=30s --timeout=3s --start-period=20s \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8501/_stcore/health')"

# Weights are not in the image: compose.yaml mounts them read-only.
CMD [".venv/bin/streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501", "--server.headless=true"]
