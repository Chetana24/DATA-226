# In Cloud Composer, add apache-airflow-providers-snowflake to PYPI Packages
from airflow import DAG
from airflow.models import Variable
from airflow.decorators import task
from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook

from datetime import timedelta
from datetime import datetime
import snowflake.connector
import requests



def return_snowflake_conn():

    # Initialize the SnowflakeHook
    hook = SnowflakeHook(snowflake_conn_id='snowflake_conn')
    
    # Execute the query and fetch results
    conn = hook.get_conn()
    return conn.cursor()


@task
def extract(url):
  r = requests.get(url)
  data = r.json()
  return(data)


@task
def transform(data):
  records = []
  for d in data["Time Series (Daily)"]:
    stock_info = data["Time Series (Daily)"][d]
    stock_info['date'] = d
    records.append(stock_info)
  return(records)


@task
def load(cur, data, target_table):
    staging_table = "dev.raw_data.TEMP_BRY_DATA"
    try:
        cur.execute("BEGIN;")
        cur.execute(f"""CREATE OR REPLACE TABLE {target_table} (OPEN FLOAT,HIGH FLOAT,LOW FLOAT,CLOSE FLOAT,VOLUME FLOAT,DATE date,SYMBOL VARCHAR(10), PRIMARY KEY(DATE, SYMBOL));""")
        cur.execute(f"""CREATE OR REPLACE TABLE {staging_table} (OPEN FLOAT,HIGH FLOAT,LOW FLOAT,CLOSE FLOAT,VOLUME FLOAT,DATE date,SYMBOL VARCHAR(10), PRIMARY KEY(DATE, SYMBOL));""")
        for r in data:
            open = r["1. open"]
            high = r["2. high"]
            low = r["3. low"]
            close = r["4. close"]
            volume = r["5. volume"]
            date = r["date"]
            symbol = "BRY"
            sql = f"INSERT INTO {target_table} (open, high, low, close, volume,date,symbol) VALUES ('{open}', '{high}', '{low}', '{close}', '{volume}','{date}','{symbol}')"
            cur.execute(sql)
        upsert_sql = f"""
            MERGE INTO {target_table} AS target
            USING {staging_table} AS stage
            ON target.DATE = stage.DATE
            WHEN MATCHED THEN
                UPDATE SET
                    target.open = stage.open,
                    target.high = stage.high,
                    target.low = stage.low,
                    target.close = stage.close,
                    target.volume = stage.volume,
                    target.date = stage.date,
                    target.symbol = stage.symbol
            WHEN NOT MATCHED THEN
                INSERT (open, high, low, close, volume,date,symbol)
                VALUES (stage.open, stage.high, stage.low, stage.close, stage.volume, stage.date, stage.symbol);
        """
        cur.execute(upsert_sql)
        cur.execute("COMMIT;")
    except Exception as e:
        cur.execute("ROLLBACK;")
        print(e)
        raise e


with DAG(
    dag_id = 'stock_api_chetana',
    start_date = datetime(2024,10,10),
    catchup=False,
    tags=['ETL'],
    schedule = '15 19 * * *'
) as dag:
    target_table = "dev.raw_data.BRY_DATA"
    vantage_api_key = Variable.get('vantage_api_key')
    symbol = "BRY"
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={vantage_api_key}"
    cur = return_snowflake_conn()

    data = extract(url)
    transformed_data = transform(data)
    load(cur, transformed_data, target_table)
