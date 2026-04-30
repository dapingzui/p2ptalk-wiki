#!/usr/bin/env python3
import subprocess
result = subprocess.run(
    ['/Users/ice/Document/QuantaAlpha/.venv/bin/python', 'scripts/quant_scan.py', '--save', '--workers', '16'],
    cwd='/Users/ice/Document/QuantaAlpha',
    capture_output=True, text=True, timeout=600
)
print(result.stdout[-8000:] if len(result.stdout) > 8000 else result.stdout)
print(result.stderr[-2000:] if result.stderr else '')
