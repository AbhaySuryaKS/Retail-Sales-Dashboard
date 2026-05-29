FROM python:3.11-slim
WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . /app

ENV PYTHONUNBUFFERED=1
ENV PORT=8050

EXPOSE 8050

# Use gunicorn to run the WSGI server
CMD ["gunicorn", "wsgi:app", "-b", "0.0.0.0:8050", "--workers", "4", "--threads", "4"]
