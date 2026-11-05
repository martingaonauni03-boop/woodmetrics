FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY woodmetrics ./woodmetrics
COPY wsgi.py .
RUN useradd --create-home appuser && mkdir -p /data && chown appuser:appuser /data
USER appuser
ENV DATABASE_PATH=/data/woodmetrics.sqlite
EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "1", "wsgi:app"]
