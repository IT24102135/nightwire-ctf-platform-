FROM ctfd/ctfd:latest

# Fix the init_plugins import error
RUN python3 << 'EOF'
import os
file_path = '/opt/CTFd/CTFd/__init__.py'
with open(file_path, 'r') as f:
    lines = f.readlines()
new_lines = []
for line in lines:
    if 'from CTFd.plugins import init_plugins' in line:
        new_lines.append('# ' + line)
    elif 'init_plugins(app)' in line and not line.strip().startswith('#'):
        new_lines.append('# ' + line)
    else:
        new_lines.append(line)
with open(file_path, 'w') as f:
    f.writelines(new_lines)
print("✓ Patched init_plugins")
EOF

# Copy initialization script
COPY init_db.py /opt/init_db.py

# Create entrypoint
RUN cat > /opt/entrypoint.sh << 'SCRIPT'
#!/bin/bash
set -e
echo "[ENTRYPOINT] Starting CTFd..."
python -m gunicorn.__main__ --bind 0.0.0.0:8000 --workers 4 'CTFd:create_app()' &
GUNICORN_PID=$!

echo "[ENTRYPOINT] Waiting for CTFd..."
for i in {1..60}; do
    if curl -s http://localhost:8000 > /dev/null 2>&1; then
        echo "[ENTRYPOINT] ✓ CTFd ready"
        break
    fi
    sleep 1
done

echo "[ENTRYPOINT] Running initialization..."
cd /opt/CTFd
python /opt/init_db.py

wait $GUNICORN_PID
SCRIPT
RUN chmod +x /opt/entrypoint.sh

ENTRYPOINT ["/opt/entrypoint.sh"]
