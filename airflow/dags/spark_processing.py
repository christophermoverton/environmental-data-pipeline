from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago

# Define default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'start_date': days_ago(1),
}

# Define the DAG
dag = DAG(
    'spark_processing_dag',
    default_args=default_args,
    description='A DAG to run Spark jobs for data processing',
    schedule_interval='@daily',  # Set the schedule interval for the Spark processing
)

# Task to run the Spark job using BashOperator and docker exec
run_spark_job = BashOperator(
    task_id='run_spark_job',
    bash_command='docker exec -t spark-master spark-submit \
  --master spark://spark-master:7077 \
  --jars /opt/bitnami/spark/jars/postgresql-42.7.4.jar \
  --driver-class-path /opt/bitnami/spark/jars/postgresql-42.7.4.jar \
  /app/data_processing.py',
    dag=dag,
)
