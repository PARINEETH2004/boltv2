# Real-Time Weather Data Stream Analysis

A complete **Big Data Analytics Pipeline** for streaming real-time weather data using **Apache Kafka**, **Hadoop HDFS**, **Apache Spark**, and **Flask**.

## Features

- **Real-Time Data Ingestion:** Continuous weather data streaming from OpenWeatherMap API via Kafka
- **Distributed Storage:** Persistent, scalable storage on Hadoop HDFS with intelligent partitioning
- **Advanced Analytics:** Batch and streaming analytics using Apache Spark for trends and anomaly detection
- **Interactive Dashboard:** Real-time visualization of weather trends, statistics, and anomalies
- **Containerized Deployment:** Docker Compose orchestration for easy local setup and cloud deployment
- **Production-Ready:** Comprehensive documentation for setup, deployment, and scaling

## Architecture

```
OpenWeatherMap API
        ↓
   [Producer]
        ↓
  [Kafka Topic]
   /    |     \
  /     |      \
[Partition 0-2]
        ↓
   [Consumer]
        ↓
[HDFS Storage]
        ↓
 [Analytics Job]
    /  |  \
   /   |   \
[Statistics] [Trends] [Anomalies]
        ↓
  [Flask API]
        ↓
 [Web Dashboard]
```

## Tech Stack

| Component | Technology | Version |
| :-------- | :--------- | :------ |
| Message Queue | Apache Kafka | 7.5.0 |
| Distributed Storage | Apache Hadoop | 3.3.4 |
| Analytics Engine | Apache Spark | 3.5.0 |
| Data Source | OpenWeatherMap API | v2.5 |
| Web Framework | Flask | 3.0.0 |
| Coordination | Apache Zookeeper | 7.5.0 |
| Containerization | Docker & Docker Compose | Latest |

## Getting Started

### Quick Start (5 minutes)

1. **Get OpenWeatherMap API Key:**
   - Visit https://openweathermap.org/api
   - Sign up and copy your API key

2. **Clone and Setup:**
   ```bash
   cp .env.example .env
   # Edit .env and add OPENWEATHER_API_KEY
   ```

3. **Start Services:**
   ```bash
   docker-compose up -d
   ```

4. **Initialize HDFS:**
   ```bash
   docker-compose exec namenode bash << 'EOF'
   hdfs dfs -mkdir -p /weather_data/{raw,analytics,archive}
   hdfs dfs -chmod -R 755 /weather_data
   EOF
   ```

5. **Create Kafka Topic:**
   ```bash
   docker-compose exec kafka kafka-topics.sh \
     --bootstrap-server kafka:29092 \
     --create \
     --topic weather_data \
     --partitions 3 \
     --replication-factor 1
   ```

6. **View Dashboard:**
   - Open http://localhost:5000 in your browser
   - Wait 5+ minutes for data to populate
   - Run analytics job to see visualizations

For detailed setup instructions, see [QUICKSTART.md](QUICKSTART.md).

## Documentation

### Core Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Get running in 5 minutes
- **[SETUP.md](SETUP.md)** - Complete installation and configuration guide
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System design, data flow, and scaling
- **[API.md](API.md)** - API endpoint reference and examples
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Production deployment on AWS, GCP, K8s, Swarm

### Project Structure

```
.
├── docker-compose.yml              # Docker service orchestration
├── Dockerfile.producer             # Producer container
├── Dockerfile.consumer             # Consumer container
├── Dockerfile.flask                # Flask app container
├── .env.example                    # Environment variables template
├── src/
│   ├── producer.py                 # Kafka producer (API → Kafka)
│   ├── consumer.py                 # Kafka consumer (Kafka → HDFS)
│   ├── analytics.py                # PySpark analytics jobs
│   └── flask_app/
│       ├── app.py                  # Flask API server
│       └── templates/
│           └── dashboard.html      # Web dashboard UI
├── scripts/
│   ├── run_analytics.sh            # Analytics job launcher
│   ├── init_hdfs.sh                # HDFS initialization
│   └── create_kafka_topic.sh       # Kafka topic creation
├── requirements.*.txt              # Python dependencies
├── README.md                       # This file
├── QUICKSTART.md                   # 5-minute setup guide
├── SETUP.md                        # Complete setup guide
├── ARCHITECTURE.md                 # System architecture
├── API.md                          # API documentation
└── DEPLOYMENT.md                   # Production deployment
```

