FROM python:3.12.5-slim-bullseye

WORKDIR /app

COPY requirements.txt /app
RUN python -m pip install --upgrade pip && python -m pip install -r requirements.txt --no-cache-dir

RUN apt-get update && apt-get install -y curl
RUN curl -fsSLo /app/Litton-7type-visual-landscape-model.pth https://lclab.thu.edu.tw/modelzoo/Litton-7type-visual-landscape-model.pth

RUN apt-get install -y cron
RUN echo "5 4 * * 0 find /tmp -type f -name 'LaDeco-*.csv' -delete" > /etc/cron.d/delete-ladeco-files

COPY app.py server.py /app/
COPY examples /app/examples

# mount run_database here
RUN mkdir -p /mnt/ai_data

EXPOSE 8000

HEALTHCHECK --interval=15m --timeout=5s CMD curl -f http://localhost:8000 || exit 1

ENTRYPOINT ["uvicorn", "server:app", "--host=0.0.0.0", "--port=8000"]
