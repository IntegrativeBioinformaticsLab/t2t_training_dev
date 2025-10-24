# Installation Steps

Complete installation guide for Text2Trait annotation system.

## Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- 2GB RAM minimum
- 10GB disk space for PDFs

### System-Specific Setup

#### Ubuntu/Debian

```bash
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv build-essential python3-dev
```

#### CentOS/RHEL

```bash
sudo yum install -y python3 python3-pip gcc python3-devel
```

#### macOS

```bash
brew install python3
```

## Installation Steps

### 1. Get the Code

```bash
# If using git
git clone <your-repo-url> t2t_training_dev
cd t2t_training_dev

# Or extract from archive
tar -xzf t2t_training_dev.tar.gz
cd t2t_training_dev
```

### 2. Create Virtual Environment (Recommended)

```bash
python3 -m venv venv
source venv/bin/activate  # On Linux/macOS

# On Windows
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**If bcrypt installation fails:**

```bash
# Ubuntu/Debian
sudo apt-get install -y build-essential python3-dev libffi-dev

# CentOS/RHEL
sudo yum install -y gcc python3-devel libffi-devel

# macOS
xcode-select --install

# Then retry
pip install bcrypt
```

### 4. Configure Environment

```bash
# Copy example configuration
cp .env.example .env

# Edit configuration (optional)
nano .env
```

Minimal configuration:
```bash
T2T_DB=t2t.db
T2T_HOST=0.0.0.0
T2T_PDF_STORAGE=pdfs
```

### 5. Initialize Database

```bash
python3 -c "from t2t_store import init_db; init_db('t2t.db')"
```

This creates:
- All database tables
- Entity types (Gene, Protein, Trait, etc.)
- Relation types (increases, decreases, etc.)

### 6. Create Admin Account

```bash
python3 create_admin.py your.email@example.com --name "Your Name"
```

**IMPORTANT:** Save the generated password immediately!

The password is:
- Displayed on screen (once)
- Saved to `.admin_password_*.txt` (chmod 600)

### 7. Verify Installation

```bash
# Check database
sqlite3 t2t.db "SELECT name FROM sqlite_master WHERE type='table';"

# Should show: entity_types, relation_types, sentences, tuples,
#              doi_metadata, user_sessions, admin_users, admin_sessions,
#              projects, project_papers

# Check entity types
python3 -c "from t2t_store import fetch_entity_dropdown_options; print(fetch_entity_dropdown_options('t2t.db'))"

# Check admin account
sqlite3 t2t.db "SELECT email, display_name, created_at FROM admin_users;"
```

### 8. Start Services

#### Option A: All Services (Recommended)

```bash
./start_all.sh
```

This starts:
- Main backend (port 5001)
- Admin backend (port 5002)
- Annotation interface (port 8050)
- Admin panel (port 8051)

#### Option B: Simple Mode (No Admin)

```bash
./start_simple.sh
```

Only starts annotation interface (port 8050)

### 9. Access the Application

#### From Local Machine

- Annotation: http://localhost:8050
- Admin Panel: http://localhost:8051

#### From Remote Machine

- Annotation: http://server-ip:8050
- Admin Panel: http://server-ip:8051

**Note:** Make sure `T2T_HOST=0.0.0.0` in `.env` for remote access

### 10. Test the Application

#### Test Annotation Interface

1. Open http://localhost:8050
2. Enter your email
3. Enter a DOI (e.g., `10.1038/nature12345`)
4. Add entity relationships
5. Save annotation

#### Test Admin Panel

1. Open http://localhost:8051
2. Login with admin credentials
3. Create a project
4. Add a DOI to the project
5. View tuples

## Firewall Configuration

If accessing from remote machines:

```bash
# Ubuntu/Debian
sudo ufw allow 8050/tcp
sudo ufw allow 8051/tcp

# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=8050/tcp
sudo firewall-cmd --permanent --add-port=8051/tcp
sudo firewall-cmd --reload
```

## Automated Startup (Optional)

### Using systemd

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
WorkingDirectory=/path/to/t2t_training_dev
Environment="PATH=/path/to/t2t_training_dev/venv/bin"
ExecStart=/path/to/t2t_training_dev/start_all.sh
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

## Troubleshooting

### Port Already in Use

```bash
# Find process
sudo lsof -i :8050

# Kill it
sudo kill -9 <PID>

# Or kill all Python processes
pkill -f "python3.*t2t"
```

### Database Locked

```bash
pkill -9 python3
rm -f t2t.db-journal
./start_all.sh
```

### Dropdowns Not Working

```bash
# Reinitialize database
python3 -c "from t2t_store import init_db; init_db('t2t.db')"
```

### Can't Access from Remote Machine

```bash
# Check if bound to 0.0.0.0
netstat -tulpn | grep 8050

# Update .env
echo "T2T_HOST=0.0.0.0" >> .env

# Check firewall
sudo ufw status

# Allow ports
sudo ufw allow 8050/tcp
sudo ufw allow 8051/tcp
```

### bcrypt Module Not Found

```bash
# Install build dependencies
sudo apt-get install -y build-essential python3-dev

# Reinstall bcrypt
pip install --force-reinstall bcrypt
```

## Verification Checklist

- [ ] Python 3.9+ installed
- [ ] Dependencies installed successfully
- [ ] Database initialized
- [ ] Admin account created
- [ ] All services start without errors
- [ ] Annotation interface accessible
- [ ] Admin panel accessible
- [ ] Can login to admin panel
- [ ] Dropdowns show entity/relation types
- [ ] Can save annotations

## Next Steps

1. **Production deployment**: See [STANDALONE_DEPLOYMENT.md](STANDALONE_DEPLOYMENT.md)
2. **User guide**: See README.md
3. **Admin guide**: See [ADMIN_GUIDE.md](ADMIN_GUIDE.md)
4. **Quick reference**: See [QUICK_REFERENCE.md](QUICK_REFERENCE.md)

## Uninstallation

```bash
# Stop services
pkill -f "python3.*t2t"

# Remove files
cd ..
rm -rf t2t_training_dev

# Remove systemd service (if installed)
sudo systemctl stop t2t
sudo systemctl disable t2t
sudo rm /etc/systemd/system/t2t.service
sudo systemctl daemon-reload
```

## Getting Help

- Check logs in `logs/` directory
- Review README.md for usage
- See STANDALONE_DEPLOYMENT.md for production setup
- Check GitHub issues (if applicable)
