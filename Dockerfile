FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /API

COPY . /API

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 80

CMD ["uvicorn", "API.main:app", "--host", "0.0.0.0", "--port", "80"]
