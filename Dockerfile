# Use an official Python runtime as a parent image
FROM python:3.10.0

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Copy the application files into the container at /app
COPY ./app /app

# Copy SSL certificates into the container
COPY ./app/nba_notifier/ssl /ssl

# Make the root file system writable (if necessary)
USER root
RUN chmod 777 /

# Install any needed packages specified in requirements.txt
RUN pip install  -r /app/nba_notifier/requirements.txt

# Expose the port the app runs on
EXPOSE 8001

# Run the application
CMD ["python", "manage.py", "runsslserver", "0.0.0.0:8001", "--certificate", "/ssl/localhost.crt", "--key", "/ssl/localhost.key"]

