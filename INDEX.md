# Project Index & Navigation Guide

Welcome! This index helps you navigate the complete Real-Time Weather Data Stream Analysis project.

## Quick Navigation

### I Want To...

#### Get Started Quickly
→ Start here: **[QUICKSTART.md](QUICKSTART.md)** (5 minutes)
- Simple step-by-step setup
- Minimal configuration
- Immediate verification

#### Understand the System
→ Read: **[README.md](README.md)** (Overview)
→ Then: **[ARCHITECTURE.md](ARCHITECTURE.md)** (Deep dive)
- System components
- Data flow
- Technical design

#### Set Up Properly
→ Follow: **[SETUP.md](SETUP.md)** (Complete guide)
- Detailed prerequisites
- Installation instructions
- Troubleshooting

#### Deploy to Production
→ Use: **[DEPLOYMENT.md](DEPLOYMENT.md)**
- AWS EMR setup
- Google Cloud Dataproc
- Kubernetes deployment
- Docker Swarm

#### Use the APIs
→ Reference: **[API.md](API.md)**
- Endpoint documentation
- Request/response examples
- Error handling

#### Understand What's Included
→ Check: **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)**
- Deliverables list
- Component overview
- Statistics

---

## Document Map

### Core Documentation

```
README.md
├── Project overview
├── Quick reference
├── Feature highlights
└── Getting started guide

QUICKSTART.md
├── 5-minute setup
├── Prerequisites check
├── Initialization steps
└── Verification

SETUP.md
├── Complete installation
├── Service configuration
├── Detailed troubleshooting
└── Monitoring guide

ARCHITECTURE.md
├── System design
├── Component overview
├── Data flow details
├── Performance metrics
└── Scaling strategies

API.md
├── Endpoint reference
├── Request/response formats
├── Error handling
└── Usage examples

DEPLOYMENT.md
├── Local deployment
├── AWS EMR
├── Google Cloud Dataproc
├── Kubernetes
├── Docker Swarm
└── Production hardening

PROJECT_SUMMARY.md
├── Deliverables
├── Statistics
├── Architecture spec
├── Extensibility
└── Next steps
```

---

## Source Code Files

### Application Code

| File | Purpose | Language | Lines |
| :--- | :------ | :------- | ----: |
| `src/producer.py` | Weather API → Kafka | Python | 150 |
| `src/consumer.py` | Kafka → HDFS | Python | 180 |
| `src/analytics.py` | Data analytics with Spark | Python | 250 |
| `src/flask_app/app.py` | Web API server | Python | 300 |
| `src/flask_app/templates/dashboard.html` | Web dashboard UI | HTML/JS | 350 |

### Configuration Files

| File | Purpose |
| :--- | :------ |
| `docker-compose.yml` | Service orchestration |
| `Dockerfile.producer` | Producer container |
| `Dockerfile.consumer` | Consumer container |
| `Dockerfile.flask` | Flask app container |
| `.env.example` | Environment template |

### Utility Scripts

| File | Purpose |
| :--- | :------ |
| `scripts/run_analytics.sh` | Analytics launcher |
| `scripts/init_hdfs.sh` | HDFS initialization |
| `scripts/create_kafka_topic.sh` | Kafka topic setup |

### Dependencies

| File | For |
| :--- | :-- |
| `requirements.producer.txt` | Producer service |
| `requirements.consumer.txt` | Consumer service |
| `requirements.flask.txt` | Flask application |
| `requirements.analytics.txt` | Analytics job |

---

## Learning Path

### Beginner
1. Read **README.md** - Understand the project
2. Follow **QUICKSTART.md** - Get it running
3. Explore **SETUP.md** - Learn each component
4. Check services at:
   - Flask: http://localhost:5000
   - Hadoop: http://localhost:9870
   - Spark: http://localhost:8080

### Intermediate
1. Study **ARCHITECTURE.md** - Understand design
2. Review source code:
   - `src/producer.py`
   - `src/consumer.py`
   - `src/analytics.py`
3. Explore **API.md** - Test endpoints
4. Customize the system (see "Extending the Project" below)

### Advanced
1. Review **DEPLOYMENT.md** - Production setup
2. Explore cloud deployment options
3. Set up monitoring and alerting
4. Implement high availability
5. Scale for larger datasets

---