## Key Services

### Producer Service
Fetches live weather data from OpenWeatherMap API and publishes to Kafka.

```python
# Fetches every 60 seconds for 5 cities
python src/producer.py
```

### Consumer Service
Reads from Kafka and writes to HDFS in partitioned structure.

```python
# Runs continuously
python src/consumer.py
```

### Analytics Job
Computes statistics, trends, and detects anomalies using PySpark.

```bash
spark-submit --master spark://spark-master:7077 src/analytics.py
```

### Flask Dashboard
Interactive web interface for visualizations and data exploration.

```bash
python src/flask_app/app.py
# Opens at http://localhost:5000
```

## Services and Access Points

| Service | URL | Port | Purpose |
| :------ | :-- | :--- | :------ |
| **Flask Dashboard** | http://localhost:5000 | 5000 | Analytics visualization |
| **Hadoop NameNode** | http://localhost:9870 | 9870 | HDFS browser & monitoring |
| **Spark Master** | http://localhost:8080 | 8080 | Spark cluster UI |
| **Kafka Broker** | localhost:9092 | 9092 | Message broker (internal) |
| **Zookeeper** | localhost:2181 | 2181 | Coordination (internal) |

## Data Models

### Raw Weather Record
```json
{
  "timestamp": "2024-10-31T15:00:00.000000",
  "city": "New York",
  "latitude": 40.7128,
  "longitude": -74.0060,
  "temperature": 15.5,
  "feels_like": 14.8,
  "humidity": 64,
  "pressure": 1013,
  "wind_speed": 4.5,
  "wind_direction": 180,
  "cloudiness": 50,
  "rainfall": 0.0,
  "weather_main": "Cloudy",
  "weather_description": "overcast clouds"
}
```

### City Statistics
```json
{
  "city": "New York",
  "record_count": 120,
  "avg_temperature": 15.32,
  "min_temperature": 12.0,
  "max_temperature": 18.5,
  "stddev_temperature": 1.45,
  "avg_humidity": 65.2,
  "avg_wind_speed": 4.5,
  "total_rainfall": 0.0,
  "avg_pressure": 1013.2
}
```

## API Endpoints

### Core Endpoints
- `GET /` - Main dashboard
- `GET /api/city-statistics` - Aggregated stats by city
- `GET /api/hourly-trends` - Hourly trends data
- `GET /api/temperature-chart` - Temperature visualization
- `GET /api/humidity-chart` - Humidity visualization
- `GET /api/anomalies` - Detected anomalies
- `GET /api/raw-data` - Recent raw observations

See [API.md](API.md) for complete endpoint documentation.

## Data Flow

1. **Ingestion (60s cycle)**
   - Producer fetches from OpenWeatherMap API
   - Publishes 5 records to Kafka (one per city)

2. **Streaming (continuous)**
   - Consumer polls Kafka messages
   - Batches 100 records and writes to HDFS
   - Partitioned: `/weather_data/raw/year=2024/month=10/day=31/weather_HHMM.jsonl`

3. **Analytics (hourly)**
   - Spark job reads from HDFS
   - Computes statistics, trends, anomalies
   - Writes results to `/weather_data/analytics/`

4. **Visualization (on-demand)**
   - Flask reads analytics from HDFS
   - Renders interactive charts with Plotly
   - Dashboard auto-refreshes every 60 seconds

## Monitoring

