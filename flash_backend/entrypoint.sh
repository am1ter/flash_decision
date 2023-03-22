# Apply db migrations
flask db upgrade
# Run webserver
xvfb-run -a --server-args="-screen 0 1280x800x24 -ac -nolisten tcp -dpi 96 +extension RANDR" python3 "flash_backend.py" --no-sandbox --disable-gpu --disable-setuid-sandbox