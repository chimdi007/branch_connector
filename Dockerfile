# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install the dependencies in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install curl
RUN apt-get update && apt-get install -y curl

# Expose the port that the app listens on
EXPOSE 4000

# Define environment variable
ENV PYTHONUNBUFFERED=1

# Run the app on port 6600
CMD ["python", "app.py"]
