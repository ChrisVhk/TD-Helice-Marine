#!/usr/bin/env bash
# reprise_cas.sh — reprend UN cas OpenFOAM parallèle interrompu, jusqu'à son endTime.
#
#   Usage :  scripts/reprise_cas.sh <nom_du_cas>        (ex. case_kOmegaSST)
#
# Enchaîne, dans l'ordre :
#   1. pré-vol du disque HÔTE (/mnt/c) — BLOQUE sous 15 Go (seuil nommé dans le message) ;
#      c'est le disque hôte plein, pas l'OOM, qui a tué case_kOmegaSST les 05-06/09,
#      et `df /` ment (VHD ext4 énorme) : on ne regarde que /mnt/c ;
#   2. garde-fou : REFUSE de toucher un cas déjà terminé (log `End` + latestTime == endTime) —
#      protège case_kEpsilon et case_laminar ;
#   3. évacue les pas de temps à 0 octet vers _corrupt_backup/<cas>/ sur TOUS les processeurs,
#      et dit lesquels ;
#   4. pimpleFoam -parallel depuis latestTime jusqu'à endTime ;
#   5. reconstructPar -newTimes.
# Log horodaté : <cas>/log.reprise_<AAAAMMJJ-HHMMSS>
#
# Aucun nom de cas en dur. Remplace _resume_kOmegaSST.sh (qui était gitignoré — INV-11 :
# l'outil qui produit un tiers des résultats doit être versionné).
set -o pipefail

SEUIL_BLOQUANT_GO=15

die() { echo "ERREUR : $*" >&2; exit 1; }

CAS="${1:?Usage: $0 <nom_du_cas>  (ex. case_kOmegaSST)}"
HELICE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CASE_DIR="$HELICE/$CAS"

if [ -z "${WM_PROJECT_DIR:-}" ]; then
  BASHRC=/usr/lib/openfoam/openfoam2412/etc/bashrc
  # shellcheck disable=SC1090
  [ -f "$BASHRC" ] && source "$BASHRC"
fi
: "${WM_PROJECT_DIR:?OpenFOAM non chargé et bashrc introuvable — source /usr/lib/openfoam/openfoam2412/etc/bashrc}"

[ -d "$CASE_DIR" ] || die "cas introuvable : $CASE_DIR"
[ -d "$CASE_DIR/processor0" ] || die "$CAS n'est pas décomposé (pas de processor0/). Un cas terminé et reconstruit n'est pas repris par ce script."

NP=$(find "$CASE_DIR" -maxdepth 1 -type d -name 'processor*' | wc -l)
[ "$NP" -ge 2 ] || die "décomposition parallèle attendue, trouvé $NP processeur(s)"

# --- 1. pré-vol disque HÔTE ---------------------------------------------------
AVAIL_GO=$(df -BG --output=avail /mnt/c 2>/dev/null | tail -1 | tr -dc '0-9')
[ -n "$AVAIL_GO" ] || die "impossible de lire l'espace libre de /mnt/c (df). C'est le disque HÔTE qui compte ici, jamais /."
echo "Pré-vol : /mnt/c = ${AVAIL_GO} Go libres  (seuil bloquant : ${SEUIL_BLOQUANT_GO} Go)."
[ "$AVAIL_GO" -ge "$SEUIL_BLOQUANT_GO" ] \
  || die "/mnt/c (${AVAIL_GO} Go) sous le seuil de ${SEUIL_BLOQUANT_GO} Go — reprise refusée. Libérer le disque HÔTE (Windows) avant de relancer."

# --- 2. garde-fou : cas déjà terminé ----------------------------------------
END_TIME=$(foamDictionary -entry endTime -value "$CASE_DIR/system/controlDict" 2>/dev/null) \
  || END_TIME=$(awk '/^[[:space:]]*endTime[[:space:]]/ {gsub(/;/,"",$2); print $2; exit}' "$CASE_DIR/system/controlDict")
