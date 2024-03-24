# Use an official Python runtime as a parent image
FROM python:3

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
#COPY . /app

# Make the root file system writable
USER root
RUN chmod 777 /

# List contents of /app directory to troubleshoot
RUN ls -lrt /
RUN ls -lrt /app/
# Install any needed packages specified in requirements.txt
USER root
#RUN pip cache purge
#RUN pip install -r /app/requirements.txt

# Expose the port the app runs on
EXPOSE 8000

# Run the application
CMD ["python", "manage.py", "runserver"]

