FROM python:3.13-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
ENV POSTGRES_DB=postgresql
ENV POSTGRES_USER=postgresql
ENV POSTGRES_PASSWORD=1234
ENV POSTGRES_HOST=localhost
ENV POSTGRES_PORT=5432
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

