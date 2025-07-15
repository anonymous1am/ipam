# deploy.sh - Deployment script for updates
#!/bin/bash

echo "Deploying Dashboard updates..."

# Navigate to application directory
cd /opt/dashboard

# Stop the service
sudo systemctl stop dashboard

# Pull latest changes from GitHub
git pull origin main

# Activate virtual environment
source venv/bin/activate

# Install/update dependencies
pip install -r requirements.txt

# Run any database migrations if needed
python -c "from database.connection import init_database; init_database()"

# Restart the service
sudo systemctl start dashboard
sudo systemctl status dashboard

echo "Deployment complete!"


# .env.example - Environment variables template
# Copy this file to .env and update with your values

# Database Configuration
DATABASE_URL=postgresql://dashboarduser:your_secure_password@localhost:5432/dashboard

# Widget Configuration
WIDGET_EXECUTION_INTERVAL=86400  # 24 hours in seconds
WIDGET_CHECK_INTERVAL=60        # 1 minute in seconds
WIDGET_TIMEOUT=300              # 5 minutes in seconds

# Flask Configuration
SECRET_KEY=your-very-secure-secret-key-change-this
DEBUG=false

# Logging Configuration
LOG_LEVEL=INFO


# requirements.txt - Python dependencies
Flask==2.3.3
psycopg2-binary==2.9.7
python-dotenv==1.0.0
psutil==5.9.5
gunicorn==21.2.0


# nginx.conf - Nginx configuration for production (optional)
server {
    listen 80;
    server_name your-domain.com;  # Replace with your domain or IP

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Static files (optional optimization)
    location /static {
        alias /opt/dashboard/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}

