FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY services/ ./services/
USER 10001
CMD ["gunicorn", "--config", "services/gunicorn_conf.py", "--bind", "0.0.0.0:8000", "--workers", "2", "--access-logfile", "-", "--error-logfile", "-", "services.app:app"]
