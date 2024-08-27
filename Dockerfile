FROM python:3.9

WORKDIR /app

RUN apt-get update && apt-get install -y netcat-openbsd

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY data_generator.py .

CMD ["python", "data_generator.py"]
