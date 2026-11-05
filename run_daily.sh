#!/bin/zsh
# Runs the Secretary once: organizes new inbox emails from the last 7 days.
# Called every morning by launchd (see com.secretary.daily.plist). Output goes to logs/daily.log.
cd "$(dirname "$0")" || exit 1
mkdir -p logs
{
  echo "===== $(date '+%Y-%m-%d %H:%M') ====="
  .venv/bin/python main.py --gmail -n 50
} >> logs/daily.log 2>&1
