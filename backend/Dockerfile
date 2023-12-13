FROM python:3.11
WORKDIR /app
RUN pip install gunicorn==20.1.0

COPY requirements.txt .

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install -r requirements.txt --no-cache-dir
COPY . .
RUN python3 manage.py collectstatic --noinput

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "foodgram.wsgi"]
