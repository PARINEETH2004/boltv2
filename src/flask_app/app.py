import os
import json
import logging
from datetime import datetime
from flask import Flask, render_template, jsonify, request
from hdfs import InsecureClient
import plotly.graph_objects as go
import plotly.utils

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

HADOOP_NAME_NODE = os.getenv('HADOOP_NAME_NODE', 'namenode:8020')
HDFS_BASE_PATH = f'/weather_data'

hdfs_client = None


def initialize_hdfs():
    """Initialize HDFS client."""
    global hdfs_client
    try:
        hdfs_url = f'http://{HADOOP_NAME_NODE}'
        hdfs_client = InsecureClient(hdfs_url, user='root')
        logger.info(f"Connected to HDFS at {hdfs_url}")
        return True
    except Exception as e:
        logger.error(f"Failed to connect to HDFS: {e}")
        return False


def read_json_file(path):
    """Read JSON file from HDFS."""
    try:
        with hdfs_client.read(path) as reader:
            content = reader.read().decode('utf-8')
            return json.loads(content)
    except Exception as e:
        logger.error(f"Error reading {path}: {e}")
        return None


def read_jsonl_file(path):
    """Read JSONL file from HDFS (line-delimited JSON)."""
    try:
        records = []
        with hdfs_client.read(path) as reader:
            content = reader.read().decode('utf-8')
            for line in content.strip().split('\n'):
                if line:
                    records.append(json.loads(line))
        return records
    except Exception as e:
        logger.error(f"Error reading JSONL {path}: {e}")
        return []


def list_hdfs_files(path):
    """List files in HDFS directory."""
    try:
        return hdfs_client.list_dir(path)
    except Exception as e:
        logger.error(f"Error listing {path}: {e}")
        return []


@app.route('/')
def dashboard():
    """Main dashboard page."""
    return render_template('dashboard.html')


