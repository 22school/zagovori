FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

VOLUME ["/app/data"]

ENV DATABASE_URL=/app/data/bot.db
ENV USE_REDIS=false

CMD ["python", "bot/run.py"] 