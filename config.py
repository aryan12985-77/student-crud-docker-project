import mysql.connector

# Database connection function
def get_db_connection():
    conn = mysql.connector.connect(
        host="mysql",          # Docker service name (important later)
        user="root",
        password="root",
        database="student_db"
    )
    return conn