#!/bin/bash

MAIL="your-email@example.com" # Replace this with a placeholder email address or environment variable

SUBJECT="Daily Logs (Last 24h) from $(hostname)"
LOGFILE="/tmp/startup-logs.txt"
STAMPFILE="/var/log/daily-log-sent.date"
TODAY=$(date +%F)

# Check if already sent today
if [ -f "$STAMPFILE" ] && grep -q "$TODAY" "$STAMPFILE"; then
  exit 0
fi

# Generate filtered critical logs only
{
  echo "Host: $(hostname)"
  echo "Date: $(date)"
  echo "----------------------------------------"
  echo "Critical system logs (last 24 hours):"
  echo

  # Extract logs with levels: emerg, alert, crit, err
  journalctl --since "24 hours ago" -p 0..3

  # Additional keywords that may not be marked as critical
  echo
  echo "Detected keywords (watchdog, soft lockup, panic, BUG, segfault):"
  echo
  journalctl --since "24 hours ago" | grep -iE "watchdog|soft lockup|BUG|panic|segfault"

} > "$LOGFILE"

# Send the email
mail -s "$SUBJECT" "$EMAIL" < "$LOGFILE"

# Save the date to prevent repeat emails
echo "$TODAY" > "$STAMPFILE"

# Clean up
rm -f "$LOGFILE"
