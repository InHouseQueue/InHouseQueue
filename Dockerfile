FROM python:3.9-slim-buster

WORKDIR /app

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . .

RUN adduser --system henry
USER henry

CMD ["python3", "main.py"]