FROM python:3.11

# Install distutils jika diperlukan
RUN apt-get update && apt-get install -y python3-distutils

# Upgrade pip dan setuptools
RUN pip install --upgrade pip setuptools

# Set working directory
WORKDIR /app

# Copy requirements.txt dan install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy sisa aplikasi
COPY . .

# Command untuk menjalankan aplikasi
CMD ["python", "app.py"]