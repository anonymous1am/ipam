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

## Installation & Deployment

### Step 1: Clone Repository
```bash
git clone https://github.com/anonymous1am/ipam.git
cd dashboard
```

### Step 2: Run Initial Setup
```bash
bash setup.sh
```

### Step 3: Configure Required Settings

#### A. Update GitHub Repository URL
Edit `setup.sh` and replace:
```bash
git clone https://github.com/anonymous1am/ipam.git .
```
With your actual GitHub repository URL.

#### B. Configure Database Credentials
Edit `config.py` and update:
```python
DATABASE_URL = 'postgresql://dashboarduser:your_secure_password@localhost:5432/dashboard'
```

**Or create a `.env` file:**
```bash
cp .env.example .env
```
Then edit `.env` with your settings:
```
DATABASE_URL=postgresql://dashboarduser:YOUR_SECURE_PASSWORD@localhost:5432/dashboard
SECRET_KEY=your-very-secure-secret-key-change-this-to-something-random
DEBUG=false
LOG_LEVEL=INFO
```

#### C. Update Database Password in Setup Script
Edit `setup.sh` and change:
```bash
sudo -u postgres psql -c "ALTER USER dashboarduser PASSWORD 'your_secure_password';"
```
Replace `your_secure_password` with your chosen database password.

#### D. Configure Backup Script
Edit `backup.sh` and update database connection:
```bash
pg_dump -h localhost -U dashboarduser dashboard > /opt/dashboard/backups/dashboard_backup_$TIMESTAMP.sql
```
You may need to configure PostgreSQL authentication (`.pgpass` file) for automated backups.

### Step 4: Network & Access Configuration

#### A. Firewall Configuration
```bash
# Allow HTTP traffic
sudo ufw allow 5000/tcp

# Or if using Nginx proxy
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

#### B. Configure Nginx Proxy (Optional but Recommended)
Edit `nginx.conf` and replace:
```
server_name your-domain.com;
```
With your actual domain or server IP address.

Then enable the configuration:
```bash
sudo cp nginx.conf /etc/nginx/sites-available/dashboard
sudo ln -s /etc/nginx/sites-available/dashboard /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Step 5: GitHub Actions Setup (Optional)
If using automated deployment, configure GitHub secrets:

1. Go to your GitHub repository → Settings → Secrets and variables → Actions
2. Add these secrets:
   - `HOST`: Your server IP address
   - `USERNAME`: Your server username
   - `SSH_KEY`: Your private SSH key for server access

### Step 6: SSL/HTTPS Setup (Production Recommended)
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate (replace with your domain)
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## Configuration Reference

### Required Changes Summary
| File | Setting | Change Required |
|------|---------|----------------|
| `setup.sh` | GitHub URL | Replace with your repository |
| `setup.sh` | Database Password | Set secure password |
| `config.py` | DATABASE_URL | Update with your password |
| `config.py` | SECRET_KEY | Generate secure random key |
| `nginx.conf` | server_name | Your domain/IP address |
| GitHub Secrets | HOST, USERNAME, SSH_KEY | For automated deployment |

### Environment Variables
Create `.env` file with:
```bash
# Database Configuration
DATABASE_URL=postgresql://dashboarduser:YOUR_PASSWORD@localhost:5432/dashboard

# Flask Configuration  
SECRET_KEY=generate-a-secure-random-key-here
DEBUG=false

# Widget Configuration
WIDGET_EXECUTION_INTERVAL=86400  # 24 hours
WIDGET_CHECK_INTERVAL=60        # 1 minute
WIDGET_TIMEOUT=300              # 5 minutes

# Logging
LOG_LEVEL=INFO
```

### PostgreSQL Configuration
If you need custom PostgreSQL settings, edit `/etc/postgresql/*/main/postgresql.conf`:
```
# Adjust these based on your server resources
max_connections = 100
shared_buffers = 128MB
effective_cache_size = 1GB
```

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

### Database Access in Widgets
```python
from database.connection import get_db_connection

def execute():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM your_table")
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    
    return {
        "title": "Database Widget",
        "data": {"count": result[0]},
        "status": "success"
    }
```

## Deployment & Updates

### Manual Deployment
```bash
cd /opt/dashboard
bash deploy.sh
```

### Automatic Deployment Options

#### 1. GitHub Actions (Recommended)
Already configured in `.github/workflows/deploy.yml` - just push to main branch.

