
FROM python:3.12-slim

WORKDIR /app

COPY app.py .

ENV PORT=5001
ENV DATA_DIR=/var/lib/backend_data

EXPOSE 5001

CMD ["python", "app.py"]
