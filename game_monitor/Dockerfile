Dockerfile
FROM python:3.10 AS builder  # Build stage
WORKDIR /app
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY . .

FROM python:3.8  # Final stage
WORKDIR /app
COPY --from=builder /app .
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
