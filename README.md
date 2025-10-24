# Text2Trait: Training Data Builder

A web-based application for annotating biological text with entity relationships and metadata. Built with Python, Flask, Dash, and SQLite - no cloud dependencies required.

## Features

### Core Annotation Features
- **Email-based user identification** with validation
- **Entity and relationship annotation** with customizable types
- **Multi-user concurrency protection** with tuple ownership tracking
- **User-based deletion protection** - only creators and admins can delete tuples
- **Dropdown menus** for entity types (Gene, Protein, Trait, etc.) and relationship types

### Project-Based PDF Management
- **Project organization** - Group papers into annotation projects
- **Batch PDF fetching** - Download PDFs using doi2pdf and Unpaywall APIs
- **Project/paper dropdowns** - Select papers from projects for annotation
- **Local PDF storage** - Serve PDFs without embedding restrictions
- **Text selection always works** - Copy text from any PDF to annotation

### Admin Features
- **Secure authentication** - Password-based login with auto-generated strong passwords
- **Session management** - 24-hour sessions with automatic expiry
- **Admin panel** - Manage projects, papers, and tuples
- **Bulk DOI input** - Add multiple papers to projects at once
- **Tuple editor** - View and edit tuples from all users
- **DOI validation and metadata** - Automatic CrossRef API integration

## Quick Start

### Installation

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Initialize database
python3 -c "from t2t_store import init_db; init_db('t2t.db')"

# 3. Create admin account
python3 create_admin.py admin@example.com --name "Admin User"
```

**IMPORTANT:** Save the password displayed on screen! It's also saved to `.admin_password_*.txt`

### Start Services

```bash
./start_all.sh
```

### Access the Application

- **Annotation Interface**: http://localhost:8050
- **Admin Panel**: http://localhost:8051 (login required)

## System Requirements

- Python 3.9 or higher
- 2GB RAM minimum
- 10GB disk space (for PDFs)
- Linux, macOS, or Windows (WSL)

## Usage

### For Annotators

1. **Enter your email** - Required for attribution
2. **Select or enter DOI** - Choose from project papers or enter manually
3. **Annotate text**:
   - Select text from the PDF viewer
   - Click "Copy selected text to sentence"
   - Add tuples with entity relationships
   - Use dropdowns for entity and relation types
4. **Save annotations** - Stored in SQLite database
5. **Browse saved annotations** - View and manage your work

### For Administrators

1. **Login** - Use your admin credentials at http://localhost:8051
2. **Create projects** - Organize papers by research topic
3. **Add DOIs** - Batch add papers to projects
4. **Fetch PDFs** - Automatically download from open access sources
5. **Manage tuples** - View and edit all annotations
6. **Monitor progress** - Track annotation statistics

## Database

All data is stored in a single **SQLite database file** (`t2t.db`):

### Tables

- `entity_types` - Gene, Protein, Trait, Enzyme, QTL, etc.
- `relation_types` - increases, decreases, regulates, etc.
- `sentences` - Annotated text with DOI references
- `tuples` - Entity relationships with contributor tracking
- `doi_metadata` - Paper DOI references
- `user_sessions` - Session tracking for users
- `admin_users` - Admin accounts with bcrypt passwords
- `admin_sessions` - Admin session management
- `projects` - Project organization
- `project_papers` - Papers within projects with PDF metadata

### Backup

```bash
# Simple backup
cp t2t.db t2t_backup_$(date +%Y%m%d).db

# Backup with PDFs
tar -czf backup_$(date +%Y%m%d).tar.gz t2t.db pdfs/
```

## Configuration

Edit `.env` file:

```bash
# Database
T2T_DB=t2t.db

# Ports
T2T_BACKEND_PORT=5001
T2T_ADMIN_PORT=5002
T2T_FRONTEND_PORT=8050
T2T_ADMIN_FRONTEND_PORT=8051

# Host (0.0.0.0 for remote access)
T2T_HOST=0.0.0.0

# PDF Storage
T2T_PDF_STORAGE=pdfs

# Optional: Email for Unpaywall API
UNPAYWALL_EMAIL=your.email@example.com
```

## Admin Management

### Create Admin Account

```bash
python3 create_admin.py admin@example.com --name "Admin User"
```

A secure 24-character password is generated automatically.

### Reset Admin Password

```bash
python3 create_admin.py admin@example.com --reset
```

### List Admins

```bash
sqlite3 t2t.db "SELECT email, display_name, created_at FROM admin_users;"
```

## Production Deployment

See [STANDALONE_DEPLOYMENT.md](STANDALONE_DEPLOYMENT.md) for:
- systemd service configuration
- Nginx reverse proxy setup
- SSL certificate configuration
- Firewall configuration
- Automated backups
- Monitoring and logging

## Troubleshooting

### bcrypt Installation Fails

```bash
# Ubuntu/Debian
sudo apt-get install -y build-essential python3-dev

