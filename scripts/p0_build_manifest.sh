#!/usr/bin/env bash
# p0_build_manifest.sh — build or verify 00_source/MANIFEST.sha256
#
# Usage (run from the repository root):
#   scripts/p0_build_manifest.sh          # build: add new files, refuse if any recorded file changed
#   scripts/p0_build_manifest.sh --check  # verify only: exit 1 on any mismatch, missing, or unrecorded file
#
# Scope: every file under 00_source/ except documentation and repo plumbing:
#   *.md (register, unavailability notes), .gitkeep, MANIFEST.sha256 itself.
#
# Immutability (GOVERNANCE D1): a recorded file whose hash has changed is a hard
# failure in both modes. The script never rewrites an existing entry.

set -euo pipefail

SRC_DIR="00_source"
MANIFEST="$SRC_DIR/MANIFEST.sha256"
MODE="${1:-build}"

if [[ ! -d "$SRC_DIR" ]]; then
  echo "ERROR: run from repository root ($SRC_DIR/ not found)" >&2
  exit 2
fi
case "$MODE" in build|--check) ;; *) echo "ERROR: unknown argument '$MODE'" >&2; exit 2 ;; esac

# Current evidence files, sorted, NUL-safe.
mapfile -d '' FILES < <(find "$SRC_DIR" -type f \
  ! -name '*.md' ! -name '.gitkeep' ! -name 'MANIFEST.sha256' -print0 | sort -z)

declare -A RECORDED=()
if [[ -f "$MANIFEST" ]]; then
  while IFS= read -r line; do
    [[ -z "$line" ]] && continue
    hash="${line%%  *}"; path="${line#*  }"
    RECORDED["$path"]="$hash"
  done < "$MANIFEST"
fi

fail=0
new_entries=()

# 1. Every recorded file must still exist with the same hash.
for path in "${!RECORDED[@]}"; do
  if [[ ! -f "$path" ]]; then
    echo "MISSING   $path"; fail=1; continue
  fi
  actual="$(sha256sum "$path" | cut -d' ' -f1)"
  if [[ "$actual" != "${RECORDED[$path]}" ]]; then
    echo "CHANGED   $path"; fail=1
  else
    echo "OK        $path"
  fi
done

# 2. Files on disk that are not yet recorded.
for path in "${FILES[@]}"; do
  [[ -n "${RECORDED[$path]+x}" ]] && continue
  if [[ "$MODE" == "--check" ]]; then
    echo "UNRECORDED $path"; fail=1
  else
    new_entries+=("$(sha256sum "$path")")
    echo "ADDED     $path"
  fi
done

if [[ $fail -ne 0 ]]; then
  echo "RESULT: FAIL — source integrity violated or manifest incomplete. Nothing written." >&2
  exit 1
fi

if [[ "$MODE" == "build" && ${#new_entries[@]} -gt 0 ]]; then
  { [[ -f "$MANIFEST" ]] && cat "$MANIFEST"; printf '%s\n' "${new_entries[@]}"; } \
    | sort -k2 > "$MANIFEST.tmp"
  mv "$MANIFEST.tmp" "$MANIFEST"
fi

total=$(( ${#RECORDED[@]} + ${#new_entries[@]} ))
echo "RESULT: PASS — $total file(s) covered (${#new_entries[@]} added)."