## Common Tasks

### View Real-Time Data

**Option 1: Web Dashboard**
```bash
# Visit http://localhost:5000
```

**Option 2: API Call**
```bash
curl http://localhost:5000/api/raw-data
```

**Option 3: Kafka Consumer**
```bash
docker-compose exec kafka kafka-console-consumer.sh \
  --bootstrap-server kafka:29092 \
  --topic weather_data \
  --max-messages 5
```

### Check System Status

```bash
# View running services
docker-compose ps

# Check HDFS storage
docker-compose exec namenode hdfs dfs -ls -R /weather_data

# View producer logs
docker-compose logs -f producer

# View consumer logs
docker-compose logs -f consumer
```

### Run Analytics

```bash
# Manual execution
docker-compose exec spark-master spark-submit \
  --master spark://spark-master:7077 \
  --deploy-mode client \
  src/analytics.py

# Scheduled execution (see SETUP.md)
crontab -e
# Add: 0 * * * * spark-submit src/analytics.py
```

### Stop Services

```bash
# Stop all services (keep data)
docker-compose down

# Stop all services (remove data)
docker-compose down -v
```

---

## Extending the Project

### Add More Cities

Edit `src/producer.py`:
```python
CITIES = [
    {'name': 'New York', 'lat': 40.7128, 'lon': -74.0060},
    {'name': 'London', 'lat': 51.5074, 'lon': -0.1278},
    {'name': 'Tokyo', 'lat': 35.6762, 'lon': 139.6503},
    {'name': 'Sydney', 'lat': -33.8688, 'lon': 151.2093},
    {'name': 'Dubai', 'lat': 25.2048, 'lon': 55.2708},
    # ADD YOUR CITIES HERE
    {'name': 'Paris', 'lat': 48.8566, 'lon': 2.3522},
]
```

### Change Data Collection Frequency

Edit `src/producer.py` (line ~58):
```python
time.sleep(60)  # Change 60 to desired seconds
```

### Add Custom Analytics

Edit `src/analytics.py`:
```python
def my_custom_analysis(spark, df):
    # Your custom analysis here
    pass

# In main():
result = my_custom_analysis(spark, df)
save_results(result, "/weather_data/analytics/custom")
```

### Add Email Alerts

Create `src/alerter.py`:
```python
import smtplib
from email.mime.text import MIMEText

def send_alert(anomaly):
    msg = MIMEText(f"Anomaly: {anomaly}")
    # Send email
```

---

## Troubleshooting Guide

### Services Not Starting

**Check logs:**
```bash
docker-compose logs [service-name]
```

**Verify prerequisites:**
```bash
docker --version
docker-compose --version
```

