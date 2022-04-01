# Apply db migrations
flask db upgrade
# Create default user
python3 -c "import app.models as md;md.create_system_users()"
# Run webserver
python3 "flash_decision.py"