# Use the base Python image
FROM python:3.12.6

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file into the container
COPY requirements.txt .

# Install the dependencies listed in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application files into the container
COPY . .

# Expose Flask port (default: 5000)
EXPOSE 5000

# Specify the command to run the Flask application
CMD ["python", "app.py"]
