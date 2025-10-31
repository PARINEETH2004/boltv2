# Flask API Documentation

## Base URL

```
http://localhost:5000
```

## Endpoints

### Dashboard

#### GET /

Main dashboard page with real-time visualizations.

**Response:** HTML page with dashboard UI

**Example:**
```bash
curl http://localhost:5000/
```

---

### City Statistics

#### GET /api/city-statistics

Returns aggregated statistics for each city (average, min, max, standard deviation).

**Response:**
```json
{
  "data": [
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
      "avg_pressure": 1013.2,
      "computation_time": "2024-10-31T14:32:15.123456"
    },
    {
      "city": "London",
      "record_count": 110,
      "avg_temperature": 12.8,
      "min_temperature": 10.5,
      "max_temperature": 15.2,
      "stddev_temperature": 1.23,
      "avg_humidity": 72.5,
      "avg_wind_speed": 5.2,
      "total_rainfall": 0.3,
      "avg_pressure": 1012.8,
      "computation_time": "2024-10-31T14:32:15.123456"
    }
  ],
  "timestamp": "2024-10-31T14:32:15.123456"
}
```

**Status Codes:**
- `200 OK` - Success
- `404 Not Found` - No analytics data available
- `500 Internal Server Error` - Server error

**Example:**
```bash
curl http://localhost:5000/api/city-statistics
```

---

### Hourly Trends

#### GET /api/hourly-trends

Returns hourly aggregated data for each city.

**Response:**
```json
{
  "data": [
    {
      "city": "New York",
      "hour": "14",
      "record_count": 5,
      "avg_temperature": 15.4,
      "avg_humidity": 64.5,
      "avg_wind_speed": 4.2
    },
    {
      "city": "New York",
      "hour": "15",
      "record_count": 5,
      "avg_temperature": 15.7,
      "avg_humidity": 63.2,
      "avg_wind_speed": 4.8
    }
  ],
  "timestamp": "2024-10-31T14:32:15.123456"
}
```

**Status Codes:**
- `200 OK` - Success
- `404 Not Found` - No trends data available
- `500 Internal Server Error` - Server error

**Example:**
```bash
curl http://localhost:5000/api/hourly-trends
```

---

### Temperature Chart

#### GET /api/temperature-chart

Returns Plotly graph object for temperature trends visualization.

**Response:**
```json
{
  "data": [
    {
      "x": ["14", "15", "16", "17"],
      "y": [15.4, 15.7, 16.1, 15.8],
      "mode": "lines+markers",
      "name": "New York",
      "line": {"width": 2}
    },
    {
      "x": ["14", "15", "16", "17"],
      "y": [12.8, 13.2, 13.5, 13.1],
      "mode": "lines+markers",
      "name": "London",
      "line": {"width": 2}
    }
  ],
  "layout": {
    "title": "Hourly Temperature Trends",
    "xaxis": {"title": "Hour"},
    "yaxis": {"title": "Temperature (°C)"},
    "hovermode": "x unified",
    "height": 500
  }
}
```

**Status Codes:**
- `200 OK` - Success
- `404 Not Found` - No data available
- `500 Internal Server Error` - Server error

**Example:**
```bash
curl http://localhost:5000/api/temperature-chart
```

---

### Humidity Chart

#### GET /api/humidity-chart

Returns Plotly graph object for humidity visualization.

**Response:**
```json
{
  "data": [
    {
      "x": ["New York", "London", "Tokyo", "Sydney", "Dubai"],
      "y": [65.2, 72.5, 58.3, 55.1, 25.0],
      "type": "bar",
      "marker": {"color": "lightblue"}
    }
  ],
  "layout": {
    "title": "Average Humidity by City",
    "xaxis": {"title": "City"},
    "yaxis": {"title": "Humidity (%)"},
    "height": 400
  }
}
```

**Status Codes:**
- `200 OK` - Success
- `404 Not Found` - No data available
- `500 Internal Server Error` - Server error

**Example:**
```bash
curl http://localhost:5000/api/humidity-chart
```

---

### Detected Anomalies

#### GET /api/anomalies

Returns detected temperature anomalies (values > 3 standard deviations from mean).

**Response:**
```json
{
  "data": [
    {
      "timestamp": "2024-10-31T14:45:30.123456",
      "city": "Dubai",
      "temperature": 42.5,
      "mean_temp": 35.0,
      "std_temp": 2.1,
      "weather_main": "Clear",
      "weather_description": "clear sky"
    },
    {
      "timestamp": "2024-10-31T13:20:15.654321",
      "city": "Tokyo",
      "temperature": 5.2,
      "mean_temp": 20.0,
      "std_temp": 2.3,
      "weather_main": "Snow",
      "weather_description": "light snow"
    }
  ],
  "timestamp": "2024-10-31T14:32:15.123456"
}
```

