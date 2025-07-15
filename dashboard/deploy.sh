# deploy.sh - Deployment script for updates
#!/bin/bash

echo "Deploying Dashboard updates..."

# Navigate to application directory
cd /opt/dashboard

# Stop the service
sudo systemctl stop dashboard

# Pull latest changes from GitHub
git pull origin main

# Update system packages
sudo apt update

# Install/update APT dependencies from requirements.txt
if [ -f "requirements.txt" ]; then
    echo "Installing APT packages from requirements.txt..."
    while IFS= read -r package; do
        if [[ ! "$package" =~ ^#.*$ ]] && [[ -n "$package" ]]; then
            echo "Installing: $package"
            sudo apt install -y "$package"
        fi
    done < requirements.txt
fi

# Install additional Python packages that aren't available via APT
if [ -f "pip-requirements.txt" ]; then
    echo "Installing additional Python packages..."
    source venv/bin/activate
    pip install -r pip-requirements.txt
fi

# Run any database migrations if needed
source venv/bin/activate
python3 -c "from database.connection import init_database; init_database()" 2>/dev/null || echo "Database initialization skipped (may already be initialized)"

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