# CentOS/RHEL
sudo yum install -y gcc python3-devel

# Then retry
pip install bcrypt
```

### Port Already in Use

```bash
# Find process
sudo lsof -i :8050

# Kill it
sudo kill -9 <PID>
```

### Database Locked

```bash
# Kill all Python processes
pkill -9 python3

# Restart services
./start_all.sh
```

### Dropdowns Not Showing

Dropdowns are populated from the database. If they're empty:

```bash
# Check database
python3 -c "
from t2t_store import fetch_entity_dropdown_options, fetch_relation_dropdown_options
print('Entities:', fetch_entity_dropdown_options('t2t.db'))
print('Relations:', fetch_relation_dropdown_options('t2t.db'))
"
```

If empty, reinitialize:

```bash
python3 -c "from t2t_store import init_db; init_db('t2t.db')"
```

## File Structure

```
t2t_training_dev/
├── t2t_training_be.py      # Main backend API
├── t2t_training_fe.py      # Annotation interface
├── t2t_admin_be.py         # Admin backend API
├── t2t_admin_fe.py         # Admin panel interface
├── t2t_store.py            # Database functions
├── create_admin.py         # Admin account management
├── start_all.sh            # Start all services
├── start_simple.sh         # Start basic annotation only
├── requirements.txt        # Python dependencies
├── .env                    # Configuration
├── t2t.db                  # SQLite database
└── pdfs/                   # PDF storage directory
```

## API Endpoints

### Main Backend (port 5001)

- `GET /api/choices` - Entity and relation type options
- `POST /api/save` - Save annotations
- `GET /api/recent` - Recent annotations
- `POST /api/validate-doi` - Validate and fetch DOI metadata
- `GET /api/get-pdf-url/<doi>` - Get PDF URL from Unpaywall/CrossRef

### Admin Backend (port 5002)

- `POST /api/admin/login` - Admin login
- `POST /api/admin/logout` - Admin logout
- `GET /api/admin/verify` - Verify session
- `GET /api/admin/projects` - List projects
- `POST /api/admin/projects` - Create project
- `GET /api/admin/projects/<id>/papers` - List papers in project
- `POST /api/admin/projects/<id>/papers` - Add paper to project
- `POST /api/admin/projects/<id>/fetch` - Fetch PDFs for project
- `GET /api/admin/tuples` - List all tuples
- `PUT /api/admin/tuples/<id>` - Update tuple

## PDF Sources

The application attempts to find PDFs from:

1. **Unpaywall.org** - Open access PDFs (primary)
2. **CrossRef** - Publisher links (fallback)
3. **doi2pdf API** - Additional source (if configured)

Only freely available PDFs can be displayed. Paywalled content will show an error message.

## Architecture

- **Backend**: Flask REST API with SQLite
- **Frontend**: Dash (Plotly) with Bootstrap
- **Database**: SQLite (single file)
- **Authentication**: bcrypt password hashing + session tokens
- **PDF Viewer**: Native browser PDF viewer (no proxy)

## Security

- Passwords hashed with bcrypt (12 rounds)
- Auto-generated 24-character secure passwords
- 24-hour session expiry
- Session tokens (32-byte random)
- Admin-only endpoints protected
- No plain-text password storage

## License

See LICENSE file for details.

## Support

- Installation: See [STANDALONE_DEPLOYMENT.md](STANDALONE_DEPLOYMENT.md)
- Quick reference: See [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
- Deployment comparison: See [DEPLOYMENT_COMPARISON.md](DEPLOYMENT_COMPARISON.md)
- Bug reports: Check logs in `logs/` directory

## Development

### Running in Development Mode

```bash
# Backend with auto-reload
export FLASK_ENV=development
python3 t2t_training_be.py

# Frontend with debug mode
python3 t2t_training_fe.py
```

### Database Migrations

If updating the schema:

```bash
# Backup first!
cp t2t.db t2t.db.backup

# Run migration if provided
python3 migrate_db.py
```

## Credits

Built with:
- Flask - Web framework
- Dash - Interactive dashboards
- SQLite - Database
- bcrypt - Password hashing
- Bootstrap - UI framework

---

**Text2Trait** - Making biological text annotation simple and efficient.
