FROM python:3.12-slim

# Don't write .pyc files; flush stdout/stderr so logs show up live.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install deps first so the layer caches when only source changes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Run as a non-root user.
RUN useradd --create-home --uid 10001 botuser && chown -R botuser:botuser /app
USER botuser

CMD ["python", "bot.py"]
