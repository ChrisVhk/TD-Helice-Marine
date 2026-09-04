#!/usr/bin/env bash
# Nettoie les 3 cas (Allclean natif + reconstruction/décomposition).
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CASES=(case_kEpsilon case_kOmegaSST case_laminar)

for c in "${CASES[@]}"; do
    echo "=== $c : Allclean ==="
    (cd "$DIR/$c" && ./Allclean)
done