**Status Codes:**
- `200 OK` - Success (empty array if no anomalies)
- `500 Internal Server Error` - Server error

**Example:**
```bash
curl http://localhost:5000/api/anomalies
```

---

### Raw Weather Data

#### GET /api/raw-data

Returns recent raw weather observations (limited to 100 most recent).

**Response:**
```json
{
  "data": [
    {
      "timestamp": "2024-10-31T15:00:00.000000",
      "city": "New York",
      "latitude": 40.7128,
      "longitude": -74.0060,
      "temperature": 15.5,
      "feels_like": 14.8,
      "humidity": 64,
      "pressure": 1013,
      "visibility": 10000,
      "wind_speed": 4.5,
      "wind_direction": 180,
      "cloudiness": 50,
      "rainfall": 0.0,
      "snowfall": 0.0,
      "weather_main": "Cloudy",
      "weather_description": "overcast clouds"
    },
    {
      "timestamp": "2024-10-31T14:59:00.000000",
      "city": "London",
      "latitude": 51.5074,
      "longitude": -0.1278,
      "temperature": 12.8,
      "feels_like": 12.0,
      "humidity": 72,
      "pressure": 1012,
      "visibility": 9000,
      "wind_speed": 5.2,
      "wind_direction": 270,
      "cloudiness": 75,
      "rainfall": 0.2,
      "snowfall": 0.0,
      "weather_main": "Rain",
      "weather_description": "light rain"
    }
  ],
  "count": 2,
  "timestamp": "2024-10-31T15:00:30.123456"
}
```

**Status Codes:**
- `200 OK` - Success (empty array if no data)
- `500 Internal Server Error` - Server error

**Example:**
```bash
curl http://localhost:5000/api/raw-data
```

---

## Error Responses

### 404 Not Found

```json
{
  "error": "Not found"
}
```

### 500 Internal Server Error

```json
{
  "error": "Internal server error"
}
```

### HDFS Connection Error

```json
{
  "error": "Failed to connect to HDFS: Connection refused"
}
```

---

## Data Types

### Temperature
- **Unit:** Celsius
- **Type:** Float
- **Range:** -50 to 60°C (typical)

### Humidity
- **Unit:** Percentage
- **Type:** Integer (0-100)

### Pressure
- **Unit:** Hectopascals (hPa)
- **Type:** Float
- **Typical Range:** 950-1050

### Wind Speed
- **Unit:** Meters per second (m/s)
- **Type:** Float

### Rainfall/Snowfall
- **Unit:** Millimeters
- **Type:** Float

### Timestamps
- **Format:** ISO 8601 (UTC)
- **Example:** `2024-10-31T15:00:00.000000`

---

## Rate Limiting

Currently, no rate limiting is implemented. For production:

```python
from flask_limiter import Limiter

limiter = Limiter(app, key_func=lambda: request.remote_addr)

@app.route('/api/city-statistics')
@limiter.limit("60 per minute")
def get_city_statistics():
    ...
```

---

## Authentication

Currently, no authentication is required. For production, implement JWT:

```python
from flask_jwt_extended import JWTManager

jwt = JWTManager(app)

@app.route('/api/city-statistics')
@jwt_required()
def get_city_statistics():
    ...
```

---

## Pagination

Currently, no pagination is implemented. For large datasets:

```python
@app.route('/api/raw-data')
def get_raw_data():
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 100, type=int)
    offset = (page - 1) * limit
    ...
```

---

## Caching

Currently, all requests fetch fresh data from HDFS. For performance:

```python
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@app.route('/api/city-statistics')
@cache.cached(timeout=300)  # 5 minutes
def get_city_statistics():
    ...
```

---

## WebSocket Support

For real-time updates, consider adding WebSocket support:

```python
from flask_socketio import SocketIO, emit

socketio = SocketIO(app)

@socketio.on('connect')
def on_connect():
    emit('data', get_city_statistics())

@socketio.on_event('subscribe_updates')
def on_subscribe_updates(data):
    emit('updates', get_raw_data())
```

---

## Testing

### Using curl

```bash
# Get city statistics
curl -X GET http://localhost:5000/api/city-statistics

# Get anomalies
curl -X GET http://localhost:5000/api/anomalies

# Get raw data
curl -X GET http://localhost:5000/api/raw-data
```

### Using Python

```python
import requests
import json

url = "http://localhost:5000/api/city-statistics"
response = requests.get(url)
data = response.json()
print(json.dumps(data, indent=2))
```

### Using JavaScript

```javascript
fetch('http://localhost:5000/api/city-statistics')
  .then(response => response.json())
  .then(data => console.log(data))
  .catch(error => console.error('Error:', error));
```

---

**Last Updated:** 2024
**Version:** 1.0
