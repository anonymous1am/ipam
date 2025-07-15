# ipam
IPAM and widget Web Application for Internal Lab Environment

Created By: Brett Davis
This Web application was created for internal use and does not include authentication in version .01

This was created to run on Ubuntu 24.04 LTS

Requirements.txt will reflect the requirements for Ubuntu 24.04

If using this for another operating system, the requirements and code will change based on which repositories are available for that operating system.


Uncomment the code after including it in the .py file for the widget.



# README.md content for the repository
# Dashboard Application

A modular Flask dashboard system that automatically discovers and executes Python widgets.

## Features

- **Auto-discovery**: Automatically finds and loads Python widgets from the `widgets/` folder
- **Caching**: Widgets run once every 24 hours, with 1-minute frontend refresh
- **Professional UI**: Clean, responsive design with teal color scheme
- **PostgreSQL Integration**: Shared database connection for all widgets
- **Error Handling**: Displays widget errors with detailed messages
- **Tab Organization**: Widgets can be organized into tabs
- **Real-time Updates**: Automatic refresh and manual refresh options

## Quick Start

1. Clone the repository
2. Run `bash setup.sh` on your Ubuntu server
3. Update database credentials in `config.py`
4. Add your Python widgets to the `widgets/` folder
5. Access the dashboard at `http://your-server:5000`

## Widget Development

Create a Python file in the `widgets/` folder with this structure:

```python
def execute():
    return {
        "title": "My Widget",
        "data": {"key": "value"},
        "status": "success"
    }

WIDGET_CONFIG = {
    "display_name": "My Widget",
    "description": "Widget description",
    "tab_group": "Overview"
}
```

## Deployment

- **Manual**: Run `bash deploy.sh` to pull updates from GitHub
- **Automatic**: Use GitHub Actions or cron jobs for scheduled deployments
- **Docker**: Use the provided docker-compose.yml for containerized deployment

## Management

- Service: `sudo systemctl {start|stop|restart|status} dashboard`
- Logs: `sudo journalctl -u dashboard -f`
- Backup: `bash backup.sh`
