#!/bin/bash
# ---------------------------------------------
# FrancoUke Django Backup Script
# ---------------------------------------------
# This script creates a timestamped JSON dump of
# your important Django app data, stores it in
# a local backup folder, and keeps only the last 5 backups.
# ---------------------------------------------

# Location of your Django project
PROJECT_DIR="/Users/danielgaulin/Documents/Projects/FrancoUke"

# Location of your virtual environment's python
VENV_PYTHON="/Users/danielgaulin/Documents/Projects/francouke-venv/bin/python"

# Backup destination
BACKUP_DIR="$PROJECT_DIR/backups"
mkdir -p "$BACKUP_DIR"

# Timestamp
DATE=$(date +"%Y-%m-%d_%H-%M-%S")

# Output file name
BACKUP_FILE="$BACKUP_DIR/full_data_$DATE.json"

echo "📦 Starting FrancoUke backup at $DATE"
cd "$PROJECT_DIR" || exit

# Activate foreign key-friendly dump
"$VENV_PYTHON" manage.py dumpdata \
  users songbook setlists board \
  --indent 2 > "$BACKUP_FILE"

if [ $? -eq 0 ]; then
  echo "✅ Backup successful: $BACKUP_FILE"
else
  echo "❌ Backup failed!"
  exit 1
fi

# Keep only the 5 most recent backups
BACKUP_COUNT=$(ls -1t "$BACKUP_DIR"/*.json 2>/dev/null | wc -l | tr -d ' ')
if [ "$BACKUP_COUNT" -gt 5 ]; then
  echo "🧹 Cleaning up old backups..."
  ls -1t "$BACKUP_DIR"/*.json | tail -n +6 | xargs rm --
fi

echo "✨ Done! Backup folder: $BACKUP_DIR"

