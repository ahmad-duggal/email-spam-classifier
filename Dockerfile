# Use an official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project into the container
COPY . .

# Expose ports for FastAPI and Streamlit
EXPOSE 8000
EXPOSE 8501

# The execution command is handled by docker-compose, 
# but we can set a default CMD to run the FastAPI server
CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8000"]
