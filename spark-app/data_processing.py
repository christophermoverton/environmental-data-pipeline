from pyspark.sql import SparkSession

# Initialize Spark Session
spark = SparkSession.builder.appName("EnvironmentalDataProcessing").getOrCreate()

# Define JDBC URL and properties
jdbc_url = "jdbc:postgresql://postgres:5432/airflow"
jdbc_properties = {
    "user": "airflow",
    "password": "airflow",
    "driver": "org.postgresql.Driver"  # Specify the PostgreSQL driver
}

try:
    # Read weather data from PostgreSQL using JDBC
    weather_df = spark.read \
        .format("jdbc") \
        .option("url", jdbc_url) \
        .option("dbtable", "weather_data") \
        .options(**jdbc_properties) \
        .load()

    # Perform analysis: Calculate average temperature for each city
    weather_df.createOrReplaceTempView("weather")
    avg_temp_df = spark.sql("SELECT city, AVG(temperature) as avg_temperature FROM weather GROUP BY city")

    # Load air quality data from PostgreSQL
    air_quality_df = spark.read \
        .format("jdbc") \
        .option("url", jdbc_url) \
        .option("dbtable", "air_quality_data") \
        .options(**jdbc_properties) \
        .load()

    # Perform analysis: Calculate average AQI for each city
    air_quality_df.createOrReplaceTempView("air_quality")
    avg_aqi_df = spark.sql("SELECT city, AVG(aqi) as avg_aqi FROM air_quality GROUP BY city")

    # Show the results
    avg_temp_df.show()
    avg_aqi_df.show()

    # Save results back to PostgreSQL
    avg_temp_df.write \
        .format("jdbc") \
        .option("url", jdbc_url) \
        .option("dbtable", "avg_temperature") \
        .options(**jdbc_properties) \
        .mode("overwrite") \
        .save()

    avg_aqi_df.write \
        .format("jdbc") \
        .option("url", jdbc_url) \
        .option("dbtable", "avg_aqi") \
        .options(**jdbc_properties) \
        .mode("overwrite") \
        .save()

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # Stop Spark session
    spark.stop()
