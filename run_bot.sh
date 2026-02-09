#!/bin/bash
export PATH=$PATH:~/.npm-global/bin
pm2 delete clawdbot 2>/dev/null
pm2 delete hive-mind 2>/dev/null
pm2 start director.py --name "hive-mind" --interpreter python3
echo "✅ Hive Mind Deployed!"
