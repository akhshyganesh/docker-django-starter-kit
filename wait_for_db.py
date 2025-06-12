import os
import time
import psycopg2
from psycopg2 import OperationalError

def wait_for_db():
    """Wait for database to become available"""
    db_conn = None
    retries = 30
    
    while retries > 0:
        try:
            db_conn = psycopg2.connect(
                host=os.environ.get('DB_HOST', 'db'),
                port=os.environ.get('DB_PORT', '5432'),
                user=os.environ.get('POSTGRES_USER', 'postgres'),
                password=os.environ.get('POSTGRES_PASSWORD', 'postgres'),
                database=os.environ.get('POSTGRES_DB', 'saas_app')
            )
            print("Database is ready!")
            break
        except OperationalError:
            print(f"Database unavailable, waiting... ({retries} retries left)")
            retries -= 1
            time.sleep(1)
    
    if db_conn:
        db_conn.close()
    
    if retries == 0:
        print("Could not connect to database!")
        exit(1)

if __name__ == "__main__":
    wait_for_db()
