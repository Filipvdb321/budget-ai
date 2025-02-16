# Use a node image as base
FROM node:20-alpine AS base
 
# Add build arguments
ARG NEXT_PUBLIC_SENTRY_ENABLED=false
ENV NEXT_PUBLIC_SENTRY_ENABLED=$NEXT_PUBLIC_SENTRY_ENABLED

WORKDIR /app

# Copy the root package.json, package-lock.json
COPY ../../package.json ../../package-lock.json ./

# Copy only the web package to the container
COPY ../../packages/web ./packages/web
COPY ../../packages/common-ts ./packages/common-ts

# Copy the root tsconfig.json
COPY ../../tsconfig.json ./

# Install dependencies and bootstrap with npm workspaces
RUN npm install

# Build the common-ts package first
RUN npm run build --workspace common-ts

# Build the web package
RUN NEXT_PUBLIC_SENTRY_ENABLED=false npm run build --workspace web

# Set the working directory to the web package
WORKDIR /app/packages/web

# Expose the port
EXPOSE 3000

# Start the application
CMD ["npm", "start"]