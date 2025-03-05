# Set the build target (either "dev" or "prod") with a default of "dev"
ARG TARGET=dev

# Start with a slim Python 3.13.0 base image, creating a shared base stage
FROM python:3.13.0-slim AS common-stage

RUN cp -v /etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem /usr/local/share/ca-certificates/custom-cert.crt
RUN update-ca-certificates

# Update package lists, upgrade installed packages and install required system packages
RUN apt-get update \
    && apt-get -y upgrade \
    && apt-get -y install curl git libpango-1.0-0 libpangoft2-1.0-0 \
    && pip install --upgrade pip pipenv wheel \
    && apt-get clean && rm -rf /var/lib/apt/lists && rm -rf ~/.cache

# Set the working directory to /app for the project files
WORKDIR /app

# Copy all files from the build context (current directory) into the container's /app directory
COPY ./ ./

# Begin the production stage
FROM common-stage AS prod-stage
# Remove test directories, install only production dependencies with Pipenv and byte-code compile application
RUN echo "Building prod-stage" 1>&2 \
    && rm -r clinical_mdr_api/tests consumer_api/tests \
    && pipenv sync --system \
    && pipenv --clear \
    && python -m compileall -f -j 0 .

# Begin the development stage
FROM common-stage AS dev-stage
# Install all dependencies with Pipenv
RUN echo "Building dev-stage" 1>&2 && pipenv sync --dev --system && pipenv --clear

# Select either the production or development stage to build the final image based on TARGET
FROM ${TARGET}-stage AS final-stage

# Set environment variables for the Uvicorn server configuration and health check path
ENV UVICORN_APP="clinical_mdr_api.main:app" \
    UVICORN_HOST="0.0.0.0" \
    UVICORN_PORT="8000" \
    UVICORN_ROOT_PATH="/" \
    HEALTHCHECK_PATH="system/healthcheck"

# Build metadata for version tracking
ARG BUILD_NUMBER
ARG BUILD_BRANCH
ARG BUILD_COMMIT
ENV BUILD_NUMBER="$BUILD_NUMBER" \
    BUILD_BRANCH="$BUILD_BRANCH" \
    BUILD_COMMIT="$BUILD_COMMIT"

# Expose port 8000 for the Uvicorn application
EXPOSE $UVICORN_PORT

RUN chgrp -R 0 /app && \
    chmod -R g=u /app

# Define a health check to verify that the application is responding at the health check endpoint
HEALTHCHECK --start-period=60s --timeout=3s --interval=10s --retries=2 CMD \
    curl --fail --silent --show-error --max-time 2 \
    "http://localhost:$UVICORN_PORT/$HEALTHCHECK_PATH" > /dev/null || exit 1

# Run the application using Uvicorn
CMD ["pipenv", "run", "uvicorn"]
