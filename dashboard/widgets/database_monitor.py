# widgets/database_monitor.py
from database.connection import get_db_connection
from datetime import datetime

def execute():
    """Database monitoring widget"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get database stats
        cursor.execute("SELECT version()")
        db_version = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT 
                count(*) as total_connections,
                count(*) FILTER (WHERE state = 'active') as active_connections
            FROM pg_stat_activity
        """)
        connection_stats = cursor.fetchone()
        
        cursor.execute("""
            SELECT 
                pg_size_pretty(pg_database_size(current_database())) as db_size
        """)
        db_size = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        return {
            "title": "Database Monitor",
            "data": {
                "version": db_version.split(' ')[1],
                "total_connections": connection_stats['total_connections'],
                "active_connections": connection_stats['active_connections'],
                "database_size": db_size,
                "status": "online"
            },
            "status": "success",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise Exception(f"Failed to monitor database: {str(e)}")

WIDGET_CONFIG = {
    "display_name": "Database Monitor", 
    "description": "PostgreSQL database performance and connection metrics",
    "tab_group": "Database"
}


# widgets/widget_status.py
from database.connection import get_db_connection
from datetime import datetime

def execute():
    """Widget status monitoring"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                widget_name,
                status,
                last_updated,
                error_message
            FROM widget_outputs
            ORDER BY last_updated DESC
        """)
        
        widgets = cursor.fetchall()
        cursor.close()
        conn.close()
        
        total_widgets = len(widgets)
        success_count = sum(1 for w in widgets if w['status'] == 'success')
        error_count = sum(1 for w in widgets if w['status'] == 'error')
        
        return {
            "title": "Widget Status",
            "data": {
                "total_widgets": total_widgets,
                "successful": success_count,
                "errors": error_count,
                "success_rate": f"{(success_count/total_widgets*100):.1f}%" if total_widgets > 0 else "0%",
                "widgets": [dict(w) for w in widgets]
            },
            "status": "success",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise Exception(f"Failed to get widget status: {str(e)}")

WIDGET_CONFIG = {
    "display_name": "Widget Status",
    "description": "Status and health of all dashboard widgets", 
    "tab_group": "System"
}
