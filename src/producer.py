import os
import json
import time
import logging
from datetime import datetime
import requests
from kafka import KafkaProducer
from kafka.errors import KafkaError

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')
KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:29092')

CITIES = [
    {'name': 'New York', 'lat': 40.7128, 'lon': -74.0060},
    {'name': 'London', 'lat': 51.5074, 'lon': -0.1278},
    {'name': 'Tokyo', 'lat': 35.6762, 'lon': 139.6503},
    {'name': 'Sydney', 'lat': -33.8688, 'lon': 151.2093},
    {'name': 'Dubai', 'lat': 25.2048, 'lon': 55.2708},
]

OPENWEATHER_URL = 'https://api.openweathermap.org/data/2.5/weather'


def fetch_weather_data(city):
    """Fetch weather data from OpenWeatherMap API for a given city."""
    try:
        params = {
            'lat': city['lat'],
            'lon': city['lon'],
            'appid': OPENWEATHER_API_KEY,
            'units': 'metric'
        }
        response = requests.get(OPENWEATHER_URL, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        weather_record = {
            'timestamp': datetime.utcnow().isoformat(),
            'city': city['name'],
            'latitude': city['lat'],
            'longitude': city['lon'],
            'temperature': data.get('main', {}).get('temp'),
            'feels_like': data.get('main', {}).get('feels_like'),
            'humidity': data.get('main', {}).get('humidity'),
            'pressure': data.get('main', {}).get('pressure'),
            'visibility': data.get('visibility'),
            'wind_speed': data.get('wind', {}).get('speed'),
            'wind_direction': data.get('wind', {}).get('deg'),
            'cloudiness': data.get('clouds', {}).get('all'),
            'rainfall': data.get('rain', {}).get('1h', 0),
            'snowfall': data.get('snow', {}).get('1h', 0),
            'weather_main': data.get('weather', [{}])[0].get('main'),
            'weather_description': data.get('weather', [{}])[0].get('description'),
        }
        logger.info(f"Fetched weather data for {city['name']}: {weather_record['temperature']}°C")
        return weather_record
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching weather for {city['name']}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error for {city['name']}: {e}")
        return None


def delivery_report(err, msg):
    """Callback for Kafka message delivery."""
    if err is not None:
        logger.error(f'Message delivery failed: {err}')
    else:
        logger.debug(f'Message delivered to {msg.topic()} [{msg.partition()}]')


def main():
    """Main producer loop."""
    logger.info("Starting Kafka Producer Service...")

    try:
        producer = KafkaProducer(
            bootstrap_servers=[KAFKA_BOOTSTRAP_SERVERS],
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            acks='all',
            retries=3,
        )
        logger.info("Successfully connected to Kafka broker")
    except KafkaError as e:
        logger.error(f"Failed to connect to Kafka: {e}")
        return

    iteration = 0
    while True:
        try:
            iteration += 1
            logger.info(f"--- Data collection cycle {iteration} ---")

            for city in CITIES:
                weather_data = fetch_weather_data(city)

                if weather_data:
                    future = producer.send(
                        'weather_data',
                        value=weather_data
                    )
                    future.add_errback(lambda x: logger.error(f"Send failed: {x}"))
                    future.add_callback(delivery_report)
                else:
                    logger.warning(f"Skipped sending data for {city['name']}")

            producer.flush()
            logger.info(f"Completed cycle {iteration}. Waiting 60 seconds for next collection...")
            time.sleep(60)

        except KeyboardInterrupt:
            logger.info("Producer interrupted by user")
            break
        except Exception as e:
            logger.error(f"Error in producer loop: {e}")
            time.sleep(10)

    producer.close()
    logger.info("Producer service stopped")


if __name__ == '__main__':
    if not OPENWEATHER_API_KEY:
        logger.error("OPENWEATHER_API_KEY environment variable not set")
        exit(1)

    main()
