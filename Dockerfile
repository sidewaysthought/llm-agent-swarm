# Use an official Python base image from the Docker Hub
FROM python:3.10.12-alpine3.18

# Install system dependencies - change this if the base image ever needs to update to something that isn't alpine
RUN apk add --no-cache tini

# Set environment variables
ENV PIP_NO_CACHE_DIR=yes 

# Create a non-root user and set permissions
RUN addgroup -S appuser
RUN adduser -S appuser
WORKDIR /home/appuser
RUN chown appuser:appuser /home/appuser
USER appuser

# Copy the application files into our user's home dir
COPY --chown=appuser:appuser . ./

# Copy the requirements.txt file and install the requirements
COPY --chown=appuser:appuser requirements.txt .
RUN python -m pip install --no-cache-dir --upgrade pip && \
    python -m pip install --no-cache-dir --user -r requirements.txt

# Ensure proper handling of kernel signals - https://github.com/krallin/tini
ENTRYPOINT [ "tini", "--" ]

# Run it! Although, our entrypoint will be the 
CMD ["python3", "-m", "agent_swarm.py"]