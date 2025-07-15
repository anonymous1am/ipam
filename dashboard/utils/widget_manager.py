# utils/widget_manager.py - Widget Management System
import os
import importlib.util
import sys
import json
import traceback
from datetime import datetime, timedelta
import logging
from database.connection import get_db_connection
from config import Config

logger = logging.getLogger(__name__)

class WidgetManager:
    def __init__(self):
        self.widgets = {}
        
    def discover_widgets(self):
        """Discover and load widgets from the widgets folder"""
        widget_folder = Config.WIDGET_FOLDER
        
        if not os.path.exists(widget_folder):
            os.makedirs(widget_folder)
            logger.info(f"Created widgets folder: {widget_folder}")
            return
        
        for filename in os.listdir(widget_folder):
            if filename.endswith('.py') and not filename.startswith('__'):
                widget_name = filename[:-3]  # Remove .py extension
                self.load_widget(widget_name, os.path.join(widget_folder, filename))
        
        logger.info(f"Discovered {len(self.widgets)} widgets")
    
    def load_widget(self, widget_name, file_path):
        """Load a single widget from file"""
        try:
            spec = importlib.util.spec_from_file_location(widget_name, file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Check if module has required execute function
            if not hasattr(module, 'execute'):
                logger.error(f"Widget {widget_name} missing execute() function")
                return
            
            # Get widget configuration
            config = getattr(module, 'WIDGET_CONFIG', {})
            
            self.widgets[widget_name] = {
                'module': module,
                'config': config,
                'file_path': file_path
            }
            
            # Register widget metadata in database
            self.register_widget_metadata(widget_name, config)
            
            logger.info(f"Loaded widget: {widget_name}")
            
        except Exception as e:
            logger.error(f"Error loading widget {widget_name}: {str(e)}")
    
    def register_widget_metadata(self, widget_name, config):
        """Register widget metadata in database"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO widget_metadata (
                    widget_name, display_name, description, tab_group
                ) VALUES (%s, %s, %s, %s)
                ON CONFLICT (widget_name) DO UPDATE SET
                    display_name = EXCLUDED.display_name,
                    description = EXCLUDED.description,
                    tab_group = EXCLUDED.tab_group
            """, (
                widget_name,
                config.get('display_name', widget_name.replace('_', ' ').title()),
                config.get('description', ''),
                config.get('tab_group', 'Overview')
            ))
            
            conn.commit()
            cursor.close()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error registering widget metadata {widget_name}: {str(e)}")
    
    def execute_widget(self, widget_name, force=False):
        """Execute a specific widget"""
        if widget_name not in self.widgets:
            raise ValueError(f"Widget {widget_name} not found")
        
        try:
            # Check if execution is needed
            if not force and not self.should_execute_widget(widget_name):
                return self.get_widget_output(widget_name)
            
            # Execute widget
            module = self.widgets[widget_name]['module']
            result = module.execute()
            
            # Store result in database
            self.store_widget_output(widget_name, result)
            
            # Update execution timestamp
            self.update_execution_timestamp(widget_name)
            
            return self.get_widget_output(widget_name)
            
        except Exception as e:
            error_msg = f"Widget execution error: {str(e)}"
            logger.error(f"Error executing widget {widget_name}: {error_msg}")
            
            # Store error in database
            self.store_widget_error(widget_name, error_msg)
            
            return self.get_widget_output(widget_name)
    
    def should_execute_widget(self, widget_name):
        """Check if widget should be executed"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Check if output exists
            cursor.execute("""
                SELECT last_updated FROM widget_outputs 
                WHERE widget_name = %s
            """, (widget_name,))
            
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if not result:
                return True  # No output exists, should execute
            
            # Check if output is older than execution interval
            last_updated = result['last_updated']
            interval = timedelta(seconds=Config.WIDGET_EXECUTION_INTERVAL)
            
            return datetime.now() - last_updated > interval
            
        except Exception as e:
            logger.error(f"Error checking widget execution need {widget_name}: {str(e)}")
            return True  # On error, try to execute
    
    def store_widget_output(self, widget_name, output):
        """Store widget output in database"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO widget_outputs (
                    widget_name, output_data, status, error_message
                ) VALUES (%s, %s, %s, %s)
                ON CONFLICT (widget_name) DO UPDATE SET
                    output_data = EXCLUDED.output_data,
                    last_updated = CURRENT_TIMESTAMP,
                    status = EXCLUDED.status,
                    error_message = EXCLUDED.error_message
            """, (
                widget_name,
                json.dumps(output),
                'success',
                None
            ))
            
            conn.commit()
            cursor.close()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error storing widget output {widget_name}: {str(e)}")
    
    def store_widget_error(self, widget_name, error_message):
        """Store widget error in database"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO widget_outputs (
                    widget_name, output_data, status, error_message
                ) VALUES (%s, %s, %s, %s)
                ON CONFLICT (widget_name) DO UPDATE SET
                    last_updated = CURRENT_TIMESTAMP,
                    status = EXCLUDED.status,
                    error_message = EXCLUDED.error_message
            """, (
                widget_name,
                None,
                'error',
                error_message
            ))
            
            conn.commit()
            cursor.close()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error storing widget error {widget_name}: {str(e)}")
    
    def update_execution_timestamp(self, widget_name):
        """Update widget execution timestamp"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE widget_metadata 
                SET last_execution = CURRENT_TIMESTAMP 
                WHERE widget_name = %s
            """, (widget_name,))
            
            conn.commit()
            cursor.close()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error updating execution timestamp {widget_name}: {str(e)}")
    
    def get_widget_output(self, widget_name):
        """Get widget output from database"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT wo.*, wm.display_name, wm.description, wm.tab_group
                FROM widget_outputs wo
                LEFT JOIN widget_metadata wm ON wo.widget_name = wm.widget_name
                WHERE wo.widget_name = %s
            """, (widget_name,))
            
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if result:
                return dict(result)
            else:
                return {
                    'widget_name': widget_name,
                    'status': 'no_data',
                    'error_message': 'No output data available'
                }
                
        except Exception as e:
            logger.error(f"Error getting widget output {widget_name}: {str(e)}")
            return {
                'widget_name': widget_name,
                'status': 'error',
                'error_message': str(e)
            }
    
    def get_all_widgets(self):
        """Get all widget outputs"""
        widgets = []
        for widget_name in self.widgets.keys():
            widget_data = self.get_widget_output(widget_name)
            widgets.append(widget_data)
        return widgets
    
    def get_tabs(self):
        """Get available tabs and their widgets"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT tab_group, array_agg(widget_name ORDER BY widget_name) as widgets
                FROM widget_metadata
                WHERE is_active = true
                GROUP BY tab_group
                ORDER BY tab_group
            """)
            
            results = cursor.fetchall()
            cursor.close()
            conn.close()
            
            tabs = {}
            for result in results:
                tabs[result['tab_group']] = result['widgets']
            
            return tabs
            
        except Exception as e:
            logger.error(f"Error getting tabs: {str(e)}")
            return {'Overview': list(self.widgets.keys())}
    
    def check_and_execute_widgets(self):
        """Check all widgets and execute if needed"""
        for widget_name in self.widgets.keys():
            try:
                if self.should_execute_widget(widget_name):
                    self.execute_widget(widget_name)
                    logger.info(f"Executed widget: {widget_name}")
            except Exception as e:
                logger.error(f"Error in check_and_execute for {widget_name}: {str(e)}")


