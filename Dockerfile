FROM python:3.11.4-alpine

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apk add --no-cache netcat-openbsd postgresql-client gcc musl-dev libffi-dev

# Upgrade pip
RUN pip install --upgrade pip

# Install Python dependencies
COPY ./requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

# Copy app files and entrypoint script
COPY . .

# Move entrypoint outside of app volume
COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
