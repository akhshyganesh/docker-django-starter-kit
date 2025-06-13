#!/usr/bin/env python3
"""
Production database wait script with enhanced error handling
"""
import os
import sys
import time
import logging
import psycopg2
from psycopg2 import OperationalError
from decouple import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def wait_for_db():
    """
    Wait for PostgreSQL database to become available
    """
    # Database configuration
    db_config = {
        'host': config('POSTGRES_HOST', default='db'),
        'port': config('POSTGRES_PORT', default=5432, cast=int),
        'user': config('POSTGRES_USER', default='postgres'),
        'password': config('POSTGRES_PASSWORD', default='postgres'),
        'database': config('POSTGRES_DB', default='saas_app'),
    }
    
    max_attempts = 30
    attempt = 0
    
    logger.info("Waiting for PostgreSQL database to become available...")
    logger.info(f"Database: {db_config['user']}@{db_config['host']}:{db_config['port']}/{db_config['database']}")
    
    while attempt < max_attempts:
        try:
            # Attempt to connect to PostgreSQL
            conn = psycopg2.connect(**db_config)
            conn.close()
            logger.info("PostgreSQL is available!")
            return True
            
        except OperationalError as e:
            attempt += 1
            logger.warning(f"Attempt {attempt}/{max_attempts} - PostgreSQL not available: {e}")
            
            if attempt >= max_attempts:
                logger.error("PostgreSQL did not become available within the expected time")
                return False
                
            time.sleep(2)
    
    return False

def wait_for_redis():
    """
    Wait for Redis to become available
    """
    try:
        import redis
        
        redis_url = config('REDIS_URL', default='redis://localhost:6379/0')
        logger.info(f"Waiting for Redis at {redis_url}...")
        
        max_attempts = 15
        attempt = 0
        
        while attempt < max_attempts:
            try:
                r = redis.from_url(redis_url)
                r.ping()
                logger.info("Redis is available!")
                return True
                
            except (redis.ConnectionError, redis.TimeoutError) as e:
                attempt += 1
                logger.warning(f"Attempt {attempt}/{max_attempts} - Redis not available: {e}")
                
                if attempt >= max_attempts:
                    logger.error("Redis did not become available within the expected time")
                    return False
                    
                time.sleep(2)
        
        return False
        
    except ImportError:
        logger.warning("Redis module not available, skipping Redis check")
        return True

def main():
    """
    Main function to wait for all required services
    """
    logger.info("Starting service availability checks...")
    
    # Check database
    if not wait_for_db():
        logger.error("Database check failed")
        sys.exit(1)
    
    # Check Redis
    if not wait_for_redis():
        logger.error("Redis check failed")
        sys.exit(1)
    
    logger.info("All services are available!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
