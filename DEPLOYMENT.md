# Deployment Guide

## Local Deployment (Development)

See `QUICKSTART.md` for rapid setup.

---

## AWS EMR Deployment

### Prerequisites

- AWS Account with EMR permissions
- AWS CLI installed and configured
- SSH key pair for EC2 instances

### Step 1: Create EMR Cluster

```bash
aws emr create-cluster \
  --name weather-analytics \
  --release-label emr-6.12.0 \
  --applications Name=Spark Name=Hadoop Name=Kafka \
  --instance-groups \
    InstanceGroupType=MASTER,InstanceCount=1,InstanceType=m5.xlarge \
    InstanceGroupType=CORE,InstanceCount=2,InstanceType=m5.xlarge \
    InstanceGroupType=TASK,InstanceCount=2,InstanceType=m5.xlarge \
  --ec2-attributes KeyName=your-key-pair \
  --bootstrap-actions Path=s3://your-bucket/bootstrap.sh \
  --service-role EMR_DefaultRole \
  --ec2-instance-profile EMR_EC2_DefaultRole \
  --region us-east-1
```

### Step 2: Upload Code to S3

```bash
aws s3 sync . s3://your-bucket/weather-analytics/
```

### Step 3: Create Bootstrap Script

**bootstrap.sh:**
```bash
#!/bin/bash
set -e

# Install Python dependencies
sudo pip install kafka-python requests hdfs plotly flask python-dotenv

# Create application directories
mkdir -p /home/hadoop/weather-analytics
cd /home/hadoop/weather-analytics

# Download code from S3
aws s3 sync s3://your-bucket/weather-analytics/ .

echo "EMR bootstrap completed"
```

Upload to S3:
```bash
aws s3 cp bootstrap.sh s3://your-bucket/bootstrap.sh
```

### Step 4: Configure Services

SSH into the master node:
```bash
aws emr describe-cluster --cluster-id <cluster-id> --region us-east-1 | grep MasterPublicDNS
ssh -i your-key-pair.pem hadoop@<master-dns>
```

Start Kafka:
```bash
cd /opt/kafka
bin/kafka-server-start.sh config/server.properties
```

Initialize HDFS:
```bash
hdfs dfs -mkdir -p /weather_data/{raw,analytics,archive}
```

### Step 5: Deploy Services

#### Producer

```bash
nohup python src/producer.py > logs/producer.log 2>&1 &
```

#### Consumer

```bash
nohup python src/consumer.py > logs/consumer.log 2>&1 &
```

#### Spark Job (Scheduled)

Add to crontab:
```bash
crontab -e
# Add: 0 * * * * spark-submit --master yarn --deploy-mode cluster src/analytics.py
```

#### Flask App

```bash
nohup python src/flask_app/app.py > logs/flask.log 2>&1 &
```

### Step 6: Access Services

Tunnel to master:
```bash
ssh -i your-key-pair.pem -N -L 5000:localhost:5000 hadoop@<master-dns> &
ssh -i your-key-pair.pem -N -L 8080:localhost:8080 hadoop@<master-dns> &
ssh -i your-key-pair.pem -N -L 9870:localhost:9870 hadoop@<master-dns> &
```

Access dashboard: http://localhost:5000

---

## Google Cloud Dataproc Deployment

### Step 1: Create Dataproc Cluster

```bash
gcloud dataproc clusters create weather-analytics \
  --region=us-central1 \
  --master-machine-type=n1-standard-4 \
  --worker-machine-type=n1-standard-4 \
  --num-workers=2 \
  --image-version=2.1 \
  --scopes=default,cloud-platform
```

### Step 2: Upload Code to GCS

```bash
gsutil -m cp -r . gs://your-bucket/weather-analytics/
```

### Step 3: Create Initialization Action

**init.sh:**
```bash
#!/bin/bash
sudo pip install kafka-python requests hdfs plotly flask

cd /tmp
gsutil cp -r gs://your-bucket/weather-analytics/* /opt/weather-analytics/
```

Upload and reference in cluster creation:
```bash
gsutil cp init.sh gs://your-bucket/init.sh
```

Re-create cluster with init script:
```bash
gcloud dataproc clusters create weather-analytics \
  --region=us-central1 \
  --image-version=2.1 \
  --initialization-actions gs://your-bucket/init.sh \
  ...
```

### Step 4: Submit Jobs

Producer job:
```bash
gcloud dataproc jobs submit pyspark src/producer.py \
  --cluster=weather-analytics \
  --region=us-central1 \
  -- --mode streaming
```

Spark analytics:
```bash
gcloud dataproc jobs submit spark src/analytics.py \
  --cluster=weather-analytics \
  --region=us-central1
```

### Step 5: Access Services

Create SSH tunnel:
```bash
gcloud compute ssh <master-node> \
  --project=your-project \
  --zone=us-central1-a \
  -- -N -L 5000:localhost:5000
```

---

## Kubernetes Deployment

### Step 1: Create K8s Manifests

**producer-deployment.yaml:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: weather-producer
spec:
  replicas: 1
  selector:
    matchLabels:
      app: producer
  template:
    metadata:
      labels:
        app: producer
    spec:
      containers:
      - name: producer
        image: weather-analytics:producer
        env:
        - name: KAFKA_BOOTSTRAP_SERVERS
          value: kafka-service:29092
        - name: OPENWEATHER_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-keys
              key: openweather
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

