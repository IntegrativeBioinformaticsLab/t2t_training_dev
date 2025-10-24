# Deployment Comparison Guide

Quick reference to choose the right deployment option for your needs.

## Quick Decision Tree

```
Do you need the full admin panel and project management?
├─ No  → Use Simple Mode (./start_simple.sh)
└─ Yes → Continue...

Do you have a Supabase account?
├─ Yes → Use Supabase Version
└─ No  → Continue...

Do you want to use cloud services?
├─ Yes → Sign up for Supabase
└─ No  → Use Standalone Version ⭐ RECOMMENDED
```

## Feature Comparison

| Feature | Simple | Standalone | Supabase |
|---------|--------|------------|----------|
| **Setup Complexity** | Low | Low | Medium |
| **Admin Authentication** | ❌ | ✅ | ✅ |
| **Project Management** | ❌ | ✅ | ✅ |
| **Batch PDF Fetching** | ❌ | ✅ | ✅ |
| **Project/Paper Dropdowns** | ❌ | ✅ | ✅ |
| **Manual DOI Entry** | ✅ | ✅ | ✅ |
| **Basic Annotation** | ✅ | ✅ | ✅ |
| **Tuple Editor (Admin)** | ❌ | ✅ | ✅ |
| **User Management** | ❌ | ✅ | ✅ |
| **Database** | SQLite | SQLite | PostgreSQL |
| **Internet Required** | No* | No* | Yes |
| **Cloud Account Needed** | ❌ | ❌ | ✅ |
| **Cost** | Free | Free | Free tier + |
| **Scalability** | Single user | Low-Medium | High |
| **Data Location** | Local | Local | Cloud |
| **Backup** | Manual | Manual | Automatic |

\* Internet only needed for PDF fetching and DOI metadata

## Technical Comparison

| Aspect | Simple | Standalone | Supabase |
|--------|--------|------------|----------|
| **Installation** |
| Python packages | 15 | 16 | 17 |
| System dependencies | None | build-essential | None |
| Cloud setup | None | None | Supabase account |
| Time to deploy | 2 min | 5 min | 10 min |
| **Database** |
| Type | SQLite | SQLite | PostgreSQL |
| Tables | 6 | 10 | 10 |
| Max size | ~140TB | ~140TB | Unlimited |
| Concurrent users | 1-5 | 1-20 | Unlimited |
| **Security** |
| Admin auth | None | bcrypt + sessions | Supabase Auth |
| RLS policies | N/A | N/A | Yes |
| Password storage | N/A | bcrypt hash | Supabase |
| Session management | N/A | SQLite | Supabase |
| **Deployment** |
| Single machine | ✅ | ✅ | ✅ |
| Multi-server | ❌ | Limited | ✅ |
| Docker | ✅ | ✅ | ✅ |
| Cloud hosting | ✅ | ✅ | ✅ |
| On-premise | ✅ | ✅ | Limited |

## File Comparison

### Simple Mode

Uses:
- `t2t_training_be.py` (backend)
- `t2t_training_fe.py` (frontend)
- `t2t_store.py` (database)

Doesn't need:
- Admin backend
- Admin frontend
- Admin scripts
- Supabase dependencies

### Standalone Mode

Uses:
- All Simple Mode files, PLUS:
- `t2t_admin_be_standalone.py` (admin backend)
- `t2t_admin_fe.py` (admin frontend)
- `create_admin_standalone.py` (admin management)
- `requirements-standalone.txt` (dependencies)

Doesn't need:
- Supabase client library
- Supabase account
- Internet connection (except PDF APIs)

### Supabase Mode

Uses:
- All files
- `t2t_admin_be.py` (Supabase version)
- `create_admin.py` (Supabase version)
- `requirements.txt` (includes Supabase)

Requires:
- Supabase account
- Internet connection
- Environment variables for Supabase

## Use Cases

### Simple Mode

**Perfect for:**
- Quick testing
- Single user
- Manual DOI entry only
- Learning the system
- No admin needs

**Example:**
"I want to try annotating a few papers manually."

### Standalone Mode ⭐

**Perfect for:**
- University research labs
- Corporate on-premise deployment
- Privacy-sensitive data
- No internet connectivity
- Full control over data
- Small to medium teams (5-50 users)
- Development/staging environments

**Examples:**
- "We need to annotate papers but data must stay on campus."
- "I want all features but no cloud dependencies."
- "Deploy on our internal server without internet."

### Supabase Mode

**Perfect for:**
- Cloud deployment
- Global team collaboration
- High availability requirements
- Managed backups
- Rapid scaling
- Large teams (50+ users)

