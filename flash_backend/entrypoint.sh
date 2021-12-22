# Go to backend folder
cd /flash_backend/
# Use db migrations
flask db upgrade
# Create default user
python3 -c "import app.models as md;md.create_def_user()"
# Run webserver
python3 "flash_decision.py"