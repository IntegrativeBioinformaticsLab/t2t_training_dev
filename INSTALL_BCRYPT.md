# Installing bcrypt

You need to install the `bcrypt` package to use the admin authentication system.

## If you're using Poetry (Recommended)

Since your error showed a Poetry virtualenv path, you're likely using Poetry:

```bash
# Navigate to project directory
cd /home/mds207/t2t/t2t_training_dev

# Activate the virtualenv (if not already active)
poetry shell

# Install bcrypt
poetry add bcrypt

# Or if you just want to install without adding to pyproject.toml
poetry run pip install bcrypt
```

## If you're using pip

```bash
# If you have a virtualenv, activate it first
source venv/bin/activate  # or wherever your virtualenv is

# Install bcrypt
pip install bcrypt
# or
pip3 install bcrypt
# or
python3 -m pip install bcrypt
```

## If you're using system Python

```bash
# Install for your user
pip install --user bcrypt
# or
pip3 install --user bcrypt
```

## After Installing

Try creating the admin account again:

```bash
python3 create_admin.py M.D.Sharma@exeter.ac.uk --name "Dr. Sharma"
```

## Verify Installation

To check if bcrypt is installed:

```bash
python3 -c "import bcrypt; print('bcrypt installed:', bcrypt.__version__)"
```

Should output: `bcrypt installed: 4.x.x`

## Troubleshooting

### "No module named pip"
Your Python installation doesn't have pip. Install it:
```bash
# Ubuntu/Debian
sudo apt-get install python3-pip

# macOS
python3 -m ensurepip
```

### "Permission denied"
Use `--user` flag:
```bash
pip install --user bcrypt
```

### Still having issues?
Check which Python you're using:
```bash
which python3
python3 --version
```

Make sure you're installing to the same Python environment that runs your scripts.
