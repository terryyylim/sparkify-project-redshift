from typing import Any

import configparser
import psycopg2
from sql_queries import copy_table_queries, insert_table_queries


def load_staging_tables(cur: Any, conn: Any) -> None:
    """
    Load data from S3 bucket into Redshift tables
    """
    for query in copy_table_queries:
        cur.execute(query)
        conn.commit()


def insert_tables(cur: Any, conn: Any) -> None:
    """
    Insert data from staging tables to dimension and fact tables
    """
    for query in insert_table_queries:
        cur.execute(query)
        conn.commit()


def main() -> None:
    config = configparser.ConfigParser()
    config.read('dwh.cfg')

    conn = psycopg2.connect("host={} dbname={} user={} password={} port={}".format(*config['CLUSTER'].values()))
    cur = conn.cursor()

    load_staging_tables(cur, conn)
    insert_tables(cur, conn)

    conn.close()


if __name__ == "__main__":
    main()
