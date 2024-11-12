# Use Golang image for building Telegraf
FROM --platform=linux/amd64 golang:1.23-alpine AS builder

# Install required packages
RUN apk add --no-cache git make

# Clone Telegraf source code
WORKDIR /go/src/github.com/influxdata
RUN git clone https://github.com/influxdata/telegraf.git

# Copy the custom plugin code into the Telegraf outputs directory
COPY plugins/outputs /go/src/github.com/influxdata/telegraf/plugins/outputs/

# Build Telegraf with the custom plugin
WORKDIR /go/src/github.com/influxdata/telegraf
RUN go mod download && go build -o telegraf ./cmd/telegraf

# Use the official Telegraf image for the final container
FROM telegraf:latest

# Copy the built Telegraf binary from the builder stage
COPY --from=builder /go/src/github.com/influxdata/telegraf/telegraf /usr/bin/telegraf

# Ensure the binary has executable permissions
RUN chmod +x /usr/bin/telegraf

# Copy custom Telegraf configuration
COPY telegraf.conf /etc/telegraf/telegraf.conf

# Default command to run Telegraf
CMD ["/usr/bin/telegraf", "--config", "/etc/telegraf/telegraf.conf"]