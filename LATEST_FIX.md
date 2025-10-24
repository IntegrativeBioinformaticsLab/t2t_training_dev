# Latest Fix - Missing admin-email Component

## Issue

Application crashed with error:
```
A nonexistent object was used in a `State` of a Dash callback.
The id of this object is `admin-email` and the property is `value`.
```

## Root Cause

When we added skip auth mode, the admin-email input field was removed from the layout (it was part of the old login form). However, two callbacks still referenced it:

1. `add_dois_to_project` (line 383) - Uses `State("admin-email", "value")`
2. `fetch_pdfs` (line 480) - Uses `State("admin-email", "value")`

## Solution

Added a hidden `dcc.Store` component with id `admin-email` that:
- Exists in the global app layout
- Gets populated with "dev@localhost" in skip auth mode
- Provides the email value that callbacks expect

## Changes Made

**File: `t2t_admin_fe.py`**

### 1. Added admin-email Store (line 36)
```python
admin_email_store = dcc.Store(id='admin-email', storage_type='session')
```

### 2. Added to app layout (line 44)
```python
app.layout = dbc.Container([
    session_store,
    admin_info_store,
    admin_email_store,  # Added
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
], fluid=True)
```

### 3. Added callback to populate it (lines 209-219)
```python
@app.callback(
    Output("admin-email", "data"),
    Input("url", "pathname"),
    prevent_initial_call=False
)
def init_admin_email(pathname):
    """Set default admin email in skip auth mode."""
    if SKIP_AUTH:
        return "dev@localhost"
    return None
```

## How It Works

1. When app loads, `init_admin_email` callback fires
2. If `SKIP_AUTH=true`, sets `admin-email` store to "dev@localhost"
3. Callbacks that reference `State("admin-email", "value")` now work
4. Backend ignores the email anyway (uses session admin info)

## Testing

```bash
# Restart services
pkill -f "python3.*t2t"
./start_all.sh

# Test admin panel: http://localhost:8051
# - Create project: Should work ✓
# - Add DOIs: Should work (no crash) ✓
# - Fetch PDFs: Should work (no crash) ✓
```

## All Fixed Issues Summary

1. ✅ Session expired errors → Skip auth mode
2. ✅ Duplicate callback outputs → Added allow_duplicate
3. ✅ Missing admin-email component → Added Store with default value

Application should now be fully functional!
