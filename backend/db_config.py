# db_config.py
# Simple MySQL connector helper using mysql-connector-python

import mysql.connector
from mysql.connector import errorcode

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "root-password",  # <-- change if needed
    "database": "tanglaw_db"
}

def get_db_connection():
    """
    Returns a new MySQL connection.
    Caller is responsible for closing connection.
    """
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG["host"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["database"],
            autocommit=False  # control commits explicitly
        )
        return conn
    except mysql.connector.Error as err:
        # helpful errors for local debugging
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            raise Exception("DB access denied — check username/password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            raise Exception("Database does not exist — run SQL script first")
        else:
            raise
