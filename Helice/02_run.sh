#!/usr/bin/env bash
# Lance mesh + solve pour les 3 variantes de turbulence (case_kEpsilon, case_kOmegaSST, case_laminar).
set -euo pipefail

: "${WM_PROJECT_DIR:?OpenFOAM non chargé — source /usr/lib/openfoam/openfoam2412/etc/bashrc}"

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CASES=(case_kEpsilon case_kOmegaSST case_laminar)

for c in "${CASES[@]}"; do
    echo "=== $c : Allrun.pre (mesh) ==="
    (cd "$DIR/$c" && ./Allrun.pre)
    echo "=== $c : Allrun (solve) ==="
    (cd "$DIR/$c" && ./Allrun)
done

echo "Terminé. Sorties propellerInfo dans <case>/postProcessing/propellerInfo1/"