**Examples:**
- "Our team is distributed across continents."
- "We expect thousands of annotations per day."
- "We want automatic backups and scaling."

## Migration Paths

### From Simple → Standalone

```bash
# 1. Install additional dependencies
pip install bcrypt

# 2. Re-initialize database (adds admin tables)
python3 -c "from t2t_store import init_db; init_db('t2t.db')"

# 3. Create admin account
python3 create_admin_standalone.py admin@example.com

# 4. Start with admin services
./start_all.sh
```

✅ **Data preserved:** All existing annotations remain

### From Simple → Supabase

```bash
# 1. Sign up for Supabase
# 2. Get connection credentials
# 3. Add to .env
# 4. Create admin via Supabase script
python3 create_admin.py admin@example.com
```

✅ **Data preserved:** Existing annotations remain in SQLite

### From Standalone → Supabase

```bash
# Option 1: Run both (SQLite for annotations, Supabase for projects)
# Already works! No changes needed.

# Option 2: Migrate everything to Supabase
# (Would require custom migration script - not provided yet)
```

### From Supabase → Standalone

```bash
# 1. Export Supabase data (SQL dump or CSV)
# 2. Import to SQLite
# 3. Switch to standalone scripts
# (Custom migration script required - not provided yet)
```

## Performance Comparison

### Simple Mode
- **Response time:** <50ms
- **Max concurrent users:** 5
- **PDF serving:** Direct from disk
- **Database queries:** Instant (SQLite)

### Standalone Mode
- **Response time:** <50ms
- **Max concurrent users:** 20
- **PDF serving:** Direct from disk
- **Database queries:** Instant (SQLite)
- **Admin operations:** Instant (SQLite)

### Supabase Mode
- **Response time:** 100-300ms (network latency)
- **Max concurrent users:** Unlimited
- **PDF serving:** Direct from disk
- **Database queries:** Fast (PostgreSQL + network)
- **Admin operations:** Fast (PostgreSQL + network)

## Cost Comparison

### Simple Mode
- **Hosting:** Your server cost only
- **Database:** Free (SQLite)
- **Total:** $0 (or your server cost)

### Standalone Mode
- **Hosting:** Your server cost only
- **Database:** Free (SQLite)
- **Total:** $0 (or your server cost)

### Supabase Mode
- **Hosting:** Your server cost for app
- **Database:** Supabase pricing
  - Free tier: 500MB, 2GB bandwidth/month
  - Pro: $25/month + usage
- **Total:** $0-25+/month (depends on usage)

## Recommended Choice

### For Most Users: **Standalone Mode** ⭐

Why:
- ✅ Full features (admin, projects, PDFs)
- ✅ No cloud dependencies
- ✅ No ongoing costs
- ✅ Simple deployment
- ✅ Full privacy control
- ✅ Works offline
- ✅ Easy backup (single file)

### When to Choose Supabase:
- Need high availability (99.9%+ uptime)
- Global team (multiple continents)
- High concurrent usage (100+ users)
- Want managed infrastructure
- Okay with data in cloud
- Need automatic scaling

### When to Choose Simple:
- Just testing the concept
- Single user
- Don't need admin features
- Want absolute minimum setup

## Quick Start Commands

### Simple Mode
```bash
./start_simple.sh
```

### Standalone Mode
```bash
pip install -r requirements-standalone.txt
python3 -c "from t2t_store import init_db; init_db('t2t.db')"
python3 create_admin_standalone.py admin@example.com --name "Admin"
./start_all.sh
```

### Supabase Mode
```bash
pip install -r requirements.txt
python3 create_admin.py admin@example.com --name "Admin"
./start_all.sh
```

## Documentation Links

- **Simple Mode:** See README.md Quick Start
- **Standalone Mode:** [STANDALONE_QUICKSTART.md](STANDALONE_QUICKSTART.md) and [STANDALONE_DEPLOYMENT.md](STANDALONE_DEPLOYMENT.md)
- **Supabase Mode:** [SECURITY_SETUP.md](SECURITY_SETUP.md) and [DEPLOYMENT_OPTIONS.md](DEPLOYMENT_OPTIONS.md)

## Summary

| If you want... | Choose |
|----------------|--------|
| Quickest start | Simple |
| Full features + no cloud | **Standalone ⭐** |
| Cloud deployment | Supabase |
| Privacy/security | Standalone |
| Global collaboration | Supabase |
| University research | Standalone |
| Corporate on-premise | Standalone |
| High availability | Supabase |
| Lowest cost | Simple or Standalone |

**Most users should use Standalone Mode** - it provides all features with no cloud dependencies and is perfect for independent server deployment.
