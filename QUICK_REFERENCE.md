# Quick Reference - Session & Callback Fixes

## Issues Fixed

### ✅ 1. "Session expired" Error in Skip Auth Mode

**What was wrong:** Creating projects showed "Session expired. Please log in again." even with `T2T_SKIP_AUTH=true`.

**What was fixed:**
- Admin frontend now skips session validation when `SKIP_AUTH=true`
- Sends dummy "dev-token" instead of checking localStorage
- File: `t2t_admin_fe.py` (create_project callback)

### ✅ 2. Duplicate Callback Outputs

**What was wrong:** Browser console showed "Duplicate callback outputs" errors.

**What was fixed:** Added `allow_duplicate=True` to duplicate outputs:
- `pdf-viewer.src`
- `pdf-viewer.style`
- `btn-copy-pdf-text.style`
- `pdf-status.children`
- `literature-link.value`

File: `t2t_training_fe.py` (lines 537, 580-582, 960)

## Quick Test

```bash
# Stop and restart
pkill -f "python3.*t2t"
./start_all.sh

# Test admin (port 8051)
# - Create project: Should work without "Session expired"

# Test annotation (port 8050)
# - Open browser console (F12)
# - Should have NO "Duplicate callback outputs" errors
# - Dropdowns should work
```

## What to Check

**Admin Panel (http://localhost:8051):**
- ✅ Loads without login
- ✅ Can create projects
- ✅ No "Session expired" errors

**Annotation Interface (http://localhost:8050):**
- ✅ Clean browser console
- ✅ Entity/relation dropdowns work
- ✅ Add tuple works
- ✅ Save works

## If Issues Persist

**Session errors:**
```bash
grep T2T_SKIP_AUTH .env  # Should be: true
pkill -f "python3.*t2t" && ./start_all.sh
```

**Callback errors:**
```bash
grep "allow_duplicate=True" t2t_training_fe.py | wc -l
# Should show 6+ lines
```

See `CURRENT_STATUS.md` for complete setup guide.
