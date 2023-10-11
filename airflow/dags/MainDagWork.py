from clickhouse_driver import Client
from datetime import datetime
import csv, json
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.bash_operator import BashOperator
from airflow.operators.empty import EmptyOperator
from airflow.models import Variable
from airflow.utils.dates import days_ago
from airflow.decorators import task_group
import time
from datetime import datetime, timedelta
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options as ChromeOptions
import pandas as pd
import os

with open('/airflow/dags/config_connections.json', 'r') as config_file:
    connections_config = json.load(config_file)

conn_config = connections_config['click_connect']
config = {
    'database': conn_config['database'],
    'user': conn_config['user'],
    'password': conn_config['password'],
    'host': conn_config['host'],
    'port': conn_config['port'],
}

##ch_connection = ClickHouseConnection.get_connection()

client = Client(**config)

with open('/airflow/dags/config_connections_resources.json', 'r') as config_file:
    cfg_resources = json.load(config_file)

Variable.set("shares_resources", cfg_resources, serialize_json=True)

dag_resources = Variable.get("shares_resources", deserialize_json=True)

url_zarplata = dag_resources.get('zarplata')
url_careerist = dag_resources.get('careerist')
url_getmatch = dag_resources.get('getmatch')

#options = ChromeOptions()

#TODO доработать фрэйм под унифицированные колонки или под каждый парсинг индивидуально
df = pd.DataFrame(columns=['name_vacancy', 'organization', 'url', 'skils', 'city', 'min_price', 'max_price', 'current', 'vac', 'busyness', 'data'])

def create_table_zarplata():
    """
    Создание таблицы для ресурса зарплата.ру
    """
    table_name = 'zarplata_table'
    drop_table_query = f"DROP TABLE IF EXISTS {config['database']}.{table_name};"
    client.execute(drop_table_query)
    create_table_query  = f"""
    CREATE TABLE {config['database']}.{table_name}(
        name_vacancy String
        organization String
        url String
        skils String
        city String
        min_price Decimal
        max_price Decimal
        current String
        vac String
        busyness String
        data Data
    ) ENGINE = AggregatingMergeTree
    """
    
    #Семейство MergeTree Наиболее универсальные и функциональные движки таблиц для задач с высокой загрузкой. Общим свойством этих движков является быстрая вставка данных с последующей фоновой обработкой данных. Движки *MergeTree поддерживают репликацию данных (в Replicated* версиях движков), партиционирование, и другие возможности не поддержанные для других движков.
    
    client.execute(create_table_query)
    
def create_table_careerist():
    """
    Создание таблицы для ресурса careerist
    """
    table_name = 'careerist_table'
    drop_table_query = f"DROP TABLE IF EXISTS {config['database']}.{table_name};"
    client.execute(drop_table_query)
    create_table_query  = f"""
    CREATE TABLE {config['database']}.{table_name}(
        name_vacancy String
        organization String
        url String
        skils String
        city String
        min_price Decimal
        max_price Decimal
        current String
        vac String
        busyness String
        data Data
    ) ENGINE = AggregatingMergeTree
    """
    client.execute(create_table_query)
    
def create_table_getmatch():
    """
    Создание таблицы для ресурса getmatch
    """
    table_name = 'getmatch_table'
    drop_table_query = f"DROP TABLE IF EXISTS {config['database']}.{table_name};"
    client.execute(drop_table_query)
    create_table_query  = f"""
    CREATE TABLE {config['database']}.{table_name}(
        name_vacancy String
        organization String
        price Decimal
        url String
        skils String
        city String
    ) ENGINE = AggregatingMergeTree
    """
    client.execute(create_table_query)

def create_table_for_all_parsed_data():
    """
    Создание таблицы для внесения всех данных
    """
    table_name = 'parsed_table_all_data'
    drop_table_query = f"DROP TABLE IF EXISTS {config['database']}.{table_name};"
    client.execute(drop_table_query)
    create_table_query  = f"""
    CREATE TABLE {config['database']}.{table_name}(
        name_vacancy String
        organization String
        price Decimal
        url String
        skils String
        city String
    ) ENGINE = S3('./parsed_data/*', 'CSV')
    """
    client.execute(create_table_query)

def parse_zarplata():
    with webdriver.Remote(command_executor='http://selenium-router:4444/wd/hub', options=options) as browser:

def parse_careerist():
    with webdriver.Remote(command_executor='http://selenium-router:4444/wd/hub', options=options) as browser:

def parse_getmatch():
    with webdriver.Remote(command_executor='http://selenium-router:4444/wd/hub', options=options) as browser:

def parced_data_to_table_zarplata():
    """
    загрузка спарсенных данных c сайта zarplata из csv в таблицу ClickHouse
    """    
    table_name = 'zarplata_table'
    with open(f'./parsed_data/zarplata_data.csv', 'r') as f:
        data = [row.split(';') for row in f]
    insert_query = f"INSERT INTO {config['database']}.{table_name} FORMAT CSV"
    client.execute(insert_query, data)

