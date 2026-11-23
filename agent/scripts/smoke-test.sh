#!/bin/sh
set -eu
PROJECT_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
CLI="$PROJECT_ROOT/agent/bin/deepfos-agent"

check() {
  label=$1
  shift
  output=$("$CLI" "$@" --json)
  LABEL="$label" python3 -c '
import json, os, sys
payload = json.load(sys.stdin)
label = os.environ["LABEL"]
if not payload.get("ok"):
    raise SystemExit("%s failed: %s" % (label, payload.get("error")))
print("%s: ok" % label)
' <<EOF
$output
EOF
}

check "describe" describe
check "doctor" doctor
check "docs" docs "财务模型 保存" --limit 2
check "symbols" symbols "AsyncFinancialCube.query" --limit 2
check "source" source "class AsyncFinancialCube" --limit 3
check "review" review
echo "Smoke test passed"
