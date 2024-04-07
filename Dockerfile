# Use an official Python runtime as a parent image
FROM python:3.10.0

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Copy the application files into the container at /app
COPY app /app

# Install any needed packages specified in requirements.txt
RUN pip install -r /app/nba_notifier/requirements.txt

# Expose the port the app runs on
EXPOSE 8000

# Run the application without SSL
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

