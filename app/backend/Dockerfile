# Use an official Python base image.
# Python 3.11 is a good stable choice for this project.
FROM python:3.11-slim

# Set the working directory inside the container.
# All following commands will run from this folder unless changed.
WORKDIR /app

# Copy the requirements file first.
# This is done before copying the whole source code so Docker layer caching
# can be more efficient when only application code changes.
COPY requirements.txt /app/requirements.txt

# Install Python dependencies.
# --no-cache-dir keeps the image smaller by avoiding pip cache storage.
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the backend application source code into the container.
COPY main.py /app/main.py

# Expose port 8000 for documentation/readability.
# This does not publish the port by itself, but clearly communicates that
# the application inside the container listens on 8000.
EXPOSE 8000

# Start the FastAPI application using uvicorn.
#
# Important:
# - main:app  -> file "main.py", object "app"
# - host 0.0.0.0 -> listen on all interfaces inside container
# - port 8000 -> backend application port
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]