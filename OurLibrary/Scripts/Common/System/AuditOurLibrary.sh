#!/usr/bin/env bash
# File: AuditOurLibrary.sh
# Path: OurLibrary/Scripts/Common/System/AuditOurLibrary.sh
# Standard: AIDEV-PascalCase-2.3
# Created: 2025-08-25
# Last Modified: 2025-08-25  01:00PM
# Symlink Pattern: PROJECT_TOOL
#
# Description: Occasional, manual audit export of Firebase Auth + Firestore.
# Requires: firebase-tools, jq; active project our-library-d7b60.

set -euo pipefail

cd "$(pwd)"  # PROJECT_TOOL: operate where invoked
DATE="$(date +%Y%m%d_%H%M%S)"
OUT="audits/${DATE}"
mkdir -p "${OUT}"

echo "🔐 Exporting Firebase Auth users → ${OUT}/users.json"
firebase auth:export "${OUT}/users.json" --project our-library-d7b60

echo "🗄️  Exporting Firestore → ${OUT}/firestore"
firebase firestore:export "${OUT}/firestore" --project our-library-d7b60

echo "🧾 Writing summary"
{
  echo "Audit Summary - $(date -Iseconds)"
  echo "Users: $(jq '.users | length' < "${OUT}/users.json" 2>/dev/null || echo 'n/a')"
  echo "Collections: $(find "${OUT}/firestore" -name '*.export_metadata' | wc -l | tr -d ' ')"
} > "${OUT}/audit-summary.txt"

tar -czf "ourlibrary-audit-${DATE}.tar.gz" -C audits "${DATE}"
echo "✅ Audit bundle: ourlibrary-audit-${DATE}.tar.gz"