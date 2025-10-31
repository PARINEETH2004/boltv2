# Real-Time Weather Data Stream Analysis - Setup Guide

## Prerequisites

Before you begin, ensure you have the following installed on your system:

- **Docker** (version 20.10+)
- **Docker Compose** (version 1.29+)
- **Git**
- **OpenWeatherMap API Key** (free at https://openweathermap.org/api)

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                   REAL-TIME DATA PIPELINE                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  [OpenWeatherMap API]                                          │
│           ↓                                                     │
│  [Kafka Producer] → [Kafka Broker] → [Kafka Consumer]         │
│                            ↑                ↓                  │
│                      [Zookeeper]      [HDFS Storage]          │
│                                            ↓                  │
│                              [PySpark Analytics Job]          │
│                                     ↓      ↓      ↓          │
│                              [Analytics Output]                │
│                                     ↓                          │
│                         [Flask Dashboard - :5000]              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Installation Steps

### Step 1: Clone or Set Up Project

```bash
cd /path/to/weather-analytics-project
```

### Step 2: Configure Environment Variables

Copy the example environment file and update it with your OpenWeatherMap API key:

```bash
cp .env.example .env
```

Edit `.env` and add your API key:

```
OPENWEATHER_API_KEY=your_actual_api_key_here
KAFKA_BOOTSTRAP_SERVERS=kafka:29092
HADOOP_NAME_NODE=namenode:8020
SPARK_MASTER=spark://spark-master:7077
FLASK_ENV=production
```

**How to get an OpenWeatherMap API Key:**
1. Visit https://openweathermap.org/api
2. Sign up for a free account
3. Navigate to "API keys" section
4. Copy your API key

### Step 3: Start All Services

```bash
docker-compose up -d
```

This starts:
- Zookeeper
- Kafka Broker
- Hadoop NameNode and DataNode
- Spark Master and Worker
- Python Producer Service
- Python Consumer Service
- Flask Dashboard

Monitor the services:

```bash
docker-compose logs -f
```

### Step 4: Initialize HDFS (One-time setup)

Once containers are running, initialize HDFS directories:

```bash
docker-compose exec namenode bash /bin/bash << 'EOF'
hdfs dfs -mkdir -p /weather_data/raw
hdfs dfs -mkdir -p /weather_data/analytics
hdfs dfs -mkdir -p /weather_data/archive
hdfs dfs -chmod -R 755 /weather_data
echo "HDFS initialization completed"
EOF
```

### Step 5: Create Kafka Topic

```bash
docker-compose exec kafka kafka-topics.sh \
  --bootstrap-server kafka:29092 \
  --create \
  --topic weather_data \
  --partitions 3 \
  --replication-factor 1 \
  --if-not-exists
```

## Accessing Services

Once running, access the following:

| Service           | URL/Port                              | Purpose                          |
| :---------------- | :------------------------------------ | :------------------------------- |
| Flask Dashboard   | http://localhost:5000                 | Analytics visualization          |
| Hadoop NameNode   | http://localhost:9870                 | HDFS file browser & monitoring   |
| Spark Master      | http://localhost:8080                 | Spark cluster UI                 |
| Kafka Broker      | kafka:29092 (internal)                | Message streaming               |
| Zookeeper         | zookeeper:2181 (internal)             | Coordination service             |

## Running Analytics Jobs

### Option 1: Manual Analytics Execution

Run the PySpark analytics job manually:

```bash
docker-compose exec spark-master spark-submit \
  --master spark://spark-master:7077 \
  --deploy-mode client \
  --executor-memory 2g \
  --executor-cores 2 \
  --conf spark.hadoop.fs.defaultFS=hdfs://namenode:8020 \
  /path/to/src/analytics.py
```

### Option 2: Scheduled Analytics (Cron)

Schedule the analytics job to run periodically (e.g., every hour):

```bash
docker-compose exec spark-master crontab -e
```

Add:
```
0 * * * * spark-submit --master spark://spark-master:7077 --deploy-mode client /path/to/src/analytics.py
```

## Project Structure

```
.
├── docker-compose.yml           # Docker service definitions
├── Dockerfile.producer          # Producer container config
├── Dockerfile.consumer          # Consumer container config
├── Dockerfile.flask             # Flask app container config
├── .env.example                 # Environment variables template
├── src/
│   ├── producer.py              # Kafka producer (fetches API data)
│   ├── consumer.py              # Kafka consumer (writes to HDFS)
│   ├── analytics.py             # PySpark analytics job
│   └── flask_app/
│       ├── app.py               # Flask application
│       └── templates/
│           └── dashboard.html   # Web dashboard
├── scripts/
│   ├── run_analytics.sh         # Analytics job launcher
│   ├── init_hdfs.sh             # HDFS initialization
│   └── create_kafka_topic.sh    # Kafka topic creation
├── requirements.producer.txt    # Producer dependencies
├── requirements.consumer.txt    # Consumer dependencies
├── requirements.flask.txt       # Flask dependencies
└── requirements.analytics.txt   # Analytics dependencies
```

## Data Flow

1. **Producer (producer.py)**
   - Fetches live weather data from OpenWeatherMap API
   - Publishes JSON records to Kafka topic `weather_data`
   - Runs continuously every 60 seconds

2. **Consumer (consumer.py)**
   - Consumes messages from Kafka topic
   - Batches records (100 at a time)
   - Writes to HDFS in partitioned structure: `/weather_data/raw/year=2024/month=10/day=31/weather_HHMM.jsonl`

3. **Analytics (analytics.py)**
   - Reads raw data from HDFS
   - Computes city-level statistics (avg, min, max, stddev)
   - Computes hourly trends
   - Detects temperature anomalies
   - Saves results to `/weather_data/analytics/`

4. **Dashboard (Flask)**
   - Reads analytics results from HDFS
   - Displays real-time visualizations
   - Shows city statistics, trends, and anomalies
   - Accessible at http://localhost:5000

## Monitoring

### Check Service Logs

Producer logs:
```bash
docker-compose logs producer
```

Consumer logs:
```bash
docker-compose logs consumer
```

Flask app logs:
```bash
docker-compose logs flask-app
```

### Monitor Kafka Topics

List topics:
```bash
docker-compose exec kafka kafka-topics.sh \
  --bootstrap-server kafka:29092 \
  --list
```

Check message count:
```bash
docker-compose exec kafka kafka-run-class.sh \
  kafka.tools.JmxTool \
  --object-name kafka.server:type=BrokerTopicMetrics,name=MessagesInPerSec
```

### Monitor HDFS

Access HDFS web UI at http://localhost:9870

Or use command line:
```bash
docker-compose exec namenode hdfs dfs -ls -R /weather_data
```

## Troubleshooting

### Producer Not Connecting to Kafka

**Error:** `kafka.errors.NoBrokersAvailable`

**Solution:**
1. Ensure Kafka container is running: `docker-compose ps kafka`
2. Check Kafka logs: `docker-compose logs kafka`
3. Verify network connectivity: `docker-compose exec producer ping kafka`
4. Ensure `KAFKA_BOOTSTRAP_SERVERS=kafka:29092` in `.env`

### Consumer Not Writing to HDFS

**Error:** `Connection refused` to HDFS

**Solution:**
1. Check if NameNode is running: `docker-compose ps namenode`
2. Verify HDFS is initialized (see Step 4 above)
3. Check NameNode logs: `docker-compose logs namenode`
4. Ensure directories exist: `docker-compose exec namenode hdfs dfs -ls /weather_data`

### Analytics Job Failing

**Error:** `Cannot connect to Spark Master`

**Solution:**
1. Verify Spark Master is running: `docker-compose ps spark-master`
2. Check Spark UI at http://localhost:8080
3. Ensure Spark Master address is correct: `spark://spark-master:7077`
4. Check Spark logs: `docker-compose logs spark-master`

### Flask Dashboard Not Loading Data

**Error:** `No analytics data available`

**Solution:**
1. Run analytics job manually (see "Running Analytics Jobs" section)
2. Check Flask logs: `docker-compose logs flask-app`
3. Verify HDFS data exists: `docker-compose exec namenode hdfs dfs -ls -R /weather_data/analytics`
4. Ensure Flask can access HDFS: `docker-compose exec flask-app python -c "from hdfs import InsecureClient; print('HDFS OK')"`

## Stopping Services

```bash
docker-compose down
```

To remove all data and start fresh:

```bash
docker-compose down -v
```

## Next Steps

1. **Extend the Project:**
   - Add new cities in `producer.py`
   - Implement additional analytics (forecasting, seasonal patterns)
   - Add email/SMS alerts for anomalies

2. **Deploy to Cloud:**
   - Use AWS EMR or GCP Dataproc for scalability
   - Replace local HDFS with S3 or GCS
   - Use managed Kafka services

3. **Optimize Performance:**
   - Increase Spark executor resources
   - Add more Kafka partitions
   - Implement data archival strategy

## Additional Resources

- **OpenWeatherMap API:** https://openweathermap.org/api
- **Apache Kafka:** https://kafka.apache.org/documentation/
- **Apache Hadoop:** https://hadoop.apache.org/docs/
- **Apache Spark:** https://spark.apache.org/docs/latest/
- **Flask:** https://flask.palletsprojects.com/

## Support

For issues or questions:
1. Check the logs using `docker-compose logs [service-name]`
2. Review the troubleshooting section above
3. Verify environment variables in `.env`
4. Ensure all prerequisites are installed

---

**Last Updated:** 2024
**Version:** 1.0
