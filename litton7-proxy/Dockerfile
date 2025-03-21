# LaDeco-Public proxy for Synology NAS
# see README.md for recommanded build command
FROM python:3.12.9-slim-bullseye

RUN apt-get update && apt-get install -y curl

WORKDIR /app
COPY requirements.txt /app/
RUN python -m pip install --upgrade pip && python -m pip install -r /app/requirements.txt --no-cache-dir

COPY webui.py serve.sh server.py /app/
COPY examples/* /app/examples/

EXPOSE 8000

HEALTHCHECK --interval=15m --timeout=3s CMD curl -f http://localhost:8000/healthcheck || exit 1

ENTRYPOINT ["/bin/bash", "/app/serve.sh"]
