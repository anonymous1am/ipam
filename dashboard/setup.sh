# setup.sh - Initial setup script for Ubuntu server
#!/bin/bash

echo "Setting up Dashboard Application..."

# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies from requirements.txt
if [ -f "requirements.txt" ]; then
    echo "Installing APT packages from requirements.txt..."
    while IFS= read -r package; do
        if [[ ! "$package" =~ ^#.*$ ]] && [[ -n "$package" ]]; then
            echo "Installing: $package"
            sudo apt install -y "$package"
        fi
    done < requirements.txt
else
    # Fallback to manual installation if requirements.txt not found
    sudo apt install -y python3 python3-pip python3-venv python3-flask python3-psycopg2 python3-dotenv python3-psutil python3-gunicorn postgresql postgresql-contrib git nginx
fi

# Create application directory
sudo mkdir -p /opt/dashboard
sudo chown $USER:$USER /opt/dashboard

# Clone repository (replace with your GitHub repo URL)
cd /opt/dashboard
git clone https://github.com/yourusername/dashboard.git .

# Create virtual environment (for any additional pip packages)
python3 -m venv venv
source venv/bin/activate

# Install any additional Python packages not available via APT
if [ -f "pip-requirements.txt" ]; then
    pip install -r pip-requirements.txt
fi

# Setup PostgreSQL database
sudo -u postgres createdb dashboard
sudo -u postgres createuser dashboarduser
sudo -u postgres psql -c "ALTER USER dashboarduser PASSWORD 'your_secure_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE dashboard TO dashboarduser;"

# Create systemd service file
sudo tee /etc/systemd/system/dashboard.service > /dev/null <<EOF
[Unit]
Description=Dashboard Flask Application
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/opt/dashboard
Environment=PATH=/opt/dashboard/venv/bin
ExecStart=/usr/bin/python3 app.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable dashboard
sudo systemctl start dashboard

echo "Dashboard setup complete!"
echo "Update the database configuration in config.py with your database credentials"
echo "Access the dashboard at http://your-server-ip:5000"
