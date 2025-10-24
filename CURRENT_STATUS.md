# Current Status - System Ready for Testing

## What's Been Fixed

### 1. ✅ Passwordless Admin Login (Development Mode)

Added `T2T_SKIP_AUTH` environment variable to bypass authentication for debugging.

**Configuration in `.env`:**
```bash
# Development mode: Skip authentication (WARNING: Use only for debugging!)
T2T_SKIP_AUTH=true
```

**What This Does:**
- Admin panel loads without login required
- All admin endpoints work without session tokens
- Backend provides a mock admin user: `dev@localhost`
- Frontend skips login page entirely

**Security Note:**
⚠️ This is ONLY for development/debugging. Set to `false` in production!

### 2. ✅ Database Fixed and Verified

The database now contains all required entity and relation types:

**Entity Types (9):**
- Coordinates
- Enzyme
- Gene
- Metabolite
- Protein
- QTL
- Regulator
- Trait
- Variant

**Relation Types (15):**
- contributes_to
- decreases
- develops_from
- disrupts
- does_not_influence
- increases
- influences
- inhers_in
- is_a
- is_not_related_to
- is_related_to
- may_influence
- may_not_influence
- part_of
- regulates

### 3. ✅ Database Commits Fixed

All database write operations now properly commit:
- Session creation
- Session deletion
- Last login updates
- Project creation
- Paper additions

### 4. ✅ Datetime Handling Fixed

All deprecated `datetime.utcnow()` replaced with `datetime.now(timezone.utc)`.

## How to Test the System

### Step 1: Verify Database

```bash
# Load the binary database file (if needed)
# The t2t.db file should be 124KB SQLite database

# Verify entity types
python3 -c "from t2t_store import fetch_entity_dropdown_options; \
            print(fetch_entity_dropdown_options('t2t.db'))"

# Verify relation types
python3 -c "from t2t_store import fetch_relation_dropdown_options; \
            print(fetch_relation_dropdown_options('t2t.db'))"
```

**Expected Output:**
```
['Coordinates', 'Enzyme', 'Gene', 'Metabolite', 'Protein', 'QTL', 'Regulator', 'Trait', 'Variant']
['contributes_to', 'decreases', 'develops_from', 'disrupts', 'does_not_influence', 'increases', 'influences', 'inhers_in', 'is_a', 'is_not_related_to', 'is_related_to', 'may_influence', 'may_not_influence', 'part_of', 'regulates']
```

### Step 2: Verify Configuration

```bash
# Check that skip auth is enabled
grep T2T_SKIP_AUTH .env

# Should show:
# T2T_SKIP_AUTH=true
```

### Step 3: Stop Any Running Services

```bash
pkill -f "python3.*t2t"
```

### Step 4: Start All Services

```bash
./start_all.sh
```

This starts:
- **Main Backend** (port 5001) - `/api/choices`, `/api/save`, etc.
- **Admin Backend** (port 5002) - `/api/admin/projects`, etc.
- **Annotation Frontend** (port 8050) - Main annotation interface
- **Admin Frontend** (port 8051) - Admin panel

### Step 5: Test Annotation Interface

1. **Open:** http://localhost:8050

2. **Check the page loads:**
   - Should see email input field
   - Should see DOI input field or project/paper dropdowns

3. **Enter your email:** `M.D.Sharma@exeter.ac.uk`

4. **Check dropdowns appear:**
   - Entity type dropdown should show: Gene, Protein, Trait, etc.
   - Relation type dropdown should show: increases, decreases, etc.

5. **Click "Add tuple" button:**
   - New row should appear
   - Dropdowns should be populated

6. **Test saving:**
   - Select entities and relations
   - Click Save
   - Should save successfully

### Step 6: Test Admin Panel (No Login Required!)

1. **Open:** http://localhost:8051

2. **Should bypass login page** (goes directly to main admin interface)

3. **Test creating a project:**
   - Click "Create Project"
   - Enter project name and description
   - Should create successfully

4. **Test adding papers:**
   - Select a project
   - Paste DOIs
   - Should add successfully

5. **Test viewing tuples:**
   - Click "View Tuples" tab
   - Should show all annotations

## Troubleshooting

### Issue: Dropdowns Still Empty

**Check database:**
```bash
file t2t.db
# Should show: SQLite 3.x database, 124K

python3 -c "from t2t_store import fetch_entity_dropdown_options; \
            print(len(fetch_entity_dropdown_options('t2t.db')))"
# Should show: 9
```

