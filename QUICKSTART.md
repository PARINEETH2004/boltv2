# Quick Start Guide

Get the Real-Time Weather Data Stream Analysis system running in 5 minutes.

## Prerequisites

- Docker & Docker Compose installed
- OpenWeatherMap API key (free from https://openweathermap.org/api)

## 1. Get Your API Key

1. Visit https://openweathermap.org/api
2. Sign up for a free account
3. Go to API Keys section
4. Copy your API key

## 2. Create Environment File

```bash
cat > .env << EOF
OPENWEATHER_API_KEY=your_api_key_here
KAFKA_BOOTSTRAP_SERVERS=kafka:29092
HADOOP_NAME_NODE=namenode:8020
SPARK_MASTER=spark://spark-master:7077
FLASK_ENV=production
EOF
```

## 3. Start All Services

```bash
docker-compose up -d
```

**Wait 30-60 seconds** for containers to initialize.

Check status:
```bash
docker-compose ps
```

All services should show "Up" status.

## 4. Initialize HDFS

```bash
docker-compose exec namenode bash << 'EOF'
hdfs dfs -mkdir -p /weather_data/raw /weather_data/analytics /weather_data/archive
hdfs dfs -chmod -R 755 /weather_data
EOF
```

## 5. Create Kafka Topic

```bash
docker-compose exec kafka kafka-topics.sh \
  --bootstrap-server kafka:29092 \
  --create \
  --topic weather_data \
  --partitions 3 \
  --replication-factor 1 \
  --if-not-exists
```

## 6. Monitor Data Flow (Optional)

Watch producer logs:
```bash
docker-compose logs -f producer
```

In another terminal, watch consumer:
```bash
docker-compose logs -f consumer
```

## 7. Run Analytics (After ~5 minutes of data collection)

```bash
docker-compose exec spark-master spark-submit \
  --master spark://spark-master:7077 \
  --deploy-mode client \
  --executor-memory 2g \
  --executor-cores 2 \
  --conf spark.hadoop.fs.defaultFS=hdfs://namenode:8020 \
  /path/to/src/analytics.py
```

## 8. View Dashboard

Open your browser:
```
http://localhost:5000
```

You should see:
- City statistics (temperature, humidity, pressure)
- Temperature trends chart
- Humidity by city chart
- Detected anomalies
- Recent raw data

## Verify Data Pipeline

### Check HDFS Data

```bash
docker-compose exec namenode hdfs dfs -ls -R /weather_data
```

Expected output:
```
/weather_data/raw/year=2024/month=10/day=31/weather_0000.jsonl
/weather_data/raw/year=2024/month=10/day=31/weather_0100.jsonl
...
```

### Check Kafka Messages

```bash
docker-compose exec kafka kafka-console-consumer.sh \
  --bootstrap-server kafka:29092 \
  --topic weather_data \
  --from-beginning \
  --max-messages 5
```

### Check Analytics Output

```bash
docker-compose exec namenode hdfs dfs -ls -R /weather_data/analytics
```

### View Flask Logs

```bash
docker-compose logs flask-app
```

## Accessing Services

| Service          | URL                     |
| :--------------- | :---------------------- |
| Dashboard        | http://localhost:5000   |
| Hadoop NameNode  | http://localhost:9870   |
| Spark Master UI  | http://localhost:8080   |

## Stopping Everything

```bash
docker-compose down
```

To remove all data and start fresh:
```bash
docker-compose down -v
```

## Troubleshooting

### No data on dashboard
1. Wait 5+ minutes for data collection
2. Run analytics job manually
3. Check logs: `docker-compose logs [service-name]`

### Producer not running
```bash
docker-compose logs producer
```

Check that `OPENWEATHER_API_KEY` is set in `.env`

### Consumer not writing to HDFS
```bash
docker-compose logs consumer
```

Verify HDFS is initialized (step 4)

### Analytics job fails
```bash
docker-compose logs spark-master
```

Ensure raw data exists in HDFS (step 8 verification)

## Next Steps

1. **Scale to more cities:** Edit `src/producer.py` and add cities to the `CITIES` list
2. **Change collection frequency:** Edit sleep duration in `producer.py` (line 58)
3. **Customize analytics:** Modify `src/analytics.py` for different computations
4. **Add alerts:** Implement email notifications for anomalies
5. **Deploy to cloud:** Use AWS EMR or GCP Dataproc

## Performance Notes

**Data Collection:**
- 5 cities × 1 request/minute = 300 API calls/hour
- Free tier: 1000 calls/day, so current setup uses ~30% of quota

**Storage:**
- ~3.5 MB raw data per day
- Analytics results: ~50 KB per run

**Processing Time:**
- Analytics job: 5-30 seconds (depending on data volume)
- Dashboard load: 1-2 seconds

---

**Need more help?** See SETUP.md for detailed configuration, ARCHITECTURE.md for system design, or API.md for endpoint documentation.
