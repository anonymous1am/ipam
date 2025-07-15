# setup.sh - Initial setup script for Ubuntu server
#!/bin/bash

echo "Setting up Dashboard Application..."

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3 and pip
sudo apt install -y python3 python3-pip python3-venv

# Install PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# Install Git
sudo apt install -y git

# Install Nginx (optional, for production deployment)
sudo apt install -y nginx

# Create application directory
sudo mkdir -p /opt/dashboard
sudo chown $USER:$USER /opt/dashboard

# Clone repository (replace with your GitHub repo URL)
cd /opt/dashboard
git clone https://github.com/yourusername/dashboard.git .

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
pip install psutil  # Additional dependency for system monitoring

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
ExecStart=/opt/dashboard/venv/bin/python app.py
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

