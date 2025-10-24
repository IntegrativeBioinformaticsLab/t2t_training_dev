# Standalone Deployment Guide (No Cloud Dependencies)

Deploy Text2Trait on any independent machine using only SQLite - no Supabase or cloud services required.

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements-standalone.txt

# 2. Initialize database
python3 -c "from t2t_store import init_db; init_db('t2t.db')"

# 3. Create admin account
python3 create_admin_standalone.py admin@example.com --name "Admin"

# 4. Start services
./start_all.sh
```

Access at:
- http://localhost:8050 (Annotation)
- http://localhost:8051 (Admin Panel)

## Key Differences from Supabase Version

| Feature | Supabase Version | Standalone Version |
|---------|-----------------|-------------------|
| **Database** | Supabase (PostgreSQL) | SQLite |
| **Authentication** | Supabase Auth | bcrypt + SQLite sessions |
| **Admin Script** | `create_admin.py` | `create_admin_standalone.py` |
| **Admin Backend** | `t2t_admin_be.py` | `t2t_admin_be_standalone.py` |
| **Dependencies** | requirements.txt | requirements-standalone.txt |
| **Setup Complexity** | Medium (need Supabase account) | Low (just Python) |
| **Cloud Dependencies** | Yes | No |
| **Portability** | Requires internet | Fully offline |

## Files to Use

**Standalone Mode:**
- ✅ `requirements-standalone.txt`
- ✅ `create_admin_standalone.py`
- ✅ `t2t_admin_be_standalone.py`
- ✅ No `.env` Supabase variables needed

**Supabase Mode:**
- ✅ `requirements.txt`
- ✅ `create_admin.py`
- ✅ `t2t_admin_be.py`
- ✅ Requires `.env` with Supabase credentials

## Installation on Remote Server

### 1. Copy Files to Server

```bash
# Using scp
scp -r t2t_training_dev/ user@server:/home/user/

# Or using rsync
rsync -avz t2t_training_dev/ user@server:/home/user/t2t_training_dev/

# SSH into server
ssh user@server
cd t2t_training_dev
```

### 2. Install System Dependencies

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv build-essential python3-dev

# CentOS/RHEL
sudo yum install -y python3 python3-pip gcc python3-devel

# macOS
brew install python3
```

### 3. Set Up Python Environment

```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # or: . venv/bin/activate

# Install standalone dependencies
pip install --upgrade pip
pip install -r requirements-standalone.txt
```

### 4. Initialize Database

```bash
# Create all tables including admin tables
python3 <<EOF
from t2t_store import init_db
init_db('t2t.db')
print("Database initialized successfully!")
EOF

# Verify
sqlite3 t2t.db "SELECT name FROM sqlite_master WHERE type='table';" | grep admin
```

Should show:
```
admin_users
admin_sessions
```

### 5. Configure Environment

Create `.env` file (minimal for standalone):

```bash
cat > .env << 'EOF'
# Database
T2T_DB=t2t.db

# Ports
T2T_BACKEND_PORT=5001
T2T_ADMIN_PORT=5002
T2T_FRONTEND_PORT=8050
T2T_ADMIN_FRONTEND_PORT=8051

# Bind to all interfaces (for remote access)
T2T_HOST=0.0.0.0

# PDF Storage
T2T_PDF_STORAGE=pdfs

# Admin emails (for legacy checks)
T2T_ADMIN_EMAILS=admin@example.com

# Optional: Email for Unpaywall API
UNPAYWALL_EMAIL=your.email@example.com
EOF

chmod 600 .env
```

### 6. Create Admin Account

```bash
python3 create_admin_standalone.py admin@example.com --name "Administrator"
```

**IMPORTANT:** Save the password shown on screen immediately!

The password is also saved to `.admin_password_*.txt` (chmod 600).

### 7. Test Locally

```bash
# Start all services
./start_all.sh

# Check if running
ps aux | grep python3 | grep t2t

# Test connections
curl http://localhost:5001/api/health  # Backend
curl http://localhost:5002/api/health  # Admin backend
curl http://localhost:8050  # Frontend
curl http://localhost:8051  # Admin frontend
```

### 8. Configure Firewall

```bash
# Allow ports for remote access
sudo ufw allow 8050/tcp  # Annotation interface
sudo ufw allow 8051/tcp  # Admin panel

# Optional: Backend APIs (if accessed externally)
sudo ufw allow 5001/tcp
sudo ufw allow 5002/tcp

# Check firewall status
sudo ufw status
```

### 9. Access from Remote Machine

From your local machine:

```
http://server-ip:8050  # Annotation interface
http://server-ip:8051  # Admin panel (login with created credentials)
```

## Production Deployment with Systemd

Create service file:

```bash
sudo nano /etc/systemd/system/t2t.service
```

Content:

```ini
[Unit]
Description=Text2Trait Annotation System
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/home/your-username/t2t_training_dev
Environment="PATH=/home/your-username/t2t_training_dev/venv/bin"
ExecStart=/home/your-username/t2t_training_dev/start_all.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable t2t
sudo systemctl start t2t
sudo systemctl status t2t
```

## Nginx Reverse Proxy (Optional)

For production with domain name:

```bash
sudo nano /etc/nginx/sites-available/t2t
```

