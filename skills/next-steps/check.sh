#!/usr/bin/env bash
# Run each step's status check and print what it showed, so every status on a
# next-steps page rests on a real result.
# Usage: check.sh CHECKS.tsv      (lines: <step-id><TAB><command>; # comments ok)
# Output, per step: id, exit code, time, first 5 lines of output.
# Checks must be read-only. Never put sudo, installs, purchases or writes here.
set -u
f="${1:?usage: check.sh CHECKS.tsv}"
while IFS=$'\t' read -r id cmd; do
  [[ -z "${id// }" || "$id" == \#* ]] && continue
  out=$(timeout 20 bash -c "$cmd" </dev/null 2>&1); rc=$?
  printf '== %s  exit=%s  at=%s\n$ %s\n' "$id" "$rc" "$(date '+%Y-%m-%d %H:%M')" "$cmd"
  printf '%s\n' "$out" | head -5
  [[ $(printf '%s\n' "$out" | wc -l) -gt 5 ]] && echo "... (more lines cut)"
  [[ $rc -eq 124 ]] && echo "(timed out after 20 s: status unknown)"
done < "$f"
exit 0
