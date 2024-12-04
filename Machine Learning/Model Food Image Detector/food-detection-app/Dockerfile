# Gunakan image dasar Python
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Salin file requirements.txt dan install dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Salin semua file aplikasi ke dalam container
COPY . .

# Buat direktori uploads
RUN mkdir uploads

# Expose port yang digunakan oleh Flask
EXPOSE 5000

# Perintah untuk menjalankan aplikasi Flask
CMD ["python", "app.py"]