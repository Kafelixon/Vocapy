# Use the official fastapi uvicorn image
FROM tiangolo/uvicorn-gunicorn-fastapi:latest

# Copy the local directory’s contents into the container at /app
COPY ./ /app

# Set the working directory in the container to /app
WORKDIR /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Command to run the application using uvicorn
CMD ["uvicorn", "api.server:app", "--host", "0.0.0.0", "--port", "8000"]
