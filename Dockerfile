FROM python:3.8-alpine

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN export FLASK_APP=tasks
RUN export FLASK_ENV=development
RUN apk --no-cache add --virtual build-dependencies gcc libffi-dev python3-dev musl-dev postgresql-dev

RUN pip install --upgrade pip
COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt

COPY . /usr/src/app
EXPOSE 5000