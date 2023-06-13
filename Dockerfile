# Use an official Python base image from the Docker Hub
FROM python:3.10.12-alpine3.18

# Install system dependencies
# Change this if the base image ever needs to update to something that isn't Alpine,
# as 'apk' is Alpine's package manager
RUN apk add --no-cache tini

# Create a non-root user and set permissions
RUN addgroup -S appuser
RUN adduser -S appuser
RUN chown appuser:appuser /home/appuser
WORKDIR /home/appuser

# Change to our user
USER appuser

# Activate a venv in our user's home dir
RUN python3 -m venv /home/appuser/venv

# Copy the application files into our user's home dir
COPY --chown=appuser:appuser . ./

# Copy the requirements.txt file and install the requirements
#COPY --chown=appuser:appuser requirements.txt .
RUN . /home/appuser/venv/bin/activate && \
    python -m pip install --no-cache-dir --upgrade pip && \
    python -m pip install --no-cache-dir -r requirements.txt

# Ensure proper handling of kernel signals - https://github.com/krallin/tini
ENTRYPOINT [ "tini", "--" ]

# Run it!
CMD . /home/appuser/venv/bin/activate && python3 -m main
