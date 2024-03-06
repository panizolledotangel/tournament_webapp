FROM python:3.11.6-alpine

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY webapp .

ENV FLASK_ENV=production
ENV FLASK_APP=main_app.py
ENV FLASK_RUN_PORT=8080
ENV FLASK_RUN_HOST=0.0.0.0

CMD ["flask", "run"] 