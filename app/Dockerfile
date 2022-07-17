FROM python:3.8


COPY . /src/app

RUN pip install --no-cache-dir -r src/app/requirements.txt

ENV PYTHONPATH "${PYTHONPATH}:/src"

WORKDIR /src/app