Content:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Annotation interface
    location / {
        proxy_pass http://127.0.0.1:8050;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Admin panel
    location /admin/ {
        proxy_pass http://127.0.0.1:8051/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:5001/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Admin API
    location /api/admin/ {
        proxy_pass http://127.0.0.1:5002/api/admin/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Enable:

```bash
sudo ln -s /etc/nginx/sites-available/t2t /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## SSL/HTTPS (Recommended for Production)

```bash
# Install Certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal is configured automatically
sudo certbot renew --dry-run
```

## Backup Strategy

### Automated Daily Backup

```bash
#!/bin/bash
# /home/user/backup-t2t.sh

BACKUP_DIR=/home/user/backups
PROJECT_DIR=/home/user/t2t_training_dev
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
cp $PROJECT_DIR/t2t.db $BACKUP_DIR/t2t_${DATE}.db

# Backup PDFs (if not too large)
tar -czf $BACKUP_DIR/pdfs_${DATE}.tar.gz -C $PROJECT_DIR pdfs/

# Keep only last 30 days
find $BACKUP_DIR -name "t2t_*.db" -mtime +30 -delete
find $BACKUP_DIR -name "pdfs_*.tar.gz" -mtime +30 -delete

echo "Backup completed: $(date)"
```

Add to crontab:

```bash
chmod +x /home/user/backup-t2t.sh
crontab -e
```

Add line:

```
0 2 * * * /home/user/backup-t2t.sh >> /home/user/backup.log 2>&1
```

## Monitoring

### Check Service Health

```bash
# Check if processes are running
systemctl status t2t

# Check port usage
ss -tulpn | grep -E '5001|5002|8050|8051'

# Check database size
ls -lh /home/user/t2t_training_dev/t2t.db

# Check database stats
sqlite3 t2t.db "
SELECT 'Sentences: ' || COUNT(*) FROM sentences
UNION ALL
SELECT 'Tuples: ' || COUNT(*) FROM tuples
UNION ALL
SELECT 'Projects: ' || COUNT(*) FROM projects
UNION ALL
SELECT 'Papers: ' || COUNT(*) FROM project_papers
UNION ALL
SELECT 'Admins: ' || COUNT(*) FROM admin_users;
"
```

### Log Monitoring

```bash
# View logs
tail -f /home/user/t2t_training_dev/logs/*.log

# Or if using systemd
journalctl -u t2t -f
```

## Troubleshooting

### bcrypt Installation Fails

```bash
# Install build tools
sudo apt-get install -y build-essential python3-dev libffi-dev

# Or on CentOS
sudo yum install -y gcc python3-devel libffi-devel

# Retry
pip install bcrypt
```

### Port Already in Use

```bash
# Find process
sudo lsof -i :8050

# Kill it
sudo kill -9 <PID>

# Or kill all t2t processes
pkill -f "python3.*t2t"
```

### Database Locked Error

```bash
# Check for locks
fuser t2t.db

# Kill processes
pkill -9 python3

# Restart
./start_all.sh
```

### Permission Denied

```bash
# Fix ownership
sudo chown -R $USER:$USER /home/user/t2t_training_dev

# Fix permissions
chmod 755 /home/user/t2t_training_dev
chmod 600 /home/user/t2t_training_dev/.env
chmod 600 /home/user/t2t_training_dev/t2t.db
```

## Security Checklist

- [ ] Admin password files secured (chmod 600) or deleted
- [ ] Database file secured (chmod 600)
- [ ] .env file secured (chmod 600)
- [ ] Firewall configured
- [ ] SSL/HTTPS enabled (if public)
- [ ] Regular backups configured
- [ ] Strong admin passwords used
- [ ] Unnecessary ports closed

## Performance Tips

### For Better Performance

```bash
# Increase Python workers
export T2T_WORKERS=8

# Use faster WSGI server (optional)
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5001 t2t_training_be:app
```

### Database Optimization

```bash
# Run periodically
sqlite3 t2t.db "VACUUM; ANALYZE;"

# Check database integrity
sqlite3 t2t.db "PRAGMA integrity_check;"
```

## Migration to Standalone

If you're currently using Supabase and want to migrate:

1. **Export from Supabase** (manual SQL export)
2. **Initialize standalone database**
3. **Import data to SQLite**
4. **Switch to standalone scripts**
5. **Test thoroughly**

See migration guide (if needed, create one).

## Summary

✅ **Advantages of Standalone:**
- No cloud dependencies
- Lower cost (no cloud bills)
- Better privacy (all data local)
- Offline capable
- Simpler deployment
- Easier backup/restore

❌ **Limitations:**
- SQLite not ideal for high concurrency
- Manual scaling required
- No built-in replication
- Single point of failure

**When to use standalone:**
- On-premise deployment required
- Privacy/security concerns
- Low to medium usage
- No internet connectivity
- Research/academic use

**When to use Supabase:**
- High availability needed
- Multiple geographic locations
- High concurrency
- Managed backups preferred
- Rapid scaling required

## Support

- Check logs: `tail -f logs/*.log`
- Database issues: `sqlite3 t2t.db`
- Process issues: `ps aux | grep t2t`
- Network issues: `netstat -tulpn | grep python`

The standalone version provides full feature parity with the Supabase version while being completely self-contained!
