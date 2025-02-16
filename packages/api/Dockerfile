# Use a node image as base
FROM node:20-alpine AS base

# Add build arguments
ARG SENTRY_DISABLED=false
ENV SENTRY_DISABLED=$SENTRY_DISABLED

WORKDIR /app

# Copy the root package.json, package-lock.json
COPY ../../package.json ../../package-lock.json ./
# Copy only the api package to the container
COPY ../../packages/api ./packages/api
COPY ../../packages/common-ts ./packages/common-ts
# Copy the root tsconfig.json
COPY ../../tsconfig.json ./

# Install dependencies and bootstrap with npm workspaces
RUN npm install

# Build the common-ts package first
RUN npm run build --workspace common-ts

# Build the api package - conditionally use Sentry
RUN if [ "$SENTRY_DISABLED" = "true" ] ; then \
        npm run build:api ; \
    else \
        --mount=type=secret,id=SENTRY_AUTH_TOKEN \
        export SENTRY_AUTH_TOKEN=$(cat /run/secrets/SENTRY_AUTH_TOKEN) && \
        npm run build:api ; \
    fi

# Set the working directory to the api package
WORKDIR /app/packages/api

# Expose the port
EXPOSE 4000

# Start the application
CMD ["npm", "start"]