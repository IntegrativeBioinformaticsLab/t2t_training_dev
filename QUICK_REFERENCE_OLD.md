# Quick Reference Guide

## Installation

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Initialize database
python3 -c "from t2t_store import init_db; init_db('t2t.db')"

# 3. Create admin account
python3 create_admin.py admin@example.com --name "Admin"

# 4. Start services
./start_all.sh
```

## Access URLs

- **Annotation**: http://localhost:8050
- **Admin Panel**: http://localhost:8051

## Common Commands

### Admin Management

```bash
# Create admin account
python3 create_admin.py email@example.com --name "Name"

# Reset admin password
python3 create_admin.py email@example.com --reset

# List admins
sqlite3 t2t.db "SELECT email, display_name FROM admin_users;"
```

### Database Operations

```bash
# Backup database
cp t2t.db t2t_backup_$(date +%Y%m%d).db

# Check database
sqlite3 t2t.db "SELECT COUNT(*) FROM tuples;"

# View entity types
sqlite3 t2t.db "SELECT name FROM entity_types;"

# View relation types
sqlite3 t2t.db "SELECT name FROM relation_types;"
```

### Service Management

```bash
# Start all services
./start_all.sh

# Start simple mode (no admin)
./start_simple.sh

# Stop all services (Ctrl+C or)
pkill -f "python3.*t2t"

# Check if running
ps aux | grep python3 | grep t2t

# Check ports
ss -tulpn | grep -E '5001|5002|8050|8051'
```

## File Structure

```
t2t_training_dev/
├── t2t_training_be.py      # Main backend (port 5001)
├── t2t_training_fe.py      # Annotation UI (port 8050)
├── t2t_admin_be.py         # Admin backend (port 5002)
├── t2t_admin_fe.py         # Admin UI (port 8051)
├── t2t_store.py            # Database functions
├── create_admin.py         # Admin management
├── start_all.sh            # Start all services
├── requirements.txt        # Dependencies
├── .env                    # Configuration
├── t2t.db                  # SQLite database
└── pdfs/                   # PDF storage
```

## Configuration (.env)

```bash
# Database
T2T_DB=t2t.db

# Ports
T2T_BACKEND_PORT=5001
T2T_ADMIN_PORT=5002
T2T_FRONTEND_PORT=8050
T2T_ADMIN_FRONTEND_PORT=8051

# Host
T2T_HOST=0.0.0.0

# PDF Storage
T2T_PDF_STORAGE=pdfs

# Email for Unpaywall (optional)
UNPAYWALL_EMAIL=your@email.com
```

## API Endpoints

### Main Backend (5001)

- `GET /api/choices` - Entity/relation options
- `POST /api/save` - Save annotations
- `GET /api/recent` - Recent annotations
- `POST /api/validate-doi` - Validate DOI
- `GET /api/get-pdf-url/<doi>` - Get PDF URL

### Admin Backend (5002)

- `POST /api/admin/login` - Login
- `POST /api/admin/logout` - Logout
- `GET /api/admin/verify` - Verify session
- `GET /api/admin/projects` - List projects
- `POST /api/admin/projects` - Create project
- `GET /api/admin/projects/<id>/papers` - List papers
- `POST /api/admin/projects/<id>/papers` - Add paper
- `GET /api/admin/tuples` - List tuples

## Troubleshooting

### Port in Use

```bash
sudo lsof -i :8050
sudo kill -9 <PID>
```

### Database Locked

```bash
pkill -9 python3
./start_all.sh
```

### Dropdowns Empty

```bash
python3 -c "from t2t_store import init_db; init_db('t2t.db')"
```

### bcrypt Installation

```bash
sudo apt-get install -y build-essential python3-dev
pip install bcrypt
```

### Can't Access Remotely

```bash
# Check .env has T2T_HOST=0.0.0.0
grep T2T_HOST .env

# Check firewall
sudo ufw allow 8050/tcp
sudo ufw allow 8051/tcp
```

## Database Schema

### Main Tables

- `entity_types` - Gene, Protein, Trait, etc.
- `relation_types` - increases, decreases, regulates, etc.
- `sentences` - Annotated text
- `tuples` - Entity relationships
- `doi_metadata` - DOI references
- `user_sessions` - User sessions

### Admin Tables

- `admin_users` - Admin accounts (bcrypt passwords)
- `admin_sessions` - Login sessions (24hr expiry)
- `projects` - Project organization
- `project_papers` - Papers in projects

## Workflow

### For Annotators

1. Open http://localhost:8050
2. Enter email
3. Select/enter DOI
4. Annotate text with entity relationships
5. Save annotations

### For Admins

1. Login at http://localhost:8051
2. Create project
3. Add DOIs to project
4. Annotators can select from project papers
5. View/edit all annotations

## Production Deployment

See [STANDALONE_DEPLOYMENT.md](STANDALONE_DEPLOYMENT.md) for:
- systemd service setup
- Nginx reverse proxy
- SSL certificates
- Automated backups
- Monitoring

## Getting Help

- README: Full documentation
- ADMIN_GUIDE: Project management details
- STANDALONE_DEPLOYMENT: Production setup
- Check logs in `logs/` directory
