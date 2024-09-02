FROM python:3.9-slim AS production

ENV PYTHONUNBUFFERED=1
WORKDIR /app

# system dependencies for postgres
RUN apt-get update && \
    apt-get install -y \
    bash \
    build-essential \
    gcc \
    libffi-dev \
    musl-dev \
    openssl \
    postgresql \
    libpq-dev

COPY requirements/prod.txt .requirements/prod.txt
RUN pip install -r .requirements/prod.txt

COPY manage.py ./manage.py
COPY flower_shop_website ./flower_shop_website
COPY flower_database_backend ./flower_database_backend

EXPOSE 8000

FROM production AS development

COPY requirements/dev.txt .requirements/dev.txt
RUN pip install -r .requirements/dev.txt
COPY . .

# run commands
# docker build -t myapp .
# where myapp is name of image, could be any name
# docker run -d -p 8000:8000 myapp
# docker ps to check status of port
#  0.0.0.0:8000->8000/tcp means it worked, use localhost:8000 to access