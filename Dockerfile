FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /backend

COPY . /backend

# Install any needed packages specified in requirements.txt
# Note: The requirements.txt file must be present in the directory where you build the Docker image
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable
ENV FLASK_ENV=development