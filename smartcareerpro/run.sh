#!/usr/bin/env bash
# Start SmartCareerPro
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

if [ -z "${ZHIPU_API_KEY:-}" ]; then
  echo "⚠️  ZHIPU_API_KEY is not set."
  echo "   Get your key at https://bigmodel.cn/usercenter/proj-mgmt/apikeys"
  echo "   Then run: export ZHIPU_API_KEY=your_key"
  exit 1
fi

cd "$ROOT_DIR"
pip install -q -r smartcareerpro/requirements.txt

echo "🚀 Starting SmartCareerPro on http://localhost:${PORT:-8080}"
python -m smartcareerpro.main
