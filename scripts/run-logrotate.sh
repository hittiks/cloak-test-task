#!/usr/bin/env sh
set -eu

# Usage:
#   sh /scripts/run-logrotate.sh prismal-backend
#
# Required mounts:
#   /config/<name>  -> logrotate config file (can be non-root owner)
#   /logs           -> logs directory
#   /var/lib/logrotate -> persistent state dir (volume)
#

NAME="${1:-prismal-backend}"

SLEEP_SECONDS="${LOGROTATE_SLEEP_SECONDS:-1800}"

CONFIG_SRC="/config/${NAME}"
CONFIG_DST="/etc/logrotate.d/${NAME}"
STATE_FILE="/var/lib/logrotate/${NAME}.status"

apk add --no-cache logrotate >/dev/null

if [ ! -f "${CONFIG_SRC}" ]; then
  echo "ERROR: config not found: ${CONFIG_SRC}" >&2
  exit 2
fi

# logrotate security requirements:
# - config must be owned by root (uid 0)
# - config must not be writable by group/others
cp "${CONFIG_SRC}" "${CONFIG_DST}"
chown root:root "${CONFIG_DST}"
chmod 0644 "${CONFIG_DST}"

# Best-effort: ensure expected dirs exist (containers write as uid/gid 999:999)
mkdir -p /logs/app
chown -R 999:999 /logs/app 2>/dev/null || true

echo "logrotate service started: name=${NAME} sleep=${SLEEP_SECONDS}s"

while true; do
  echo "[$(date -Iseconds)] logrotate run (sleep=${SLEEP_SECONDS}s)"
  logrotate -v -s "${STATE_FILE}" "${CONFIG_DST}" || true
  sleep "${SLEEP_SECONDS}"
done
