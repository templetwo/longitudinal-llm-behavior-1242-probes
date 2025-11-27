#!/usr/bin/env bash
file="$1"
if [ ! -f "$file" ]; then echo "file not found"; exit 1; fi
content=$(cat "$file")
echo "=== START: RAW RESPONSE ==="
echo "$content" | sed -n '1,200p'
echo; echo "=== SUMMARY BLOCK (if present) ==="
echo "$content" | awk '/^Summary/ {p=1; next} /^$/ && p{exit} p{print}'
