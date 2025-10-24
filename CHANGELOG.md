# Changelog

## Version 2.0.0 - Security & Project Management Update

### New Features

#### 🔐 Secure Admin Authentication
- **Password-based login** with bcrypt hashing
- **Auto-generated strong passwords** (24 characters, mixed case, numbers, symbols)
- **Session management** with 24-hour automatic expiry
- **Password reset capability**
- Admin account creation script: `python3 create_admin.py`

#### 📁 Project-Based PDF Management
- **Project organization** - Group papers into annotation projects
- **Batch PDF fetching** - Download PDFs using doi2pdf → Unpaywall fallback
- **Project/paper dropdowns** - Select papers for annotation
- **Local PDF storage** - Serve PDFs without iframe restrictions
- **Text selection always works** - No browser security issues

#### 🛠️ Admin Panel Enhancements
- Secure login page with session management
- Project creation and management
- Bulk DOI input (paste multiple DOIs at once)
- PDF batch fetching with status tracking
- Tuple editor - view all users' annotations

### Database Changes

#### New Supabase Tables
- `projects` - Project metadata
- `project_papers` - Papers in projects with DOI, title, authors, PDF paths
- `admin_users` - Admin accounts with bcrypt password hashes
- `admin_sessions` - Active admin sessions with expiry

#### Existing Tables (SQLite)
- No changes to existing tuple/sentence storage
- Backward compatible with existing data

### API Changes

#### New Admin Endpoints
- `POST /api/admin/login` - Admin login, returns session token
- `POST /api/admin/logout` - Invalidate session
- `GET /api/admin/verify` - Verify session validity
- `POST /api/admin/projects` - Create project (requires session)
- `GET /api/admin/projects` - List projects
- `GET /api/admin/projects/{id}/papers` - List papers in project
- `POST /api/admin/projects/{id}/papers` - Add DOIs to project
- `POST /api/admin/projects/{id}/fetch` - Fetch PDFs for project
- `GET /api/pdfs/{project_id}/{paper_id}` - Serve PDF file
- `GET /api/admin/tuples` - List all tuples
- `PUT /api/admin/tuples/{id}` - Update tuple

#### Authentication
- All admin endpoints now use `@session_required` decorator
- Session token passed via `Authorization: Bearer {token}` header
- Old `@admin_required` (email-based) deprecated but still functional

### Security Improvements

#### Password Security
- Bcrypt hashing with 12 rounds (industry standard)
- Passwords never stored in plain text
- Cannot be reverse-engineered

#### Session Security
- Cryptographically random tokens (32 bytes, URL-safe)
- 24-hour automatic expiry
- IP address and user agent tracking
- Invalidation on logout

#### API Security
- All admin operations require valid session
- Expired sessions automatically rejected
- No operations possible without authentication

### New Scripts

- `create_admin.py` - Create admin accounts with secure passwords
- `diagnose_env.py` - Check environment variable configuration
- `start_all.sh` - Start all services with proper environment loading
- `start_admin_only.sh` - Start only admin services for testing
- `test_admin_backend.sh` - Test admin backend startup
- `setup.sh` - Complete setup with dependency installation

### New Documentation

- `SECURITY_SETUP.md` - Comprehensive security setup guide
- `ADMIN_GUIDE.md` - Updated with new authentication workflow
- `CHANGELOG.md` - This file

### Dependencies Added

- `bcrypt>=4.0.0,<5.0.0` - Password hashing
- `supabase>=2.0.0,<3.0.0` - Database client

### Migration Notes

#### For New Installations
1. Run `./setup.sh` to install dependencies
2. Create admin account: `python3 create_admin.py your@email.com`
3. Start services: `./start_all.sh`
4. Log in to admin panel with generated password

#### For Existing Installations
1. Update dependencies: `pip install -r requirements.txt`
2. Run migrations (Supabase tables auto-created)
3. Create admin accounts for existing admins
4. Old email-based auth still works during transition
5. Migrate to new auth system when ready

### Breaking Changes

⚠️  **Admin Panel** now requires login
- Old direct access with email input deprecated
- Must create admin account and log in
- Sessions expire after 24 hours

### Backward Compatibility

✅  **Fully backward compatible**
- Existing tuple/sentence data unchanged
- Old annotation interface works as before
- Can still enter DOIs manually
- Email-based admin check still functional

### Benefits

#### For Administrators
- ✅ Secure password authentication
- ✅ Better project organization
- ✅ Bulk PDF preparation
- ✅ Centralized admin panel

#### For Annotators
- ✅ Easy paper selection from dropdowns
- ✅ PDF text selection always works
- ✅ No iframe embedding issues
- ✅ Offline-friendly after PDF download

#### For System Security
- ✅ Strong password hashing
- ✅ Session management
- ✅ Audit trail (IP, user agent)
- ✅ Automatic session expiry

### Known Issues

None currently identified.

### Future Enhancements

- Email notifications for password resets
- Two-factor authentication (2FA)
- Admin audit logs
- Project-level access control
- Annotation progress tracking per project
- Export annotations by project
- PDF text extraction and search

### Support

For help with:
- **Security setup**: See [SECURITY_SETUP.md](SECURITY_SETUP.md)
- **Admin operations**: See [ADMIN_GUIDE.md](ADMIN_GUIDE.md)
- **General usage**: See [README.md](README.md)
- **Deployment**: See [DEPLOYMENT.md](DEPLOYMENT.md)

### Contributors

- System architecture and implementation
- Security features and authentication
- Project management system
- PDF fetching integration

---

## Version 1.x (Previous)

See git history for previous versions.