def parced_data_to_table_careerist():
    """
    загрузка спарсенных данных c сайта careerist из csv в таблицу ClickHouse
    """    
    table_name = 'careerist_table'
    with open(f'./parsed_data/careerist_data.csv', 'r') as f:
        data = [row.split(';') for row in f]
    insert_query = f"INSERT INTO {config['database']}.{table_name} FORMAT CSV"
    client.execute(insert_query, data)

def parced_data_to_table_getmatch():
    """
    загрузка спарсенных данных c сайта getmatch из csv в таблицу ClickHouse
    """    
    table_name = 'getmatch_table'
    with open(f'./parsed_data/getmatch_data.csv', 'r') as f:
        data = [row.split(';') for row in f]
    insert_query = f"INSERT INTO {config['database']}.{table_name} FORMAT CSV"
    client.execute(insert_query, data)

def all_parced_data_to_one_table():
    """
    загрузка спарсенных данных из csv в таблицу ClickHouse
    """    
    table_name = 'parsed_table_all_data'
    with open(f'./parsed_data/*.csv', 'r') as f:
        data = [row.split(';') for row in f]
    insert_query = f"INSERT INTO {config['database']}.{table_name} FORMAT CSV"
    client.execute(insert_query, data)

    
with DAG(
        dag_id = "parse_dag", 
        schedule_interval = "@daily",
        default_args = {"owner": "airflow", 'start_date': days_ago(1)}, 
        tags=[], 
        catchup = False) 
        as dag:
        
    start = EmptyOperator(
        task_id="start",
    )
    create_table_zarplata = PythonOperator(
        task_id='create_table_zarplata',
        python_callable=create_table_zarplata,
    #    start_date=days_ago(1),
    #    schedule_interval='@daily',
        dag=dag,
        tags=['create_table_zarplata']
    )

    create_table_careerist = PythonOperator(
        task_id='create_table_careerist',
        python_callable=create_table_careerist,
    #    start_date=days_ago(1),
    #    schedule_interval='@daily',
        dag=dag,
        tags=['create_table_careerist']
    )

    create_table_getmatch = PythonOperator(
        task_id='create_table_getmatch',
        python_callable=create_table_getmatch,
    #   start_date=days_ago(1),
    #    schedule_interval='@daily',
        dag=dag,
        tags=['create_table_getmatch']
    )

    parse_zarplata = PythonOperator(
        task_id='parse_zarplata',
        python_callable=parse_zarplata,
    #   start_date=days_ago(1),
    #    schedule_interval='@daily',
        dag=dag,
        tags=['parse_zarplata']
    )

    parse_careerist = PythonOperator(
        task_id='parse_careerist',
        python_callable=parse_careerist,
    #   start_date=days_ago(1),
    #    schedule_interval='@daily',
        dag=dag,
        tags=['parse_careerist']
    )

    parse_getmatch = PythonOperator(
        task_id='parse_getmatch',
        python_callable=parse_getmatch,
    #   start_date=days_ago(1),
    #    schedule_interval='@daily',
        dag=dag,
        tags=['parse_getmatch']
    )

    parced_data_to_table_zarplata = PythonOperator(
        task_id='parced_data_to_table_zarplata',
        python_callable=parced_data_to_table_zarplata,
    #   start_date=days_ago(1),
    #    schedule_interval='@daily',
        dag=dag,
        tags=['parced_data_to_table_zarplata']
    )

    parced_data_to_table_careerist = PythonOperator(
        task_id='parced_data_to_table_careerist',
        python_callable=parced_data_to_table_careerist,
    #   start_date=days_ago(1),
    #    schedule_interval='@daily',
        dag=dag,
        tags=['parced_data_to_table_careerist']
    )

    parced_data_to_table_getmatch = PythonOperator(
        task_id='parced_data_to_table_getmatch',
        python_callable=parced_data_to_table_getmatch,
    #   start_date=days_ago(1),
    #    schedule_interval='@daily',
        dag=dag,
        tags=['parced_data_to_table_getmatch']
    )
    
    all_parced_data_to_one_table = PythonOperator(
        all_parced_data_to_one_table = PythonOperator(
        task_id='all_parced_data_to_one_table',
        python_callable=all_parced_data_to_one_table,
    #   start_date=days_ago(1),
    #    schedule_interval='@daily',
        dag=dag,
        tags=['all_parced_data_to_one_table']
    )

    end = EmptyOperator(
        task_id="end"
    )

@task_group()
 def group_create_table():
     create_table_zarplata = EmptyOperator(task_id="create_table_zarplata")
     create_table_careerist = EmptyOperator(task_id="create_table_careerist")
     create_table_getmatch = EmptyOperator(task_id="create_table_getmatch")


group_create_table()
parse_zarplata >> parced_data_to_table_zarplata >> parse_careerist >> parced_data_to_table_careerist >> parse_getmatch >> parced_data_to_table_getmatch

parse_zarplata >> parse_careerist >> parse_getmatch >> all_parced_data_to_one_table
