FROM python:3.10-slim

RUN apt-get update && apt-get install -y git gcc && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 👇 Change the port here from 8000 → 8080
CMD ["uvicorn", "main_dan_with_learning:app", "--host", "0.0.0.0", "--port", "8080"]
