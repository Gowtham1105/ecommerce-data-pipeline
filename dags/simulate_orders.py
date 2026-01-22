from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

# Default settings for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

# Define the DAG
dag = DAG(
    'simulate_user_orders',
    default_args=default_args,
    description='Runs the data generator script every 5 minutes',
    schedule_interval=timedelta(minutes=5), # <--- Runs every 5 mins
    catchup=False,
)

# The Task: Run the Python script
run_generator = BashOperator(
    task_id='generate_mock_orders',
    bash_command='python /opt/airflow/scripts/data_generator.py',
    dag=dag,
)