#### 2. Cron Job
```bash
# Add to crontab for daily updates at 2 AM
crontab -e
# Add: 0 2 * * * cd /opt/dashboard && bash deploy.sh >> /var/log/dashboard-deploy.log 2>&1
```

#### 3. Webhook (Advanced)
Set up a webhook endpoint to trigger deployments on GitHub push events.

## Management Commands

### Service Management
```bash
# Check status
sudo systemctl status dashboard

# Start/Stop/Restart
sudo systemctl start dashboard
sudo systemctl stop dashboard
sudo systemctl restart dashboard

# Enable/Disable auto-start
sudo systemctl enable dashboard
sudo systemctl disable dashboard
```

### Logs & Monitoring
```bash
# View real-time logs
sudo journalctl -u dashboard -f

# View recent logs
sudo journalctl -u dashboard --since "1 hour ago"

# View error logs only
sudo journalctl -u dashboard -p err

# Application logs location
tail -f /var/log/dashboard.log  # If configured in config.py
```

### Database Management
```bash
# Backup database
bash backup.sh

# Restore database
sudo -u postgres psql dashboard < backup_file.sql

# Connect to database
sudo -u postgres psql dashboard

# Monitor database performance
sudo -u postgres psql -c "SELECT * FROM pg_stat_activity;"
```

### Widget Management
```bash
# List discovered widgets
ls -la widgets/

# Test widget execution
cd /opt/dashboard
source venv/bin/activate
python3 -c "
from utils.widget_manager import WidgetManager
wm = WidgetManager()
wm.discover_widgets()
print(wm.execute_widget('your_widget_name'))
"

# Force refresh all widgets
curl http://localhost:5000/api/widgets
```

## Troubleshooting

### Common Issues

#### Service Won't Start
```bash
# Check service logs
sudo journalctl -u dashboard -n 50

# Check if port is in use
sudo netstat -tlnp | grep :5000

# Check file permissions
ls -la /opt/dashboard/
```

#### Database Connection Issues
```bash
# Test PostgreSQL connection
sudo -u postgres psql -c "SELECT version();"

# Check if database exists
sudo -u postgres psql -l | grep dashboard

# Test application database connection
cd /opt/dashboard && python3 -c "from database.connection import get_db_connection; print(get_db_connection())"
```

#### Widget Errors
```bash
# Check widget syntax
python3 -m py_compile widgets/your_widget.py

# Test widget execution manually
cd /opt/dashboard
python3 -c "
import sys
sys.path.append('widgets')
import your_widget
print(your_widget.execute())
"
```

#### Permission Issues
```bash
# Fix ownership
sudo chown -R $USER:$USER /opt/dashboard

# Fix permissions
chmod +x setup.sh deploy.sh backup.sh
```

### Performance Optimization

#### For High-Traffic Environments
1. Use Nginx proxy (already configured)
2. Enable PostgreSQL connection pooling
3. Increase widget execution timeout if needed
4. Consider Redis for widget result caching

#### Resource Monitoring
```bash
# Monitor system resources
htop
df -h
free -h

# Monitor database performance
sudo -u postgres psql dashboard -c "
SELECT query, state, query_start 
FROM pg_stat_activity 
WHERE state != 'idle';
"
```

## Security Considerations

### Required Security Updates
1. **Change default passwords** in all configuration files
2. **Generate secure SECRET_KEY** for Flask sessions
3. **Configure firewall** to restrict access to necessary ports only
4. **Enable SSL/HTTPS** for production deployments
5. **Regular security updates**: `sudo apt update && sudo apt upgrade`
6. **Database access**: Restrict PostgreSQL to localhost only
7. **File permissions**: Ensure sensitive files are not world-readable

### Recommended Security Measures
```bash
# Restrict database configuration file
chmod 600 config.py

# Create dedicated user for dashboard
sudo useradd -r -s /bin/false dashboard
sudo chown -R dashboard:dashboard /opt/dashboard

# Configure fail2ban for SSH protection
sudo apt install fail2ban
```

## Support & Contributing

### Getting Help
1. Check the logs: `sudo journalctl -u dashboard -f`
2. Test widget execution manually
3. Verify database connectivity
4. Check file permissions and ownership

### Contributing
1. Fork the repository
2. Create a feature branch
3. Test your changes thoroughly
4. Submit a pull request
