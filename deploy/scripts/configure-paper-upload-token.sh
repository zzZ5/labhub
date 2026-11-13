#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
HASH="${1:-}"
if [[ ! "$HASH" =~ ^[a-f0-9]{64}$ ]]; then
  echo "Usage: bash deploy/scripts/configure-paper-upload-token.sh <SHA256 hash, not the raw token>" >&2
  exit 2
fi
test -f .env || { echo "Existing production .env required" >&2; exit 2; }
python3 - "$HASH" <<'PY'
import os
import sys
from pathlib import Path

path = Path('.env')
lines = path.read_text(encoding='utf-8').splitlines()
key = 'LABHUB_PAPER_UPLOAD_TOKEN_SHA256='
lines = [line for line in lines if not line.lstrip().startswith(key)]
lines.append(key + sys.argv[1])
temporary = path.with_name('.env.paper-upload.tmp')
temporary.write_text('\n'.join(lines) + '\n', encoding='utf-8')
os.chmod(temporary, path.stat().st_mode & 0o777)
os.replace(temporary, path)
PY
docker compose -f docker-compose.prod.yml up -d --build --no-deps backend
echo "Paper-upload credential configured. Run the authorized client sync and verify API readback."
