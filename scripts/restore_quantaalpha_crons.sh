#!/bin/bash
(crontab -l 2>/dev/null; echo "0 * * * * /Users/ice/Document/QuantaAlpha/scripts/research_director.sh"; echo "0 22 * * * /Users/ice/Document/QuantaAlpha/daily_sync_cron.sh"; echo "0 8 * * * /Users/ice/Document/QuantaAlpha/scripts/run_ercot.sh") | crontab -
