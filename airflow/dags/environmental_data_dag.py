from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.utils.dates import days_ago
from airflow.hooks.postgres_hook import PostgresHook
import requests
import json
import os
from urllib.parse import quote

# List of cities to collect data from
cities = [
    {"city": "New York", "state": "New York", "country": "United States"},
    {"city": "Los Angeles", "state": "California", "country": "United States"},
    {"city": "Chicago", "state": "Illinois", "country": "United States"},
    {"city": "San Francisco", "state": "California", "country": "United States"},
    {"city": "London", "state": "England", "country": "United Kingdom"},
    {"city": "Manchester", "state": "England", "country": "United Kingdom"},
    {"city": "Paris", "state": "Île-de-France", "country": "France"},
    {"city": "Berlin", "state": "Berlin", "country": "Germany"},
    {"city": "Munich", "state": "Bavaria", "country": "Germany"},
    {"city": "Sydney", "state": "New South Wales", "country": "Australia"},
    {"city": "Melbourne", "state": "Victoria", "country": "Australia"},
    {"city": "Brisbane", "state": "Queensland", "country": "Australia"},
    {"city": "Perth", "state": "Western Australia", "country": "Australia"},
    {"city": "Rome", "state": "Lazio", "country": "Italy"},
    {"city": "Madrid", "state": "Community of Madrid", "country": "Spain"},
    {"city": "Amsterdam", "state": "North Holland", "country": "Netherlands"},
    {"city": "Vienna", "state": "Vienna", "country": "Austria"},
    {"city": "Oslo", "state": "Oslo", "country": "Norway"},
    {"city": "Stockholm", "state": "Stockholm County", "country": "Sweden"},
    {"city": "Dublin", "state": "Leinster", "country": "Ireland"},
]


# Function to fetch weather data
def fetch_weather_data(**kwargs):
    api_key = os.getenv("OPENWEATHERMAP_API_KEY")
    for city_info in cities:
        city = city_info['city']
        encoded_city = quote(city)
        url = f"http://api.openweathermap.org/data/2.5/weather?q={encoded_city}&appid={api_key}"

        response = requests.get(url)
        data = response.json()

        if response.status_code != 200 or 'main' not in data:
            print(f"Error fetching weather data for {city}: {data.get('message', 'Unknown error')}")
            continue

        # Save the data to a file
        with open(f'/opt/airflow/logs/weather_data_{city}.json', 'w') as f:
            json.dump(data, f)
        print(f"Weather data for {city} fetched successfully.")

        # Push data to XCom for further use
        kwargs['ti'].xcom_push(key=f'weather_data_{city}', value=data)

# Function to fetch air quality data
def fetch_air_quality_data(**kwargs):
    api_key = os.getenv("AIRVISUAL_API_KEY")
    for city_info in cities:
        city = city_info['city']
        state = city_info['state']
        country = city_info['country']

        # Encode parameters
        encoded_city = quote(city)
        encoded_state = quote(state)
        encoded_country = quote(country)

        url = f"http://api.airvisual.com/v2/city?city={encoded_city}&state={encoded_state}&country={encoded_country}&key={api_key}"

        response = requests.get(url)
        data = response.json()

        if response.status_code != 200 or 'data' not in data:
            print(f"Error fetching air quality data for {city}: {data.get('message', 'Unknown error')}")
            continue

        # Save the data to a file
        with open(f'/opt/airflow/logs/air_quality_data_{city}.json', 'w') as f:
            json.dump(data, f)
        print(f"Air quality data for {city} fetched successfully.")

        # Push data to XCom for further use
        kwargs['ti'].xcom_push(key=f'air_quality_data_{city}', value=data)

# Function to insert weather data into the database
def insert_weather_data(**kwargs):
    postgres_hook = PostgresHook(postgres_conn_id='postgres_default')
    for city_info in cities:
        city = city_info['city']
        weather_data = kwargs['ti'].xcom_pull(key=f'weather_data_{city}', task_ids='fetch_weather_data')

        if not weather_data:
            print(f"No weather data available for {city}")
            continue

        # Extract necessary fields from weather data
        temperature = weather_data["main"]["temp"]
        humidity = weather_data["main"]["humidity"]
        pressure = weather_data["main"]["pressure"]
        weather_description = weather_data["weather"][0]["description"]

        # Insert weather data into the database
        insert_sql = """
        INSERT INTO weather_data (city, temperature, humidity, pressure, weather_description)
        VALUES (%s, %s, %s, %s, %s);
        """
        postgres_hook.run(insert_sql, parameters=(city, temperature, humidity, pressure, weather_description))
        print(f"Inserted weather data for {city} into the database.")

# Function to insert air quality data into the database
def insert_air_quality_data(**kwargs):
    postgres_hook = PostgresHook(postgres_conn_id='postgres_default')
    for city_info in cities:
        city = city_info['city']
        air_quality_data = kwargs['ti'].xcom_pull(key=f'air_quality_data_{city}', task_ids='fetch_air_quality_data')

        if not air_quality_data:
            print(f"No air quality data available for {city}")
            continue

        # Extract necessary fields from air quality data
        aqi = air_quality_data["data"]["current"]["pollution"]["aqius"]
        main_pollutant = air_quality_data["data"]["current"]["pollution"]["mainus"]
        concentration = air_quality_data["data"]["current"]["pollution"]["aqius"]

        # Insert air quality data into the database
        insert_sql = """
        INSERT INTO air_quality_data (city, aqi, main_pollutant, concentration)
        VALUES (%s, %s, %s, %s);
        """
        postgres_hook.run(insert_sql, parameters=(city, aqi, main_pollutant, concentration))
        print(f"Inserted air quality data for {city} into the database.")

# Define default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'start_date': days_ago(1),
}

# Define the DAG
dag = DAG(
    'environmental_data_dag',
    default_args=default_args,
    description='A DAG to fetch weather and air quality data for multiple cities and store it in a database',
    schedule_interval='@hourly',
)

# Task to create the schema in PostgreSQL
create_schema_task = PostgresOperator(
    task_id='create_schema',
    postgres_conn_id='postgres_default',
    sql="""
    CREATE TABLE IF NOT EXISTS weather_data (
        city VARCHAR(50),
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        temperature FLOAT,
        humidity INTEGER,
        pressure INTEGER,
        weather_description VARCHAR(255)
    );
    CREATE TABLE IF NOT EXISTS air_quality_data (
        city VARCHAR(50),
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        aqi INTEGER,
        main_pollutant VARCHAR(50),
        concentration FLOAT
    );
    """,
    dag=dag,
)

# Task to fetch weather data
fetch_weather_task = PythonOperator(
    task_id='fetch_weather_data',
    python_callable=fetch_weather_data,
    provide_context=True,
    dag=dag,
)

# Task to fetch air quality data
fetch_air_quality_task = PythonOperator(
    task_id='fetch_air_quality_data',
    python_callable=fetch_air_quality_data,
    provide_context=True,
    dag=dag,
)

# Task to insert weather data into the database
insert_weather_task = PythonOperator(
    task_id='insert_weather_data',
    python_callable=insert_weather_data,
    provide_context=True,
    dag=dag,
)

# Task to insert air quality data into the database
insert_air_quality_task = PythonOperator(
    task_id='insert_air_quality_data',
    python_callable=insert_air_quality_data,
    provide_context=True,
    dag=dag,
)

# Set task dependencies
create_schema_task >> [fetch_weather_task, fetch_air_quality_task]
fetch_weather_task >> insert_weather_task
fetch_air_quality_task >> insert_air_quality_task
