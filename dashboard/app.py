# app.py - Main Flask Application
from flask import Flask, render_template, jsonify
from datetime import datetime, timedelta
import os
import importlib.util
import sys
import json
import traceback
from threading import Timer
import psycopg2
from psycopg2.extras import RealDictCursor
import logging

app = Flask(__name__)

# Import configuration
from config import Config
app.config.from_object(Config)

# Import database utilities
from database.connection import get_db_connection, init_database
from utils.widget_manager import WidgetManager

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize widget manager
widget_manager = WidgetManager()

@app.route('/')
def dashboard():
    """Main dashboard route"""
    return render_template('dashboard.html')

@app.route('/api/widgets')
def get_widgets():
    """API endpoint to get all widget data"""
    try:
        widgets = widget_manager.get_all_widgets()
        return jsonify({
            'status': 'success',
            'widgets': widgets,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error getting widgets: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/widgets/<widget_name>/refresh')
def refresh_widget(widget_name):
    """Force refresh a specific widget"""
    try:
        result = widget_manager.execute_widget(widget_name, force=True)
        return jsonify({
            'status': 'success',
            'widget': result
        })
    except Exception as e:
        logger.error(f"Error refreshing widget {widget_name}: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/tabs')
def get_tabs():
    """Get available tabs and their widgets"""
    try:
        tabs = widget_manager.get_tabs()
        return jsonify({
            'status': 'success',
            'tabs': tabs
        })
    except Exception as e:
        logger.error(f"Error getting tabs: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

def scheduled_widget_check():
    """Background task to check and execute widgets as needed"""
    try:
        widget_manager.check_and_execute_widgets()
        logger.info("Scheduled widget check completed")
    except Exception as e:
        logger.error(f"Error in scheduled widget check: {str(e)}")
    
    # Schedule next check in 60 seconds
    Timer(60.0, scheduled_widget_check).start()

if __name__ == '__main__':
    # Initialize database on startup
    init_database()
    
    # Discover and register widgets
    widget_manager.discover_widgets()
    
    # Start background scheduler
    Timer(60.0, scheduled_widget_check).start()
    
    app.run(debug=True, host='0.0.0.0', port=5000)
