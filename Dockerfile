FROM python:3.12

RUN apt-get update && apt-get install -y \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1

WORKDIR /shop_api
COPY requirements.txt /shop_api/
RUN pip install --no-cache-dir -r requirements.txt
COPY . /shop_api/

RUN python manage.py collectstatic --noinput

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]