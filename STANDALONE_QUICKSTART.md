# Standalone Quickstart Guide

## TL;DR - Deploy on Any Machine (No Cloud)

```bash
# 1. Install dependencies
pip install -r requirements-standalone.txt

# 2. Initialize database
python3 -c "from t2t_store import init_db; init_db('t2t.db')"

# 3. Create admin
python3 create_admin_standalone.py admin@example.com --name "Admin"
# SAVE THE PASSWORD SHOWN!

# 4. Start
./start_all.sh

# 5. Access
# http://localhost:8050 - Annotation
# http://localhost:8051 - Admin (login with password from step 3)
```

## What You Get

✅ Full admin authentication (bcrypt passwords)
✅ Project management
✅ Batch PDF fetching
✅ All features from Supabase version
✅ **NO cloud dependencies**
✅ **NO internet required** (except for PDF fetching)
✅ **Single SQLite database file**

## Files for Standalone Mode

| File | Purpose |
|------|---------|
| `requirements-standalone.txt` | Dependencies (no Supabase) |
| `create_admin_standalone.py` | Create admin accounts |
| `t2t_admin_be_standalone.py` | Admin backend (SQLite) |
| `t2t_store.py` | Database functions (updated with admin tables) |

## Differences from Supabase Version

| What | Supabase Version | Standalone Version |
|------|------------------|-------------------|
| Database | PostgreSQL (cloud) | SQLite (local file) |
| Setup | Need Supabase account | Just Python |
| Internet | Required for database | Only for PDF APIs |
| Backup | Supabase handles it | You handle it |
| Scaling | Automatic | Manual |
| Cost | Supabase fees | Free |
| Privacy | Data in cloud | Data on your machine |

## Remote Deployment

### Copy to Server

```bash
# From your local machine
scp -r t2t_training_dev/ user@server:/home/user/

# SSH to server
ssh user@server
cd t2t_training_dev
```

### Install on Server

```bash
# Install system deps
sudo apt-get install -y python3 python3-pip python3-venv build-essential

# Create venv (recommended)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements-standalone.txt

# Initialize
python3 -c "from t2t_store import init_db; init_db('t2t.db')"

# Create admin
python3 create_admin_standalone.py admin@example.com --name "Admin"

# Configure .env for remote access
cat > .env << 'EOF'
T2T_DB=t2t.db
T2T_BACKEND_PORT=5001
T2T_ADMIN_PORT=5002
T2T_FRONTEND_PORT=8050
T2T_ADMIN_FRONTEND_PORT=8051
T2T_HOST=0.0.0.0
T2T_PDF_STORAGE=pdfs
EOF

# Start services
./start_all.sh

# Allow firewall
sudo ufw allow 8050/tcp
sudo ufw allow 8051/tcp
```

### Access from Your Computer

```
http://server-ip:8050  # Annotation
http://server-ip:8051  # Admin panel
```

## Common Tasks

### Create Admin Account

```bash
python3 create_admin_standalone.py email@example.com --name "Name"
```

### Reset Admin Password

```bash
python3 create_admin_standalone.py email@example.com --reset
```

### Backup Database

```bash
# Simple backup
cp t2t.db backup/t2t_$(date +%Y%m%d).db

# With PDFs
tar -czf backup_$(date +%Y%m%d).tar.gz t2t.db pdfs/
```

### Check What's in Database

```bash
sqlite3 t2t.db "
SELECT
  'Annotations: ' || COUNT(*) FROM tuples
UNION ALL
SELECT 'Projects: ' || COUNT(*) FROM projects
UNION ALL
SELECT 'Papers: ' || COUNT(*) FROM project_papers
UNION ALL
SELECT 'Admins: ' || COUNT(*) FROM admin_users;
"
```

## Troubleshooting

### "No module named bcrypt"

```bash
pip install bcrypt

# If that fails:
sudo apt-get install -y build-essential python3-dev
pip install bcrypt
```

### "Port already in use"

```bash
# Kill existing processes
pkill -f "python3.*t2t"

# Start again
./start_all.sh
```

### "Database is locked"

```bash
# Kill all python processes
pkill -9 python3

# Restart
./start_all.sh
```

### Can't Access from Remote Machine

```bash
# Check if bound to 0.0.0.0
netstat -tulpn | grep 8050

# Check firewall
sudo ufw status

# Allow ports
sudo ufw allow 8050/tcp
sudo ufw allow 8051/tcp
```

## Production Tips

### Run as SystemD Service

```bash
sudo nano /etc/systemd/system/t2t.service
```

```ini
[Unit]
Description=Text2Trait
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/home/your-user/t2t_training_dev
Environment="PATH=/home/your-user/t2t_training_dev/venv/bin"
ExecStart=/home/your-user/t2t_training_dev/start_all.sh
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable t2t
sudo systemctl start t2t
```

### Automated Backups

```bash
# Add to crontab
crontab -e
```

```
# Backup daily at 2 AM
0 2 * * * cp /home/user/t2t_training_dev/t2t.db /home/user/backups/t2t_$(date +\%Y\%m\%d).db
```

### Use Nginx for SSL

```bash
sudo apt-get install -y nginx certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## Security Checklist

- [ ] Strong admin passwords (auto-generated)
- [ ] Password files deleted after saving (`rm .admin_password_*.txt`)
- [ ] Database file secured (`chmod 600 t2t.db`)
- [ ] .env file secured (`chmod 600 .env`)
- [ ] Firewall configured (`ufw enable`)
- [ ] SSL/HTTPS enabled (if public)
- [ ] Regular backups configured

## When to Use Standalone

✅ **Use standalone if:**
- Deploying on your own server
- Privacy/security requirements (data stays on-premise)
- No internet connectivity
- Want full control
- Research/academic use
- Low to medium traffic

❌ **Use Supabase if:**
- Need global availability
- High concurrency
- Managed backups preferred
- Rapid scaling needed
- Don't want to manage servers

## Complete Example: Deploy to Ubuntu Server

```bash
# On your server
ssh user@server

# Install system packages
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv build-essential git

# Clone/copy project
git clone your-repo t2t_training_dev
cd t2t_training_dev

# Set up Python
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-standalone.txt

# Initialize
python3 -c "from t2t_store import init_db; init_db('t2t.db')"

# Create admin
python3 create_admin_standalone.py admin@example.com --name "Admin"
# SAVE THE PASSWORD!

# Configure for remote access
echo "T2T_HOST=0.0.0.0" >> .env

# Start
./start_all.sh &

# Allow firewall
sudo ufw allow 8050/tcp
sudo ufw allow 8051/tcp

# Done! Access at http://server-ip:8050
```

## Summary

The standalone version gives you:
- ✅ **Independence** - No cloud accounts needed
- ✅ **Privacy** - All data on your machine
- ✅ **Simplicity** - One SQLite file
- ✅ **Portability** - Easy to backup and move
- ✅ **Cost** - Free (no cloud bills)
- ✅ **Features** - Full parity with Supabase version

Perfect for:
- University research projects
- On-premise corporate deployment
- Privacy-sensitive applications
- Development and testing
- Offline environments

See [STANDALONE_DEPLOYMENT.md](STANDALONE_DEPLOYMENT.md) for full deployment guide with Nginx, SSL, systemd, monitoring, and more.
