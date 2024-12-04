# Gunakan image Python 3.10
FROM python:3.10-slim

# Set working directory di dalam container
WORKDIR /app

# Salin file requirements.txt ke dalam container
COPY . /app/

# Install semua dependensi yang ada di requirements.txt
RUN pip install --no-cache-dir -r requirements.txt


# Tentukan port yang digunakan oleh Flask
EXPOSE 5000

# Jalankan aplikasi Flask
CMD ["python", "app.py", "run", "--host=0.0.0.0"]
