#!/usr/bin/env bash
# ==============================================================================
# Daily Automated Backup Script for Vishwaguru Billing (PostgreSQL)
# ==============================================================================
# Usage:
#   chmod +x backup.sh
#   Add to crontab: 0 2 * * * /home/ubuntu/vishwaguru-billing/deploy/backup.sh
# ==============================================================================

set -euo pipefail

BACKUP_DIR="/home/ubuntu/backups/vishwaguru-billing"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DB_NAME="vishwaguru_billing"
DB_USER="postgres"
RETENTION_DAYS=30

mkdir -p "${BACKUP_DIR}"

echo "[$(date)] Starting database backup..."
BACKUP_FILE="${BACKUP_DIR}/${DB_NAME}_${TIMESTAMP}.sql.gz"

# Dump and compress database
pg_dump -U "${DB_USER}" -d "${DB_NAME}" | gzip > "${BACKUP_FILE}"

echo "[$(date)] Backup completed: ${BACKUP_FILE} ($(du -h "${BACKUP_FILE}" | cut -f1))"

# Delete backups older than RETENTION_DAYS
find "${BACKUP_DIR}" -type f -name "*.sql.gz" -mtime +"${RETENTION_DAYS}" -exec rm {} \;
echo "[$(date)] Cleaned backups older than ${RETENTION_DAYS} days."
