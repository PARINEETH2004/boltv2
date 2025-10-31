# System Architecture

## Overview

This is a complete **Big Data Analytics Pipeline** that ingests real-time weather data, stores it distributedly, processes it at scale, and visualizes insights through an interactive dashboard.

## Components

### 1. Data Source: OpenWeatherMap API

- Provides real-time weather data for multiple cities
- Data includes: temperature, humidity, pressure, wind speed, rainfall, etc.
- Free tier allows 1000 API calls per day

**Endpoint:** `https://api.openweathermap.org/data/2.5/weather`

**Sample Response:**
```json
{
  "coord": {"lon": 10.99, "lat": 44.34},
  "weather": [{"id": 500, "main": "Rain", "description": "light rain"}],
  "main": {
    "temp": 9.07,
    "humidity": 87,
    "pressure": 1015
  },
  "wind": {"speed": 4.1}
}
```

### 2. Apache Kafka (Message Queue)

**Role:** Real-time data ingestion and distribution

**Configuration:**
- Single broker deployment (can be scaled to multi-broker)
- Topic: `weather_data` with 3 partitions
- Replication factor: 1 (for single broker)
- Message format: JSON

**Topics:**
```
weather_data
├── Partition 0
├── Partition 1
└── Partition 2
```

**Producer Behavior:**
- Fetches data every 60 seconds
- Sends 5 weather records per cycle (one per city)
- Uses synchronous sends with acknowledgment

**Consumer Behavior:**
- Reads messages in batches of 100
- Maintains consumer group for offset management
- Auto-commits offsets every 30 seconds

### 3. Zookeeper (Coordination)

- Manages Kafka cluster coordination
- Maintains broker metadata
- Handles leader election for partitions
- Not directly accessed by applications

### 4. Apache Hadoop (Distributed Storage)

**Role:** Persistent storage for raw and processed data

**Architecture:**
```
NameNode (Master)
  ├── Manages file system namespace
  ├── Maintains file system tree
  └── Tracks all files

DataNode (Slave)
  ├── Stores actual data blocks
  └── Sends block reports to NameNode
```

**Directory Structure:**
```
/weather_data/
├── raw/
│   └── year=2024/month=10/day=31/
│       └── weather_1400.jsonl (hourly files)
└── analytics/
    ├── city_statistics/
    ├── hourly_trends/
    └── anomalies/
```

**Storage Format:**
- Raw data: JSONL (JSON Lines - one record per line)
- Analytics output: JSON
- Partitioning: By year, month, day (enables efficient queries)

### 5. Apache Spark (Distributed Processing)

**Role:** Large-scale data analytics and transformations

**Cluster Setup:**
```
Spark Master (7077)
├── Spark Worker 1 (8081)
│   └── Executors
└── Spark Worker 2 (optional)
    └── Executors
```

**Jobs:**

#### City Statistics Job
```python
df.groupBy("city").agg(
    count("*"),
    avg("temperature"),
    min("temperature"),
    max("temperature"),
    stddev("temperature"),
    avg("humidity")
)
```

#### Hourly Trends Job
```python
df.groupBy("city", "hour").agg(
    avg("temperature"),
    avg("humidity"),
    avg("wind_speed")
)
```

#### Anomaly Detection Job
```python
anomalies = df.where(
    abs(df.temperature - mean_temp) > 3 * stddev_temp
)
```

**Processing Strategy:**
- Batch processing (not real-time streaming with Spark)
- Runs on historical data (yesterday to current)
- Output is materialized to HDFS

### 6. Flask Web Application (Dashboard)

**Role:** Real-time visualization and analytics

**API Endpoints:**
- `GET /` - Main dashboard
- `GET /api/city-statistics` - City-level stats
- `GET /api/hourly-trends` - Hourly trends
- `GET /api/temperature-chart` - Temperature visualization
- `GET /api/humidity-chart` - Humidity visualization
- `GET /api/anomalies` - Detected anomalies
- `GET /api/raw-data` - Recent raw data

**Technology Stack:**
- Backend: Flask (Python)
- Frontend: HTML + JavaScript + Plotly
- Data Source: HDFS (via Python HDFS client)

## Data Flow

### Cycle 1: Data Ingestion (Continuous)

```
Time: 00:00
├── Producer fetches API
│   ├── New York: 15°C
│   ├── London: 12°C
│   ├── Tokyo: 20°C
│   ├── Sydney: 25°C
│   └── Dubai: 35°C
│
├── Sends to Kafka (weather_data topic)
│   ├── Message 1: {city: "New York", temp: 15, ...}
│   ├── Message 2: {city: "London", temp: 12, ...}
│   └── ... (continues with other cities)
│
└── Kafka partitions messages
    ├── Partition 0: NYC, Sydney
    ├── Partition 1: London
    └── Partition 2: Tokyo, Dubai
```

### Cycle 2: Data Persistence (Continuous)

```
Time: 00:00-00:05
├── Consumer polls Kafka messages
│   └── Receives up to 100 messages per poll
│
├── Batches messages
│   └── Accumulates 100 records
│
├── Writes batch to HDFS
│   └── /weather_data/raw/year=2024/month=10/day=31/weather_0000.jsonl
│
└── Commits offset to Kafka
    └── Next poll starts from new offset
```

### Cycle 3: Data Analytics (Hourly)

