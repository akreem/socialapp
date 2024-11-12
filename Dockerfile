# Use an official Python image as the base
FROM python:3.8-slim

# Set the working directory
WORKDIR /app

# Copy the app code and install dependencies
COPY . /app
RUN pip install Flask pymongo

# Run the Flask app
CMD ["python", "app.py"]
