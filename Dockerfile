# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.10-slim

# Expose port 5002 for the Flask app
EXPOSE 5002

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Create app directory
WORKDIR /app

# Install pip requirements
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

# Copy app source code
COPY . /app

# RUN pip install gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5002", "app:app"]
