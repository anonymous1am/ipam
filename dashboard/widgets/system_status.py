# widgets/system_status.py
import psutil
import platform
from datetime import datetime

def execute():
    """System status widget"""
    try:
        # Get system information
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            "title": "System Status",
            "data": {
                "cpu_usage": f"{cpu_percent}%",
                "memory_usage": f"{memory.percent}%",
                "memory_available": f"{memory.available / (1024**3):.1f} GB",
                "disk_usage": f"{disk.percent}%",
                "disk_free": f"{disk.free / (1024**3):.1f} GB",
                "platform": platform.system(),
                "hostname": platform.node(),
                "uptime": str(datetime.now() - datetime.fromtimestamp(psutil.boot_time())).split('.')[0]
            },
            "status": "success",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise Exception(f"Failed to get system status: {str(e)}")

WIDGET_CONFIG = {
    "display_name": "System Status",
    "description": "Real-time system health and performance metrics",
    "tab_group": "Overview"
}
