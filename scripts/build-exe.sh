#!/usr/bin/env sh
set -eu

python -m PyInstaller --onefile --name oopsql scripts/oopsql_cli.py