**consumer-deployment.yaml:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: weather-consumer
spec:
  replicas: 1
  selector:
    matchLabels:
      app: consumer
  template:
    metadata:
      labels:
        app: consumer
    spec:
      containers:
      - name: consumer
        image: weather-analytics:consumer
        env:
        - name: KAFKA_BOOTSTRAP_SERVERS
          value: kafka-service:29092
        - name: HADOOP_NAME_NODE
          value: namenode-service:8020
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1"
```

**flask-deployment.yaml:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: weather-flask
spec:
  replicas: 3
  selector:
    matchLabels:
      app: flask
  template:
    metadata:
      labels:
        app: flask
    spec:
      containers:
      - name: flask
        image: weather-analytics:flask
        ports:
        - containerPort: 5000
        env:
        - name: HADOOP_NAME_NODE
          value: namenode-service:8020
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: flask-service
spec:
  selector:
    app: flask
  ports:
  - protocol: TCP
    port: 80
    targetPort: 5000
  type: LoadBalancer
```

### Step 2: Build Docker Images

```bash
docker build -f Dockerfile.producer -t weather-analytics:producer .
docker build -f Dockerfile.consumer -t weather-analytics:consumer .
docker build -f Dockerfile.flask -t weather-analytics:flask .
```

Push to registry:
```bash
docker tag weather-analytics:producer gcr.io/your-project/weather-producer
docker push gcr.io/your-project/weather-producer
```

### Step 3: Deploy to K8s

```bash
kubectl create namespace weather
kubectl create secret generic api-keys \
  --from-literal=openweather=<your-api-key> \
  -n weather
kubectl apply -f producer-deployment.yaml -n weather
kubectl apply -f consumer-deployment.yaml -n weather
kubectl apply -f flask-deployment.yaml -n weather
```

### Step 4: Monitor Deployment

```bash
kubectl get pods -n weather
kubectl logs <pod-name> -n weather
kubectl port-forward svc/flask-service 5000:80 -n weather
```

---

## Docker Swarm Deployment

### Step 1: Initialize Swarm

```bash
docker swarm init
```

### Step 2: Create Stack

**docker-stack.yml:**
```yaml
version: '3.8'
services:
  producer:
    image: weather-analytics:producer
    deploy:
      replicas: 1
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
    environment:
      KAFKA_BOOTSTRAP_SERVERS: kafka:29092
      OPENWEATHER_API_KEY: ${OPENWEATHER_API_KEY}
    networks:
      - weather-net

  flask:
    image: weather-analytics:flask
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
    ports:
      - "5000:5000"
    environment:
      HADOOP_NAME_NODE: namenode:8020
    networks:
      - weather-net

  kafka:
    image: confluentinc/cp-kafka:7.5.0
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 1G
    environment:
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
    networks:
      - weather-net

networks:
  weather-net:
    driver: overlay
```

### Step 3: Deploy Stack

```bash
docker stack deploy -c docker-stack.yml weather
```

Monitor:
```bash
docker stack ps weather
docker stack services weather
```

---

## Production Hardening Checklist

- [ ] Enable SSL/TLS for all services
- [ ] Implement authentication (JWT, OAuth2)
- [ ] Set up monitoring (Prometheus, Grafana)
- [ ] Configure logging aggregation (ELK stack)
- [ ] Implement health checks
- [ ] Set up automated backups
- [ ] Configure rate limiting
- [ ] Enable encryption for data in transit
- [ ] Implement database replication
- [ ] Set up disaster recovery plan
- [ ] Configure auto-scaling policies
- [ ] Implement circuit breakers
- [ ] Enable audit logging
- [ ] Set up alerting rules
- [ ] Perform load testing

---

## Monitoring and Observability

### Prometheus Metrics

Add to docker-compose.yml:
```yaml
prometheus:
  image: prom/prometheus
  ports:
    - "9090:9090"
  volumes:
    - ./prometheus.yml:/etc/prometheus/prometheus.yml
```

### Grafana Dashboards

```yaml
grafana:
  image: grafana/grafana
  ports:
    - "3000:3000"
  environment:
    GF_SECURITY_ADMIN_PASSWORD: admin
```

### Logging Stack

```yaml
elasticsearch:
  image: docker.elastic.co/elasticsearch/elasticsearch:8.0.0

logstash:
  image: docker.elastic.co/logstash/logstash:8.0.0

kibana:
  image: docker.elastic.co/kibana/kibana:8.0.0
```

---

## Scaling Considerations

### Horizontal Scaling
- Add more Kafka partitions
- Deploy multiple consumer instances
- Scale Flask app replicas
- Add Spark worker nodes

### Vertical Scaling
- Increase executor memory for Spark
- Increase broker heap for Kafka
- Increase DataNode heap for Hadoop

### Resource Optimization
- Use S3/GCS instead of HDFS
- Implement caching layer (Redis)
- Use managed services where possible
- Compress data on disk

---

**Last Updated:** 2024
**Version:** 1.0
