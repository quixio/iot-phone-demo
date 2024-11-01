#!/bin/bash

# Define variables
PORTAL_URL="${Quix__Portal__Api}/workspaces/${Quix__Workspace__Id}/broker/librdkafka"
AUTH_TOKEN="${Quix__Sdk__Token}"
CERT_PATH="/etc/ssl/certs/ca.pem"

# Download the broker configuration as JSON
echo "Fetching broker configuration..."
response=$(curl -s -X 'GET' "$PORTAL_URL" \
  -H 'accept: text/plain' \
  -H 'X-Version: 2.0' \
  -H "Authorization: bearer $AUTH_TOKEN")

echo "$response"

# Check if the response is valid JSON
if ! echo "$response" | jq . > /dev/null 2>&1; then
  echo "Failed to fetch broker configuration or response is not JSON"
  exit 1
fi

# Extract values from JSON response and export them as environment variables
export KAFKA_BOOTSTRAP_SERVERS=$(echo "$response" | jq -r '.["bootstrap.servers"]')
export KAFKA_SECURITY_PROTOCOL=$(echo "$response" | jq -r '.["security.protocol"]')
export KAFKA_SASL_MECHANISM=$(echo "$response" | jq -r '.["sasl.mechanism"]')
export KAFKA_SASL_USERNAME=$(echo "$response" | jq -r '.["sasl.username"]')
export KAFKA_SASL_PASSWORD=$(echo "$response" | jq -r '.["sasl.password"]')

# Extract and decode the certificate, then save it to the specified path
echo "Extracting certificate..."
echo "$response" | jq -r '.["ssl.ca.cert"]' | base64 -d > "$CERT_PATH"

# Ensure the certificate is readable by Telegraf
chmod 644 "$CERT_PATH"

# Verify that the certificate file was created
if [ -f "$CERT_PATH" ]; then
  echo "Certificate saved to $CERT_PATH"
else
  echo "Failed to save certificate"
  exit 1
fi

# Start Telegraf
exec telegraf --config /etc/telegraf/telegraf.conf