#!/bin/bash

set -e

SPARK_MASTER=${SPARK_MASTER:-spark://spark-master:7077}
HADOOP_NAME_NODE=${HADOOP_NAME_NODE:-namenode:8020}

echo "Starting Weather Analytics Job..."
echo "Spark Master: $SPARK_MASTER"
echo "Hadoop NameNode: $HADOOP_NAME_NODE"

spark-submit \
  --master $SPARK_MASTER \
  --deploy-mode client \
  --executor-memory 2g \
  --executor-cores 2 \
  --conf spark.hadoop.fs.defaultFS=hdfs://$HADOOP_NAME_NODE \
  src/analytics.py

echo "Analytics job completed"