### View Logs
```bash
docker-compose logs -f producer      # Producer logs
docker-compose logs -f consumer      # Consumer logs
docker-compose logs -f flask-app     # Flask app logs
```

### Check HDFS
```bash
docker-compose exec namenode hdfs dfs -ls -R /weather_data
```

### Check Kafka
```bash
docker-compose exec kafka kafka-console-consumer.sh \
  --bootstrap-server kafka:29092 \
  --topic weather_data \
  --max-messages 5
```

## Performance

### Expected Throughput
- **Producer:** 5-10 messages/minute
- **Consumer:** 1000+ messages/second
- **Analytics:** 5-30 seconds per job
- **Dashboard Load:** 1-2 seconds

### Storage Usage
- **Raw Data:** ~3.5 MB per day (5 cities)
- **Analytics Output:** ~50 KB per job run
- **Fully scalable** for larger cities and higher frequency

## Scaling

### Horizontal Scaling
- Add Kafka brokers and repartition topics
- Add Spark workers and increase executor count
- Deploy multiple consumer instances
- Scale Flask app with load balancer

### Vertical Scaling
- Increase Spark executor memory (2GB → 4GB, 8GB)
- Increase Kafka broker heap
- Increase HDFS DataNode heap

See [DEPLOYMENT.md](DEPLOYMENT.md) for cloud deployment options.

## Troubleshooting

### No Data on Dashboard
- Wait 5+ minutes for data collection
- Run analytics job: See SETUP.md Step 4
- Check logs: `docker-compose logs [service]`

### Producer Not Starting
- Verify API key in `.env`: `grep OPENWEATHER_API_KEY .env`
- Check network: `docker-compose exec producer ping 8.8.8.8`
- View logs: `docker-compose logs producer`

### HDFS Connection Issues
- Initialize HDFS: See SETUP.md Step 4
- Check NameNode: `docker-compose exec namenode hdfs dfs -ls /`
- View logs: `docker-compose logs namenode`

See [SETUP.md](SETUP.md) for comprehensive troubleshooting.

## Production Deployment

The project is ready for production deployment on:
- **AWS EMR** - Managed Hadoop/Spark cluster
- **Google Cloud Dataproc** - Managed Spark cluster
- **Kubernetes** - Container orchestration
- **Docker Swarm** - Docker native clustering

See [DEPLOYMENT.md](DEPLOYMENT.md) for production setup.

## Future Enhancements

- Machine learning for weather forecasting
- Real-time alerting via email/SMS
- Geo-mapping with Mapbox
- Time-series database integration (InfluxDB)
- Multi-region deployment
- Advanced anomaly detection with ML
- Streaming analytics with Spark Streaming
- Data quality monitoring
- Cost optimization with data tiering

## System Requirements

### Local Development
- CPU: 4+ cores recommended
- RAM: 8GB minimum (16GB recommended)
- Disk: 20GB free space
- Docker: 20.10+
- Docker Compose: 1.29+

### Production
- Memory: 32GB+ for Spark/Hadoop
- Storage: 100GB+ for historical data
- Network: Low-latency connection for distributed processing
- HA Setup: Multiple nodes for fault tolerance

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - See LICENSE file for details

## Support

For issues or questions:
1. Check the [troubleshooting section](SETUP.md#troubleshooting)
2. Review the [architecture guide](ARCHITECTURE.md)
3. Check service logs: `docker-compose logs [service]`

## References

- [OpenWeatherMap API](https://openweathermap.org/api)
- [Apache Kafka Documentation](https://kafka.apache.org/documentation/)
- [Apache Hadoop Documentation](https://hadoop.apache.org/docs/)
- [Apache Spark Documentation](https://spark.apache.org/docs/latest/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Plotly Documentation](https://plotly.com/python/)

---

**Version:** 1.0.0
**Last Updated:** 2024
**Maintainer:** Weather Analytics Team
