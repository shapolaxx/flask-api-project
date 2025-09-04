#!/bin/bash

BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/backup_$DATE.sql"

pg_dump -h db -U user -d flask_db -F c -b -v -f "$BACKUP_FILE"


if [ $? -eq 0 ]; then
    echo "Backup successful: $BACKUP_FILE"
    
    
    ls -t $BACKUP_DIR/backup_*.sql | tail -n +8 | xargs rm -f
else
    echo "Backup failed!"
    exit 1
fi