import os
import json
import logging
from datetime import datetime, timedelta
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, avg, min, max, stddev, count, window,
    when, round as spark_round, regexp_extract
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

HADOOP_NAME_NODE = os.getenv('HADOOP_NAME_NODE', 'namenode:8020')
SPARK_MASTER = os.getenv('SPARK_MASTER', 'spark://spark-master:7077')

HDFS_BASE_PATH = f'hdfs://{HADOOP_NAME_NODE}/weather_data'
HDFS_RAW_DATA = f'{HDFS_BASE_PATH}/raw'
HDFS_ANALYTICS_OUTPUT = f'{HDFS_BASE_PATH}/analytics'


def create_spark_session():
    """Create or retrieve a Spark session."""
    spark = SparkSession.builder \
        .appName("WeatherAnalytics") \
        .master(SPARK_MASTER) \
        .config("spark.hadoop.fs.defaultFS", f"hdfs://{HADOOP_NAME_NODE}") \
        .config("spark.executor.memory", "2g") \
        .config("spark.executor.cores", "2") \
        .getOrCreate()

    spark.sparkContext.setLogLevel("INFO")
    logger.info(f"Spark session created. Master: {SPARK_MASTER}")
    return spark


def read_weather_data(spark, date_filter=None):
    """Read weather data from HDFS."""
    try:
        logger.info(f"Reading weather data from {HDFS_RAW_DATA}")

        df = spark.read \
            .option("multiline", "false") \
            .json(f"{HDFS_RAW_DATA}/**/*.jsonl")

        if date_filter:
            df = df.filter(col("timestamp") >= date_filter)

        logger.info(f"Loaded {df.count()} weather records")
        return df

    except Exception as e:
        logger.error(f"Error reading weather data: {e}")
        return None


def compute_city_statistics(spark, df):
    """Compute statistics grouped by city."""
    try:
        logger.info("Computing city-level statistics...")

        stats_df = df.groupBy("city") \
            .agg(
                count("*").alias("record_count"),
                spark_round(avg("temperature"), 2).alias("avg_temperature"),
                spark_round(min("temperature"), 2).alias("min_temperature"),
                spark_round(max("temperature"), 2).alias("max_temperature"),
                spark_round(stddev("temperature"), 2).alias("stddev_temperature"),
                spark_round(avg("humidity"), 2).alias("avg_humidity"),
                spark_round(avg("wind_speed"), 2).alias("avg_wind_speed"),
                spark_round(avg("rainfall"), 4).alias("total_rainfall"),
                spark_round(avg("pressure"), 2).alias("avg_pressure"),
            ) \
            .withColumn("computation_time", datetime.utcnow().isoformat())

        logger.info("City statistics computed successfully")
        return stats_df

    except Exception as e:
        logger.error(f"Error computing city statistics: {e}")
        return None


def compute_hourly_trends(spark, df):
    """Compute hourly trends for each city."""
    try:
        logger.info("Computing hourly trends...")

        df_with_time = df.withColumn(
            "hour",
            regexp_extract(col("timestamp"), r"(\d{2}):00", 1)
        )

        hourly_df = df_with_time.groupBy("city", "hour") \
            .agg(
                count("*").alias("record_count"),
                spark_round(avg("temperature"), 2).alias("avg_temperature"),
                spark_round(avg("humidity"), 2).alias("avg_humidity"),
                spark_round(avg("wind_speed"), 2).alias("avg_wind_speed"),
            ) \
            .orderBy("city", "hour")

        logger.info("Hourly trends computed successfully")
        return hourly_df

    except Exception as e:
        logger.error(f"Error computing hourly trends: {e}")
        return None


def detect_anomalies(spark, df, temp_threshold_std=3):
    """Detect temperature anomalies using statistical methods."""
    try:
        logger.info(f"Detecting temperature anomalies (threshold: {temp_threshold_std} std devs)...")

        city_stats = df.groupBy("city") \
            .agg(
                avg("temperature").alias("mean_temp"),
                stddev("temperature").alias("std_temp")
            )

        df_with_stats = df.join(city_stats, on="city", how="left")

        anomalies_df = df_with_stats.withColumn(
            "is_anomaly",
            when(
                (abs(col("temperature") - col("mean_temp")) > (temp_threshold_std * col("std_temp"))),
                True
            ).otherwise(False)
        ) \
        .filter(col("is_anomaly") == True) \
        .select(
            "timestamp", "city", "temperature", "mean_temp",
            "std_temp", "weather_main", "weather_description"
        ) \
        .orderBy(col("timestamp").desc())

        anomaly_count = anomalies_df.count()
        logger.info(f"Detected {anomaly_count} anomalies")

        return anomalies_df

    except Exception as e:
        logger.error(f"Error detecting anomalies: {e}")
        return None


def save_results(df, output_path, mode="overwrite"):
    """Save results to HDFS."""
    try:
        if df is None:
            logger.warning(f"Skipping save for {output_path}: DataFrame is None")
            return

        df.coalesce(1).write \
            .mode(mode) \
            .json(output_path)

        logger.info(f"Results saved to {output_path}")

    except Exception as e:
        logger.error(f"Error saving results to {output_path}: {e}")


def main():
    """Main analytics pipeline."""
    logger.info("Starting Weather Analytics Pipeline...")

    spark = create_spark_session()

    try:
        yesterday = (datetime.utcnow() - timedelta(days=1)).isoformat()
        df = read_weather_data(spark, date_filter=yesterday)

        if df is None or df.count() == 0:
            logger.warning("No data available for analysis")
            return

        df.printSchema()

        city_stats_df = compute_city_statistics(spark, df)
        if city_stats_df:
            save_results(
                city_stats_df,
                f"{HDFS_ANALYTICS_OUTPUT}/city_statistics",
                mode="overwrite"
            )

        hourly_trends_df = compute_hourly_trends(spark, df)
        if hourly_trends_df:
            save_results(
                hourly_trends_df,
                f"{HDFS_ANALYTICS_OUTPUT}/hourly_trends",
                mode="overwrite"
            )

        anomalies_df = detect_anomalies(spark, df, temp_threshold_std=2)
        if anomalies_df and anomalies_df.count() > 0:
            save_results(
                anomalies_df,
                f"{HDFS_ANALYTICS_OUTPUT}/anomalies",
                mode="overwrite"
            )
        else:
            logger.info("No anomalies detected in current dataset")

        logger.info("Analytics pipeline completed successfully")

    except Exception as e:
        logger.error(f"Error in analytics pipeline: {e}")

    finally:
        spark.stop()
        logger.info("Spark session closed")


if __name__ == '__main__':
    main()
