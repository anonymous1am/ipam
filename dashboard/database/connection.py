# database/connection.py - Database Connection Management
import psycopg2
from psycopg2.extras import RealDictCursor
import logging
from config import Config

logger = logging.getLogger(__name__)

def get_db_connection():
    """Get database connection"""
    try:
        conn = psycopg2.connect(
            Config.DATABASE_URL,
            cursor_factory=RealDictCursor
        )
        return conn
    except Exception as e:
        logger.error(f"Database connection error: {str(e)}")
        raise

def init_database():
    """Initialize database tables"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create widget_outputs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS widget_outputs (
                id SERIAL PRIMARY KEY,
                widget_name VARCHAR(255) UNIQUE NOT NULL,
                output_data JSONB,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status VARCHAR(50) DEFAULT 'success',
                error_message TEXT
            )
        """)
        
        # Create widget_metadata table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS widget_metadata (
                widget_name VARCHAR(255) PRIMARY KEY,
                display_name VARCHAR(255),
                description TEXT,
                tab_group VARCHAR(100) DEFAULT 'Overview',
                execution_interval INTEGER DEFAULT 86400,
                last_execution TIMESTAMP,
                is_active BOOLEAN DEFAULT true
            )
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info("Database initialized successfully")
        
    except Exception as e:
        logger.error(f"Database initialization error: {str(e)}")
        raise
