#!/bin/bash

echo "🚀 YakMate Auto-Deploy & Backup Engine Started"
echo "Interval: 20 minutes"

while true; do
  echo "------------------------------------------------"
  echo "⏰ Current Time: $(date)"
  
  # 1. Local Backup (Git)
  echo "📦 Backing up code locally..."
  git add .
  git commit -m "Auto-backup: $(date)"
  
  # 2. Remote Upload (Firebase)
  echo "☁️ Uploading to Firebase Hosting..."
  npx firebase deploy --only hosting --non-interactive
  
  if [ $? -eq 0 ]; then
    echo "✅ Success: Code is safe and live!"
  else
    echo "❌ Error: Deployment failed. Please check your internet or Firebase login."
  fi
  
  echo "💤 Sleeping for 20 minutes..."
  sleep 1200
done
