#!/usr/bin/env bash
# Séquence de nuit MRF du 20/09 : RUN A (nombre d'itérations) puis RUN B (schémas alignés). Critères et prévisions écrits AVANT :
#   ENSM-Enseignement/_Reserve/comparaison-3-modeles/NUIT_serie_A-B_critere.md
# Le script écrit lui-même son état dans Helice/_ETAT_SERIE.txt ; il n'y a AUCUN gardien détaché : il attend son propre run par PID
# (kill -0) et se termine avec lui. Arrêts : espace libre de l'hôte < 15 Go, code de retour != 0 (un run qui échoue n'enchaîne pas le
# suivant), durée maximale dépassée.
# Usage : bash Helice/scripts/serie_nuit_MRF.sh            (lance la série)
#         SERIE_MODE=prep bash Helice/scripts/serie_nuit_MRF.sh   (prépare les cas A seulement, sans rien lancer)
set -o pipefail
HELICE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ETAT="$HELICE/_ETAT_SERIE.txt"
SEUIL_GO=15
LIM_A=7200
LIM_B=5400
SRC="$HELICE/case_kEpsilon_MRF"
source /usr/lib/openfoam/openfoam2412/etc/bashrc >/dev/null 2>&1   # avant `set -u` : le bashrc d'OpenFOAM lit des variables non définies
set -u

libre_go() { df -BG --output=avail /mnt/c | tail -1 | tr -dc '0-9'; }
ecrire()   { printf '%s | libre %s Go | %s | %s\n' "$(date '+%F %T')" "$(libre_go)" "$1" "${2:-}" >> "$ETAT"; }
dernier_temps() { ls "$1/processor0" | grep -E '^[0-9]+$' | sort -n | tail -1; }
residu_p() { grep -E "Solving for p," "$1" 2>/dev/null | tail -1 | sed -E 's/.*Initial residual = ([0-9.e+-]+),.*/\1/'; }
moyennes() { # dossier temps_de_depart -> "K_T 10K_Q eta0 (200 dernières itérations)"
    awk '!/^#/ && NF>=7 {a[NR]=$5; b[NR]=$6; c[NR]=$7; n=NR} END{s1=s2=s3=0; k=0; for(i=n-199;i<=n;i++){s1+=a[i];s2+=b[i];s3+=c[i];k++} printf "K_T %.5f  10K_Q %.5f  eta0 %.5f  (%d dernières itérations)", s1/k, s2/k, s3/k, k}' \
        "$1/postProcessing/propellerInfo1/$2/propellerPerformance.dat"
}

preparer_A() {
    local D="$HELICE/case_kEpsilon_MRF_A" p
    rm -rf "$D"; mkdir -p "$D"
    cp -r "$SRC/constant" "$SRC/system" "$D/"
    for p in 0 1 2 3 4 5 6 7; do mkdir -p "$D/processor$p"; cp -r "$SRC/processor$p/1500" "$SRC/processor$p/constant" "$D/processor$p/"; done
    sed -i 's/^startTime .*/startTime       1500;/; s/^endTime .*/endTime         6000;/; s/^writeInterval .*/writeInterval   1500;/' "$D/system/controlDict"
    sed -i 's/^    consistent      yes;/    consistent      yes;\n    residualControl { p 1e-4; U 1e-4; "(k|epsilon)" 1e-4; }/' "$D/system/fvSolution"
}

preparer_B() { # depuis l'état final de A
    local A="$HELICE/case_kEpsilon_MRF_A" D="$HELICE/case_kEpsilon_MRF_B" p tA
    tA=$(dernier_temps "$A"); [ -n "$tA" ] || return 1
    rm -rf "$D"; mkdir -p "$D"
    cp -r "$A/constant" "$A/system" "$D/"
    for p in 0 1 2 3 4 5 6 7; do mkdir -p "$D/processor$p"; cp -r "$A/processor$p/$tA" "$A/processor$p/constant" "$D/processor$p/"; done
    sed -i "s/^startTime .*/startTime       $tA;/; s/^endTime .*/endTime         $((tA + 2000));/; s/^writeInterval .*/writeInterval   1000;/" "$D/system/controlDict"
    sed -i 's/bounded Gauss/Gauss/g' "$D/system/fvSchemes"
    echo "$tA"
}

lancer() { # nom dossier duree_max_s temps_de_depart
    local nom="$1" dir="$2" lim="$3" t0dir="$4" pid rc t0 dernier=0 it
    ( cd "$dir" || exit 90; exec mpirun -np 8 simpleFoam -parallel > log.simpleFoam 2>&1 ) &
    pid=$!
    echo "$pid" > "$dir/_PID"
    ecrire "$nom DÉMARRÉ" "PID $pid, durée max ${lim}s"
    t0=$(date +%s)
    while kill -0 "$pid" 2>/dev/null; do
        sleep 30
        if [ "$(libre_go)" -lt "$SEUIL_GO" ]; then
            ecrire "$nom ARRÊT : espace libre < ${SEUIL_GO} Go" "kill $pid"; kill "$pid" 2>/dev/null; wait "$pid" 2>/dev/null; return 91
        fi
        if [ $(( $(date +%s) - t0 )) -gt "$lim" ]; then
            ecrire "$nom ARRÊT : durée max ${lim}s dépassée" "kill $pid"; kill "$pid" 2>/dev/null; wait "$pid" 2>/dev/null; return 92
        fi
        if [ $(( $(date +%s) - dernier )) -ge 300 ]; then
            dernier=$(date +%s); it=$(grep -c '^Time = ' "$dir/log.simpleFoam")
            ecrire "$nom en cours" "PID $pid, itérations $it, dernier résidu p $(residu_p "$dir/log.simpleFoam")"
        fi
    done
    wait "$pid"; rc=$?
    ecrire "$nom TERMINÉ rc=$rc" "$(grep -m1 'SIMPLE solution converged' "$dir/log.simpleFoam" || echo 'pas de critère de convergence atteint (endTime)') ; $(moyennes "$dir" "$t0dir")"
    return "$rc"
}

: > "$ETAT"
ecrire "SÉRIE DÉMARRÉE" "script PID $$ ; critères : NUIT_serie_A-B_critere.md"
bash "$HELICE/../_Setup/outils/preflight.sh" >> "$ETAT" 2>&1 || { ecrire "ARRÊT : pré-vol INV-23 non vert" ""; exit 1; }
preparer_A || { ecrire "ARRÊT : préparation de A impossible" ""; exit 1; }
[ "${SERIE_MODE:-}" = "prep" ] && { ecrire "PRÉPARATION SEULE faite" "A prêt, rien lancé"; exit 0; }
lancer "RUN A (nombre d'itérations)" "$HELICE/case_kEpsilon_MRF_A" "$LIM_A" 1500 || { ecrire "SÉRIE ARRÊTÉE après A (rc≠0)" ""; exit 2; }
tA=$(preparer_B) || { ecrire "ARRÊT : préparation de B impossible" ""; exit 3; }
lancer "RUN B (schémas alignés, départ t=$tA)" "$HELICE/case_kEpsilon_MRF_B" "$LIM_B" "$tA" || { ecrire "SÉRIE ARRÊTÉE après B (rc≠0)" ""; exit 4; }
ecrire "SÉRIE TERMINÉE" "A et B terminés ; comparer avec case_kEpsilon_MRF (K_T 0,21398 ; 10K_Q 0,54145)"
