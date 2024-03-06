# Use an official Python runtime as a parent image
FROM python:3.8-slim-buster

# Set the working directory in the container to /mbapi
WORKDIR /mbapi

# Add the current directory contents into the container at /mbapi
ADD . /mbapi

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Run mb_api.py when the container launches
CMD ["python", "mb_api.py"]