```
Time: 01:00
├── Analytics job triggered
│   └── spark-submit analytics.py
│
├── Reads raw data from HDFS
│   └── /weather_data/raw/**/*.jsonl
│
├── Computes statistics
│   ├── City statistics (avg, min, max, stddev)
│   ├── Hourly trends (hourly aggregations)
│   └── Anomaly detection (statistical outliers)
│
└── Writes results to HDFS
    ├── /weather_data/analytics/city_statistics/
    ├── /weather_data/analytics/hourly_trends/
    └── /weather_data/analytics/anomalies/
```

### Cycle 4: Dashboard Visualization (On-demand)

```
User accesses http://localhost:5000
│
├── Flask app loads
│   └── Initialize HDFS client
│
├── Dashboard makes API requests
│   ├── GET /api/city-statistics → HDFS query
│   ├── GET /api/temperature-chart → HDFS query
│   ├── GET /api/anomalies → HDFS query
│   └── GET /api/raw-data → HDFS query
│
├── Flask processes results
│   ├── Aggregates data
│   ├── Generates Plotly charts
│   └── Formats JSON responses
│
└── Browser renders visualization
    ├── Tables
    ├── Line charts
    ├── Bar charts
    └── Real-time updates every 60 seconds
```

## Scaling Considerations

### Horizontal Scaling

**Kafka:**
- Add more brokers to the cluster
- Increase partition count for `weather_data` topic
- Rebalance partitions across brokers

**Hadoop:**
- Add more DataNodes
- Increase replication factor
- Set up namenode HA with Secondary Namenode

**Spark:**
- Add more worker nodes
- Increase executor memory and cores
- Use dynamic allocation

### Vertical Scaling

**Memory:**
- Spark executors: 2g → 4g, 8g, 16g
- Kafka brokers: Increase heap size
- HDFS: Increase datanode heap

**Storage:**
- Implement HDFS tiering
- Archive old data to cheaper storage
- Use compression (Snappy, LZ4)

### Rate Limiting

**API Calls:**
- Currently: 5 cities × 1 call/minute = 300 calls/hour
- Free tier: 1000 calls/day = ~42 calls/hour (need to reduce frequency)
- Solution: Increase interval from 60s to 300s

**Data Volume:**
- Per day: 5 cities × 24 hours × 60 min = 7,200 records
- Per record: ~500 bytes
- Per day: ~3.5 MB raw data
- Fully scalable for larger cities and higher frequency

## Security Considerations

### Current Implementation

- **No authentication** on internal services (Kafka, HDFS)
- **Docker network isolation** - services not exposed to host network
- **Flask** runs without HTTPS

### Production Hardening

1. **Kafka:**
   - Enable SASL/SSL authentication
   - Implement ACLs for topics

2. **HDFS:**
   - Enable Kerberos authentication
   - Set up RLS (Row-Level Security)
   - Use HTTPS for NameNode UI

3. **Flask:**
   - Add authentication (JWT or OAuth2)
   - Enable HTTPS with SSL certificates
   - Implement rate limiting

4. **Network:**
   - Place services behind VPN/firewall
   - Use network policies in Kubernetes
   - Enable TLS for inter-service communication

## Performance Metrics

### Expected Performance

**Producer:**
- Throughput: ~5-10 messages/minute
- Latency: ~100-500ms per message
- API fetch time: ~500ms per call

**Kafka:**
- Message retention: 7 days (configurable)
- Throughput capacity: 100+ MB/sec (per broker)
- Latency: <100ms end-to-end

**Consumer:**
- Throughput: 1000+ messages/second
- Batching: 100 messages per write
- HDFS write latency: ~100-200ms per batch

**Analytics:**
- Processing time: 5-30 seconds (depends on data volume)
- Computation: GroupBy aggregations on full dataset
- Output latency: ~1-2 seconds to HDFS

**Dashboard:**
- Page load: ~1-2 seconds (initial)
- API response: 200-500ms per endpoint
- Chart rendering: 500-1000ms (depends on data)
- Auto-refresh: Every 60 seconds

### Monitoring Metrics

1. **Kafka Metrics:**
   - Messages in rate (msgs/sec)
   - Consumer lag (offset behind producer)
   - Broker disk usage

2. **HDFS Metrics:**
   - NameNode heap usage
   - DataNode block count
   - Block replication status

3. **Spark Metrics:**
   - Task execution time
   - Shuffle spill (disk writes)
   - GC time

4. **Flask Metrics:**
   - Request latency
   - HDFS connection time
   - Error rates

## Failure Scenarios

### Kafka Broker Down
- Producer queues messages locally (retries)
- Consumer continues from last offset
- **Recovery:** Restart broker, rebalance partitions

### HDFS NameNode Down
- Consumer cannot write data
- Analytics jobs fail to read
- **Recovery:** Use Secondary NameNode for failover

### Spark Job Failure
- Analytics results not updated
- Dashboard shows stale data
- **Recovery:** Automatic retry or manual re-trigger

### API Unavailable
- Producer returns None for that city
- That city's data missing for that cycle
- **Recovery:** Wait for API to recover, continue polling

### Consumer Lag
- Data accumulates in Kafka
- Risk of data loss if retention expires
- **Recovery:** Increase consumer processing or parallelism

## Optimization Opportunities

1. **Streaming Analytics:** Replace batch Spark with Spark Streaming for real-time results
2. **Caching:** Cache analytics results in Redis for faster dashboard loads
3. **Compression:** Enable SNAPPY compression on Kafka and HDFS
4. **Partitioning:** Implement time-based HDFS partitioning for faster queries
5. **Indexing:** Use HBase or Elasticsearch for fast anomaly lookups
6. **ML:** Add predictive models for weather forecasting
7. **Alerts:** Implement real-time alerting via email/SMS/webhooks

---

**Last Updated:** 2024
**Version:** 1.0