**See:** [SETUP.md - Troubleshooting](SETUP.md#troubleshooting)

### No Data on Dashboard

1. Wait 5+ minutes for data collection
2. Run analytics job (see "Run Analytics" above)
3. Check HDFS for data:
   ```bash
   docker-compose exec namenode hdfs dfs -ls /weather_data
   ```
4. **See:** [SETUP.md - Troubleshooting](SETUP.md#troubleshooting)

### Performance Issues

1. Check resource usage:
   ```bash
   docker stats
   ```

2. Increase memory:
   - Edit `docker-compose.yml`
   - Change `executor-memory`

3. **See:** [ARCHITECTURE.md - Performance](ARCHITECTURE.md#performance-metrics)

---

## API Quick Reference

### City Statistics
```bash
curl http://localhost:5000/api/city-statistics
```

### Anomalies
```bash
curl http://localhost:5000/api/anomalies
```

### Raw Data
```bash
curl http://localhost:5000/api/raw-data
```

### Charts
```bash
curl http://localhost:5000/api/temperature-chart
curl http://localhost:5000/api/humidity-chart
```

**See:** [API.md](API.md) for complete reference

---

## Service Endpoints

### Web UIs
- **Flask Dashboard:** http://localhost:5000
- **Hadoop NameNode:** http://localhost:9870
- **Spark Master:** http://localhost:8080

### Internal Services
- **Kafka Broker:** kafka:29092 (docker network)
- **Zookeeper:** zookeeper:2181 (docker network)
- **HDFS NameNode:** namenode:8020 (docker network)

---

## Environment Setup

### Required Variables
```bash
OPENWEATHER_API_KEY=your_api_key_here
KAFKA_BOOTSTRAP_SERVERS=kafka:29092
HADOOP_NAME_NODE=namenode:8020
SPARK_MASTER=spark://spark-master:7077
FLASK_ENV=production
```

### Get API Key
1. Visit https://openweathermap.org/api
2. Sign up for free account
3. Copy your API key
4. Add to `.env` file

**See:** [SETUP.md - Configuration](SETUP.md#step-2-configure-environment-variables)

---

## File Organization

```
Weather Analytics Project
│
├── Application Code (src/)
│   ├── producer.py           - API → Kafka
│   ├── consumer.py           - Kafka → HDFS
│   ├── analytics.py          - Data analytics
│   └── flask_app/
│       ├── app.py            - Web server
│       └── templates/
│           └── dashboard.html - UI
│
├── Docker Setup
│   ├── docker-compose.yml    - Orchestration
│   ├── Dockerfile.producer
│   ├── Dockerfile.consumer
│   └── Dockerfile.flask
│
├── Configuration
│   ├── .env.example          - Template
│   └── requirements.*.txt    - Dependencies
│
├── Utilities
│   └── scripts/
│       ├── run_analytics.sh
│       ├── init_hdfs.sh
│       └── create_kafka_topic.sh
│
└── Documentation
    ├── README.md             - Overview
    ├── QUICKSTART.md         - 5-min setup
    ├── SETUP.md              - Full setup
    ├── ARCHITECTURE.md       - System design
    ├── API.md                - Endpoint ref
    ├── DEPLOYMENT.md         - Production
    ├── PROJECT_SUMMARY.md    - Deliverables
    └── INDEX.md              - This file
```

---

## Recommended Reading Order

1. **START:** [README.md](README.md) - 5 min
2. **SETUP:** [QUICKSTART.md](QUICKSTART.md) - 5 min
3. **UNDERSTAND:** [ARCHITECTURE.md](ARCHITECTURE.md) - 15 min
4. **REFERENCE:** [API.md](API.md) - As needed
5. **DEPLOY:** [DEPLOYMENT.md](DEPLOYMENT.md) - As needed
6. **DETAILS:** [SETUP.md](SETUP.md) - As needed

---

## Key Concepts

### Message Queue (Kafka)
- Streams data from producer to consumer
- Fault-tolerant message delivery
- Partitioned for scalability

### Distributed Storage (HDFS)
- Stores raw and processed data
- Time-based partitioning
- Replicates for fault tolerance

### Analytics (Spark)
- Batch processing of historical data
- Distributed SQL aggregations
- Statistical computations

### Web Service (Flask)
- REST API for data access
- Real-time visualization
- Integration with HDFS

---

## Statistics

| Metric | Value |
| :----- | ----: |
| Total Files | 25+ |
| Source Code Lines | 2,500+ |
| Documentation Lines | 2,500+ |
| Components | 7 |
| Deployment Options | 5 |
| API Endpoints | 7 |
| Cities (Default) | 5 |
| Data Points/Day | 7,200+ |

---

## Support

### Quick Help
- **Setup Issues?** → See [SETUP.md - Troubleshooting](SETUP.md#troubleshooting)
- **API Questions?** → See [API.md](API.md)
- **System Design?** → See [ARCHITECTURE.md](ARCHITECTURE.md)
- **Deployment?** → See [DEPLOYMENT.md](DEPLOYMENT.md)

### External Resources
- OpenWeatherMap: https://openweathermap.org/api
- Kafka: https://kafka.apache.org
- Hadoop: https://hadoop.apache.org
- Spark: https://spark.apache.org
- Flask: https://flask.palletsprojects.com

---

## Next Steps

### Immediate
1. Read [README.md](README.md)
2. Follow [QUICKSTART.md](QUICKSTART.md)
3. View dashboard at http://localhost:5000

### Short Term
1. Study [ARCHITECTURE.md](ARCHITECTURE.md)
2. Review source code
3. Customize for your needs

### Long Term
1. Deploy using [DEPLOYMENT.md](DEPLOYMENT.md)
2. Set up monitoring
3. Scale for production

---

**Last Updated:** 2024
**Version:** 1.0
**Status:** Complete

**Start here:** [QUICKSTART.md](QUICKSTART.md) or [README.md](README.md)