[ -n "$END_TIME" ] || die "endTime illisible dans $CASE_DIR/system/controlDict"

latest_proc_time() {
  ls "$CASE_DIR/processor0" | grep -E '^[0-9]+(\.[0-9]+)?$' | sort -g | tail -1
}
LATEST=$(latest_proc_time)
[ -n "$LATEST" ] || die "aucun pas de temps numérique dans processor0/ (cas jamais lancé ?)"

AT_ENDTIME=$(awk -v a="$LATEST" -v b="$END_TIME" 'BEGIN{print (a+0 >= b+0 - 1e-9) ? 1 : 0}')
HAS_END=0
grep -qE '^End$' "$CASE_DIR"/log.pimpleFoam* 2>/dev/null && HAS_END=1
if [ "$AT_ENDTIME" = 1 ] && [ "$HAS_END" = 1 ]; then
  die "$CAS est déjà terminé (latestTime=$LATEST, endTime=$END_TIME, log 'End' présent) — reprise refusée. Garde-fou case_kEpsilon / case_laminar."
fi

# --- 3. évacuation des pas de temps à 0 octet ------------------------------
BACKUP="$HELICE/_corrupt_backup/$CAS"
CORRUPT=()
for t in $(ls "$CASE_DIR/processor0" | grep -E '^[0-9]+(\.[0-9]+)?$' | sort -g); do
  bad=0
  for ((p = 0; p < NP; p++)); do
    d="$CASE_DIR/processor$p/$t"
    if [ ! -d "$d" ] || find "$d" -maxdepth 1 -type f -empty | grep -q .; then
      bad=1
      break
    fi
  done
  [ "$bad" = 1 ] && CORRUPT+=("$t")
done

if [ "${#CORRUPT[@]}" -gt 0 ]; then
  echo "Pas de temps corrompus (fichiers 0 octet) : ${CORRUPT[*]}"
  mkdir -p "$BACKUP"
  for t in "${CORRUPT[@]}"; do
    for ((p = 0; p < NP; p++)); do
      src="$CASE_DIR/processor$p/$t"
      [ -e "$src" ] || continue
      dst="$BACKUP/processor${p}_${t}"
      [ -e "$dst" ] && dst="${dst}_$(date +%s)"
      mv "$src" "$dst"
      echo "  déplacé : processor$p/$t  ->  _corrupt_backup/$CAS/$(basename "$dst")"
    done
  done
  LATEST=$(latest_proc_time)
  echo "latestTime après évacuation : $LATEST"
else
  echo "Aucun pas de temps à 0 octet."
fi
[ -n "$LATEST" ] || die "plus aucun pas de temps valide après évacuation — relance depuis 0 nécessaire (hors périmètre de ce script)."

# --- 4-5. reprise + reconstruction ---------------------------------------
STAMP=$(date +%Y%m%d-%H%M%S)
LOG="$CASE_DIR/log.reprise_$STAMP"
echo "=== reprise $CAS : $LATEST -> $END_TIME  ($(date -Is)) ===" | tee "$LOG"
cd "$CASE_DIR" || die "cd $CASE_DIR"

mpirun -np "$NP" pimpleFoam -parallel >>"$LOG" 2>&1
rc=$?
echo "=== pimpleFoam rc=$rc  ($(date -Is)) ===" | tee -a "$LOG"
[ "$rc" -eq 0 ] || die "pimpleFoam arrêté (rc=$rc). Voir $LOG — contrôler /mnt/c avant toute relance."

reconstructPar -newTimes >>"$LOG" 2>&1
rcr=$?
echo "=== reconstructPar rc=$rcr  ($(date -Is)) ===" | tee -a "$LOG"
[ "$rcr" -eq 0 ] || die "reconstructPar échoué (rc=$rcr). Voir $LOG."

echo "Reprise $CAS terminée — latestTime = $(latest_proc_time). Log : $LOG"