@app.route('/api/city-statistics')
def get_city_statistics():
    """Get city-level statistics."""
    try:
        analytics_path = f'{HDFS_BASE_PATH}/analytics/city_statistics'

        files = list_hdfs_files(analytics_path)
        if not files:
            return jsonify({'error': 'No analytics data available'}), 404

        stats = []
        for file in files:
            if file.endswith('.json'):
                file_path = f'{analytics_path}/{file}'
                data = read_json_file(file_path)
                if data:
                    stats.append(data)

        return jsonify({'data': stats, 'timestamp': datetime.utcnow().isoformat()})

    except Exception as e:
        logger.error(f"Error fetching city statistics: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/hourly-trends')
def get_hourly_trends():
    """Get hourly trends data."""
    try:
        analytics_path = f'{HDFS_BASE_PATH}/analytics/hourly_trends'

        files = list_hdfs_files(analytics_path)
        if not files:
            return jsonify({'error': 'No trends data available'}), 404

        trends = []
        for file in files:
            if file.endswith('.json'):
                file_path = f'{analytics_path}/{file}'
                data = read_json_file(file_path)
                if data:
                    trends.append(data)

        return jsonify({'data': trends, 'timestamp': datetime.utcnow().isoformat()})

    except Exception as e:
        logger.error(f"Error fetching hourly trends: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/anomalies')
def get_anomalies():
    """Get detected anomalies."""
    try:
        analytics_path = f'{HDFS_BASE_PATH}/analytics/anomalies'

        files = list_hdfs_files(analytics_path)
        if not files:
            return jsonify({'data': [], 'timestamp': datetime.utcnow().isoformat()})

        anomalies = []
        for file in files:
            if file.endswith('.json'):
                file_path = f'{analytics_path}/{file}'
                data = read_json_file(file_path)
                if data:
                    anomalies.extend(data if isinstance(data, list) else [data])

        return jsonify({'data': anomalies, 'timestamp': datetime.utcnow().isoformat()})

    except Exception as e:
        logger.error(f"Error fetching anomalies: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/raw-data')
def get_raw_data():
    """Get recent raw weather data."""
    try:
        raw_path = f'{HDFS_BASE_PATH}/raw'

        dirs = list_hdfs_files(raw_path)
        if not dirs:
            return jsonify({'error': 'No raw data available'}), 404

        raw_records = []
        limit = 100

        for year_dir in sorted(dirs, reverse=True)[:1]:
            year_path = f'{raw_path}/{year_dir}'
            month_dirs = list_hdfs_files(year_path)

            for month_dir in sorted(month_dirs, reverse=True)[:1]:
                month_path = f'{year_path}/{month_dir}'
                day_dirs = list_hdfs_files(month_path)

                for day_dir in sorted(day_dirs, reverse=True)[:1]:
                    day_path = f'{month_path}/{day_dir}'
                    hour_files = list_hdfs_files(day_path)

                    for hour_file in sorted(hour_files, reverse=True):
                        if hour_file.endswith('.jsonl'):
                            file_path = f'{day_path}/{hour_file}'
                            records = read_jsonl_file(file_path)
                            raw_records.extend(records)

                            if len(raw_records) >= limit:
                                raw_records = raw_records[:limit]
                                break

                    if len(raw_records) >= limit:
                        break

                if len(raw_records) >= limit:
                    break

        return jsonify({
            'data': raw_records,
            'count': len(raw_records),
            'timestamp': datetime.utcnow().isoformat()
        })

    except Exception as e:
        logger.error(f"Error fetching raw data: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/temperature-chart')
def get_temperature_chart():
    """Generate temperature trend chart."""
    try:
        analytics_path = f'{HDFS_BASE_PATH}/analytics/hourly_trends'
        files = list_hdfs_files(analytics_path)

        if not files:
            return jsonify({'error': 'No data available'}), 404

        trends_data = {}

        for file in files:
            if file.endswith('.json'):
                file_path = f'{analytics_path}/{file}'
                data = read_json_file(file_path)
                if data:
                    for record in (data if isinstance(data, list) else [data]):
                        city = record.get('city', 'Unknown')
                        if city not in trends_data:
                            trends_data[city] = {'hours': [], 'temps': []}
                        trends_data[city]['hours'].append(record.get('hour', ''))
                        trends_data[city]['temps'].append(record.get('avg_temperature', 0))

        fig = go.Figure()

        for city, data in trends_data.items():
            fig.add_trace(go.Scatter(
                x=data['hours'],
                y=data['temps'],
                mode='lines+markers',
                name=city,
                line=dict(width=2)
            ))

        fig.update_layout(
            title='Hourly Temperature Trends',
            xaxis_title='Hour',
            yaxis_title='Temperature (°C)',
            hovermode='x unified',
            height=500
        )

        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return graphJSON

    except Exception as e:
        logger.error(f"Error generating temperature chart: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/humidity-chart')
def get_humidity_chart():
    """Generate humidity chart."""
    try:
        stats_path = f'{HDFS_BASE_PATH}/analytics/city_statistics'
        files = list_hdfs_files(stats_path)

        if not files:
            return jsonify({'error': 'No data available'}), 404

        cities = []
        humidities = []

        for file in files:
            if file.endswith('.json'):
                file_path = f'{stats_path}/{file}'
                data = read_json_file(file_path)
                if data:
                    for record in (data if isinstance(data, list) else [data]):
                        cities.append(record.get('city', 'Unknown'))
                        humidities.append(record.get('avg_humidity', 0))

        fig = go.Figure(data=[
            go.Bar(x=cities, y=humidities, marker_color='lightblue')
        ])

        fig.update_layout(
            title='Average Humidity by City',
            xaxis_title='City',
            yaxis_title='Humidity (%)',
            height=400
        )

        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return graphJSON

    except Exception as e:
        logger.error(f"Error generating humidity chart: {e}")
        return jsonify({'error': str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({'error': 'Internal server error'}), 500


@app.before_request
def before_request():
    """Initialize HDFS before processing requests."""
    global hdfs_client
    if hdfs_client is None:
        initialize_hdfs()


if __name__ == '__main__':
    initialize_hdfs()
    app.run(host='0.0.0.0', port=5000, debug=False)