**If database is corrupted:**
```bash
# Backup old database
mv t2t.db t2t.db.backup

# You may need to extract from backup or re-import data
# The current t2t.db has all the data you need
```

### Issue: Admin Panel Shows Login Page

**Check configuration:**
```bash
grep T2T_SKIP_AUTH .env
# Should show: T2T_SKIP_AUTH=true (not false)
```

**Restart services:**
```bash
pkill -f "python3.*t2t"
./start_all.sh
```

### Issue: Cannot Access from Remote Machine

**Check host binding:**
```bash
grep T2T_HOST .env
# Should show: T2T_HOST=0.0.0.0
```

**Check firewall:**
```bash
# Ubuntu/Debian
sudo ufw allow 8050/tcp
sudo ufw allow 8051/tcp

# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=8050/tcp
sudo firewall-cmd --permanent --add-port=8051/tcp
sudo firewall-cmd --reload
```

### Issue: Port Already in Use

```bash
# Find and kill processes
sudo lsof -i :8050
sudo lsof -i :8051
sudo kill -9 <PID>

# Or kill all
pkill -f "python3.*t2t"
```

## Testing Checklist

Use this checklist to verify everything works:

**Database:**
- [ ] Database file is SQLite (124KB)
- [ ] Entity types loaded (9 total)
- [ ] Relation types loaded (15 total)

**Configuration:**
- [ ] T2T_SKIP_AUTH=true in .env
- [ ] T2T_HOST=0.0.0.0 in .env (for remote access)
- [ ] All ports configured (5001, 5002, 8050, 8051)

**Services:**
- [ ] All 4 services start without errors
- [ ] No port conflicts
- [ ] Can access URLs from browser

**Annotation Interface (port 8050):**
- [ ] Page loads
- [ ] Email input works
- [ ] Entity dropdown shows 9 options
- [ ] Relation dropdown shows 15 options
- [ ] "Add tuple" button works
- [ ] Can save annotations

**Admin Panel (port 8051):**
- [ ] Bypasses login page (goes straight to admin interface)
- [ ] Can create projects
- [ ] Can add papers to projects
- [ ] Can view all tuples

## What to Report If Issues Persist

If dropdowns or other features still don't work, please provide:

1. **Browser console errors:**
   - Open browser dev tools (F12)
   - Check Console tab
   - Copy any red errors

2. **Backend logs:**
   - Check terminal where services are running
   - Look for errors when accessing pages
   - Especially check for `/api/choices` requests

3. **Database verification:**
   ```bash
   python3 debug_dropdowns.py
   ```
   - Copy the full output

4. **Configuration check:**
   ```bash
   cat .env | grep -E "T2T_SKIP_AUTH|T2T_HOST|T2T_.*PORT"
   ```

5. **Service status:**
   ```bash
   ps aux | grep python3 | grep t2t
   ss -tulpn | grep -E "5001|5002|8050|8051"
   ```

## Files Modified

### Backend
- `t2t_admin_be.py` - Added skip auth support + database commits
- `t2t_store.py` - Fixed datetime handling
- `create_admin.py` - Fixed datetime handling

### Frontend
- `t2t_admin_fe.py` - Added skip auth support

### Configuration
- `.env` - Added `T2T_SKIP_AUTH=true`
- `.env.example` - Added skip auth documentation

### Database
- `t2t.db` - Properly loaded 124KB SQLite database with all entity/relation types

## Next Steps

Once you verify the annotation interface and admin panel work:

1. **For production use:**
   - Set `T2T_SKIP_AUTH=false` in `.env`
   - Create admin accounts: `python3 create_admin.py email@example.com`
   - Test login with password

2. **For continued development:**
   - Keep `T2T_SKIP_AUTH=true` for easy testing
   - Focus on annotation workflow
   - Add more features as needed

## Summary

The system is now configured for **passwordless debugging mode** with:
- ✅ Skip authentication enabled
- ✅ Database properly loaded with all entity/relation types
- ✅ All database commits working
- ✅ Timezone-aware datetime handling
- ✅ All services ready to start

**Key URLs:**
- Annotation: http://localhost:8050
- Admin: http://localhost:8051 (no login required in dev mode)

Test the system and report back with any specific errors you encounter!
