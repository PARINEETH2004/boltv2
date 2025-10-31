import os
import json
import logging
from datetime import datetime
from kafka import KafkaConsumer
from kafka.errors import KafkaError
from hdfs import InsecureClient

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:29092')
HADOOP_NAME_NODE = os.getenv('HADOOP_NAME_NODE', 'namenode:8020')

HDFS_BASE_PATH = '/weather_data'
BATCH_SIZE = 100
WRITE_INTERVAL = 60


def initialize_hdfs_client():
    """Initialize HDFS client connection."""
    try:
        hdfs_url = f'http://{HADOOP_NAME_NODE}'
        client = InsecureClient(hdfs_url, user='root')
        logger.info(f"Connected to HDFS at {hdfs_url}")
        return client
    except Exception as e:
        logger.error(f"Failed to connect to HDFS: {e}")
        return None


def create_hdfs_directories(client):
    """Create necessary directories in HDFS."""
    try:
        if not client.status(HDFS_BASE_PATH, strict=False):
            client.makedirs(HDFS_BASE_PATH)
            logger.info(f"Created HDFS directory: {HDFS_BASE_PATH}")

        raw_path = f'{HDFS_BASE_PATH}/raw'
        if not client.status(raw_path, strict=False):
            client.makedirs(raw_path)
            logger.info(f"Created HDFS directory: {raw_path}")

    except Exception as e:
        logger.error(f"Error creating HDFS directories: {e}")


def get_hdfs_filepath(timestamp):
    """Generate HDFS file path based on timestamp."""
    dt = datetime.fromisoformat(timestamp)
    year = dt.year
    month = f"{dt.month:02d}"
    day = f"{dt.day:02d}"
    hour = f"{dt.hour:02d}"

    return f"{HDFS_BASE_PATH}/raw/year={year}/month={month}/day={day}/weather_{hour}00.jsonl"


def write_batch_to_hdfs(client, batch):
    """Write a batch of weather records to HDFS as JSONL."""
    if not batch:
        return

    try:
        first_timestamp = batch[0].get('timestamp')
        hdfs_file = get_hdfs_filepath(first_timestamp)

        logger.info(f"Writing {len(batch)} records to HDFS: {hdfs_file}")

        content = '\n'.join([json.dumps(record) for record in batch])

        try:
            with client.write(hdfs_file, append=True) as writer:
                writer.write(content.encode('utf-8') + b'\n')
            logger.info(f"Successfully wrote batch to {hdfs_file}")
        except Exception as e:
            logger.error(f"Error writing to {hdfs_file}: {e}")

    except Exception as e:
        logger.error(f"Error in write_batch_to_hdfs: {e}")


def main():
    """Main consumer loop."""
    logger.info("Starting Kafka Consumer Service...")

    hdfs_client = initialize_hdfs_client()
    if not hdfs_client:
        logger.error("Failed to initialize HDFS client")
        return

    create_hdfs_directories(hdfs_client)

    try:
        consumer = KafkaConsumer(
            'weather_data',
            bootstrap_servers=[KAFKA_BOOTSTRAP_SERVERS],
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id='weather_consumer_group',
            session_timeout_ms=30000,
            max_poll_records=100,
        )
        logger.info("Successfully connected to Kafka consumer group")
    except KafkaError as e:
        logger.error(f"Failed to create Kafka consumer: {e}")
        return

    batch = []
    record_count = 0

    try:
        while True:
            messages = consumer.poll(timeout_ms=5000, max_records=BATCH_SIZE)

            if not messages:
                if batch:
                    logger.info(f"No new messages. Writing accumulated batch of {len(batch)} records...")
                    write_batch_to_hdfs(hdfs_client, batch)
                    batch = []
                continue

            for topic_partition, records in messages.items():
                for message in records:
                    record = message.value
                    batch.append(record)
                    record_count += 1

                    if len(batch) >= BATCH_SIZE:
                        write_batch_to_hdfs(hdfs_client, batch)
                        batch = []

                    if record_count % 100 == 0:
                        logger.info(f"Processed {record_count} total records")

            if batch and len(batch) >= BATCH_SIZE:
                write_batch_to_hdfs(hdfs_client, batch)
                batch = []

    except KeyboardInterrupt:
        logger.info("Consumer interrupted by user")
        if batch:
            logger.info(f"Writing final batch of {len(batch)} records...")
            write_batch_to_hdfs(hdfs_client, batch)
    except Exception as e:
        logger.error(f"Error in consumer loop: {e}")
    finally:
        consumer.close()
        logger.info("Consumer service stopped")


if __name__ == '__main__':
    main()
