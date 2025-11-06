import mysql.connector

def get_db_connection():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",         # change if you use another username
        password="root-password",         # change if your MySQL has a password
        database="tanglaw_db"
    )
    return conn
