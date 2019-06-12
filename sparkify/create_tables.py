from typing import Any

import configparser
import psycopg2
from sql_queries import create_table_queries, drop_table_queries


def drop_tables(cur: Any, conn: Any) -> None:
    """
    Run queries found in drop_table_queries function from create_tables.py.
    """
    for query in drop_table_queries:
        cur.execute(query)
        conn.commit()


def create_tables(cur: Any, conn: Any) -> None:
    """
    Run queries found in create_table_queries function from create_tables.py.
    """
    for query in create_table_queries:
        cur.execute(query)
        conn.commit()


def main() -> None:
    config = configparser.ConfigParser()
    config.read('dwh.cfg')

    conn = psycopg2.connect("host={} dbname={} user={} password={} port={}".format(*config['CLUSTER'].values()))
    cur = conn.cursor()

    drop_tables(cur, conn)
    create_tables(cur, conn)

    conn.close()


if __name__ == "__main__":
    main()
