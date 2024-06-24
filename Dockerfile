# Use an official Python runtime as a parent image
FROM python:3.10.0

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /Gametime

# Install dependencies and manage keyring files
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && curl -fsSL https://ftp-master.debian.org/keys/archive-key-10.asc | gpg --dearmor -o /usr/share/keyrings/debian-archive-buster-keyring.gpg \
    && curl -fsSL https://ftp-master.debian.org/keys/archive-key-11.asc | gpg --dearmor -o /usr/share/keyrings/debian-archive-bullseye-keyring.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/debian-archive-buster-keyring.gpg] http://deb.debian.org/debian buster main" > /etc/apt/sources.list.d/debian-buster.list \
    && echo "deb [signed-by=/usr/share/keyrings/debian-archive-bullseye-keyring.gpg] http://deb.debian.org/debian bullseye main" > /etc/apt/sources.list.d/debian-bullseye.list \
    && apt-get update && apt-get install -y --no-install-recommends \
    nginx \
    && rm -rf /var/lib/apt/lists/*

# Copy the application files into the container at /Gametime
COPY . /Gametime

# Copy SSL certificates for Nginx
RUN mkdir -p /usr/local/etc/ssl/certs/ /usr/local/etc/ssl/private/
COPY ./ssl/self-signed.crt /usr/local/etc/ssl/certs/self-signed.crt
COPY ./ssl/self-signed.key /usr/local/etc/ssl/private/self-signed.key

# Install Python packages
RUN pip install --upgrade pip
RUN pip install -r app/nba_notifier/requirements.txt

# Copy Nginx configuration file
COPY nginx.conf /etc/nginx/nginx.conf

# Expose the port the app runs on
EXPOSE 8000

# Run the application with SSL using Gunicorn
CMD ["gunicorn", "--chdir", "app", "--bind", "0.0.0.0:8000", "--certfile", "/usr/local/etc/ssl/certs/self-signed.crt", "--keyfile", "/usr/local/etc/ssl/private/self-signed.key", "nba_notifier.wsgi:application"]

