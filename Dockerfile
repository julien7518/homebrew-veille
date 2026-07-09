FROM python:3.14-slim

RUN pip install uv --no-cache-dir

WORKDIR /app
COPY pyproject.toml ./
RUN uv sync --no-dev --no-install-project

COPY . .
RUN uv sync --no-dev

EXPOSE 8080

ENV TZ=Europe/Paris
ENV DB_PATH=DB/veille.db

CMD ["uv", "run", "main.py"]
