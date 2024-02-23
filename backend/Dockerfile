FROM python:3.11

WORKDIR /app
COPY backend backend
COPY db db

RUN pip install --no-cache-dir -r backend/requirements.txt
RUN pip install --no-cache-dir -r db/requirements.txt

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 backend.main:app
