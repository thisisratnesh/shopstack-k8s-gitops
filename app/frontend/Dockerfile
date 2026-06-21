# Use nginx as the base image for serving static frontend files.
FROM nginx:1.27-alpine

# Copy our custom nginx configuration into the container.
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy frontend static files into nginx's default web root directory.
COPY index.html /usr/share/nginx/html/index.html
COPY app.js /usr/share/nginx/html/app.js

# Expose port 80 because nginx will serve the frontend on port 80.
EXPOSE 80