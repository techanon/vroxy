FROM python:3.10.6 as base

WORKDIR /vroxy
CMD ["python", "-u", "vroxy.py"]

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

FROM base as dev

COPY requirements_dev.txt ./
RUN pip install -r requirements_dev.txt