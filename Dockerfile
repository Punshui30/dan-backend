FROM python:3.10-slim

# Install system packages
RUN apt-get update && apt-get install -y git gcc && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# 👇 Tell Render what port this app exposes
EXPOSE 8080

# 👇 Start the app on the correct port
CMD ["uvicorn", "main_dan_with_learning:app", "--host", "0.0.0.0", "--port", "8080"]
