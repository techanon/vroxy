FROM python:3.9.13 as base

WORKDIR /vroxy

COPY requirements.txt ./
RUN pip install -r requirements.txt

FROM base as dev

COPY requirements_dev.txt ./
RUN pip install -r requirements_dev.txt