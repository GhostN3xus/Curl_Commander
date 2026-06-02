#!/usr/bin/env bash
set -e

pip install -e ".[dev]" --break-system-packages

echo "[✓] curlcmd installed. Run: curlcmd"
