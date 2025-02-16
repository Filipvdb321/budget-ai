/** @type {import('next').NextConfig} */
const nextConfig = {}

// Enable Sentry unless explicitly disabled
const isSentryEnabled = !process.env.SENTRY_DISABLED;

// Default config without Sentry
let config = nextConfig;

// Add Sentry if enabled
if (isSentryEnabled) {
  const { withSentryConfig } = require("@sentry/nextjs");
  config = withSentryConfig(
    nextConfig,
    {
      org: "vanden-it",
      project: "javascript-nextjs",
      silent: !process.env.CI,
      widenClientFileUpload: true,
      reactComponentAnnotation: {
        enabled: true,
      },
      tunnelRoute: "/monitoring",
      hideSourceMaps: true,
      disableLogger: true,
      automaticVercelMonitors: true,
    }
  );
}

module.exports = config;
