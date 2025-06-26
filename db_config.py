# Ye file Flask app ke configs handle karti hai. Database ke credentials yahi rakhte hain.
# import mysql.connector

# def get_db_connection():
#     return mysql.connector.connect(
#         host="localhost",
#         port=3306,
#         user="root",
#         password="1234",  # Apna password 
#         database="quiz_app_db"           # DB banaya h uska naam
#     )

import os
import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host=os.environ['DB_HOST'],
        user=os.environ['DB_USER'],
        password=os.environ['DB_PASSWORD'],
        database=os.environ['DB_NAME'],
        port=int(os.environ.get('DB_PORT', 3306))
    )
