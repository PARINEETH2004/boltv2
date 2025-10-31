#!/bin/bash

set -e

KAFKA_BROKER=${KAFKA_BROKER:-kafka:9092}
TOPIC_NAME=weather_data
PARTITIONS=3
REPLICATION_FACTOR=1

echo "Creating Kafka topic: $TOPIC_NAME"

kafka-topics.sh \
  --bootstrap-server $KAFKA_BROKER \
  --create \
  --topic $TOPIC_NAME \
  --partitions $PARTITIONS \
  --replication-factor $REPLICATION_FACTOR \
  --if-not-exists

echo "Kafka topic created successfully"
