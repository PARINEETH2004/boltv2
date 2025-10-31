#!/bin/bash

set -e

HADOOP_NAME_NODE=${HADOOP_NAME_NODE:-namenode:8020}

echo "Initializing HDFS directories..."

hdfs dfs -mkdir -p /weather_data/raw
hdfs dfs -mkdir -p /weather_data/analytics
hdfs dfs -mkdir -p /weather_data/archive

echo "Setting HDFS permissions..."
hdfs dfs -chmod -R 755 /weather_data

echo "HDFS initialization completed"
