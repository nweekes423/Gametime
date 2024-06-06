# Use an official nginx image as a parent image
FROM nginx:latest

# Copy Nginx configuration file
COPY nginx.conf /etc/nginx/nginx.conf

# Ensure the SSL directory exists (if needed)
RUN mkdir -p /etc/nginx/ssl

