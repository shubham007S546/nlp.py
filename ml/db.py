import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Shubham@25",  # Replace with your actual password
        database="ams",         # Replace with your actual database name
        port=3306               # Your Workbench shows MySQL running on port 3306
    )
