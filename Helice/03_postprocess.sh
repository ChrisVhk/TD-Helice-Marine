#!/usr/bin/env bash
# Compare KT/KQ/eta0 entre les 3 modèles de turbulence après 02_run.sh.
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "$DIR/scripts/compare_turbulence.py" "$DIR"
