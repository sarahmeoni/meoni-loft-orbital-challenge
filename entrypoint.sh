#!/usr/bin/env bash
#
# entrypoint.sh
#
# Start the satellite-lighting service. Arguments are passed through to the CLI,
# e.g. --config /app/config.json.
#
set -euo pipefail

exec python main.py "$@"
