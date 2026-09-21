#!/usr/bin/env python3
"""Produit le kit de données distribué aux étudiants (le calcul ne tourne pas en séance).

Deux sorties, indépendantes :

  --csv     data/perf_<fermeture>.csv   — séries temporelles scalaires des 3 cas.
            Colonnes : time,n,U_aval,J,KT,10KQ,eta0,tours,angle_deg. < 1 Mo au total.
            Trois fichiers de plus, un par configuration (`--csv-supplementaires`) : `perf_kEpsilon_layers.csv`
            (cas à couches, instationnaire, 4,00 tours, pas fixe 1e-5 s) et `perf_<modele>_MRF.csv` (stationnaire :
            `time` est le NUMÉRO D'ITÉRATION, `tours` et `angle_deg` sont vides). Mêmes colonnes et conventions.
            `J` = avance IMPOSÉE V_inlet/(nD) (constante) ; `U_aval` = vitesse moyenne relevée en aval du
            disque (ex-`URef` du solveur) ; `eta0` recalculé avec ce J. Voir le paragraphe suivant.
            VERSIONNÉ. Sert aux séances 1 et 2 et à l'inter-séance A.

  --champs  data/paraview_kit/          — sélection de pas de temps reconstruits pour
            ParaView (séance 3). ~750 Mo. NON versionné (gitignore) — à régénérer /
            distribuer à part. Par défaut : 5 pas du dernier tour sur case_kOmegaSST
            + 1 pas (t=0,06) sur les deux autres.

## Le rééchelonnement (décision enseignant du 15/09, INV-19)

`postProcessing/propellerInfo1/*/propellerPerformance.dat` est le BRUT produit par le
solveur -- l'enregistrement de ce qui a réellement tourné, avec `radius 0.1` (D=0,2 m).
**On ne réécrit jamais une mesure** : le brut reste intact, pour toujours faux au sens
où D=0,2 m n'a jamais été la géométrie réelle (corrigée le 14/09 à D=0,227378 m). La
correction vit ICI, dans ce script, PAS dans le brut :

    J     × (D_hist/D_correct)^1
    K_T   × (D_hist/D_correct)^4
    10K_Q × (D_hist/D_correct)^5
    eta0  inchangé (invariant par construction : eta0 = J·KT/(KQ·2π), D s'annule)

**Aucun facteur codé en dur** : `D_hist` est lu dans l'en-tête `# Radius` du brut
lui-même (auto-documenté par le solveur qui l'a produit) ; `D_correct` est lu dans
`Helice/docs/PARAMETRES_CAS.md` (source unique de vérité du cas). Si l'un des deux
change, le facteur se recalcule seul -- rien à retoucher ici.

## L'avance J et le rendement η₀ (correction du 20/09, soir)

Le `J` du solveur vaut `URef/(nD)` où `URef` est une vitesse MESURÉE à 0,17 D en aval des pales, dans la
zone d'induction : ce n'est pas une avance. Le CSV porte donc désormais :

    J        = V_inlet/(nD), avance imposée (0,8743), constante -- V_inlet lue dans `<cas>/0.orig/U`
    U_aval   = vitesse moyenne relevée en aval (colonne `URef` du solveur, négative : axe -y), conservée
               pour ce qu'elle est : une mesure, pas une avance
    eta0     = J K_T / (2 pi K_Q) avec ce J (ligne à ligne : eta0_solveur × J_imposé / J_solveur)

`KT` et `10KQ` ne dépendent que de n et D : ils ne doivent PAS bouger. `avance_imposee.py` porte la lecture
de V_inlet ; le garde-fou (K_T et 10 K_Q inchangés à la régénération) est vérifié dans `make_csv`.

**Correction du 17/09 (bug trouvé, pas supposé) : le réechelonnement se fait
SEGMENT PAR SEGMENT, plus une seule fois par cas.** Jusqu'ici `D_hist` était lu sur
le PREMIER segment (`paths[0]`) et le même ratio appliqué à TOUTES les lignes du
cas -- correct tant que « tous les segments sont identiques », vrai le 15/09 (tous
antérieurs au 14/09) mais plus du tout après une reprise postérieure à cette date :
`system/propellerInfo` porte désormais `radius 0.113689` (corrigé), donc tout NOUVEAU
segment écrit par une reprise s'auto-documente déjà au bon rayon. Lui appliquer quand
même le ratio du premier segment corrige une deuxième fois une valeur déjà correcte.
Trouvé le 17/09 sur la première reprise post-14/09 des trois cas sans couches (LOT 1,
consigne « Parallélisation-et-garde-chaîne ») : K_T de `case_kEpsilon` retombait à
~0,133 après t=0,06 s dans le CSV alors que le solveur lui-même imprimait K_T=0,2208
à la même date dans son log -- l'écart (ratio⁴≈0,599, 0,2208×0,599≈0,132) pointait
directement vers une double correction. Voir `_Methodo/JOURNAL.md`, 17/09.

Voir `Helice/docs/METHODO_DONNEES.md` pour la chaîne complète et le détail de ce
qui a changé le 15/09 (avant cette date, le rééchelonnement était fait À LA MAIN sur
les CSV, jamais capturé en code -- irreproductible, cf. JOURNAL du 15/09).

Usage :  python3 scripts/extraire_kit_donnees.py --csv
         python3 scripts/extraire_kit_donnees.py --champs
"""
import argparse
import csv
import math
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from compare_turbulence import find_performance_files, recoller, RecollementError, COLUMNS  # noqa: E402
from avance_imposee import vitesse_inlet, j_impose  # noqa: E402

CASES = {"case_kEpsilon": "kEpsilon", "case_kOmegaSST": "kOmegaSST", "case_laminar": "laminar"}
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
PARAMETRES_CAS = ROOT / "docs" / "PARAMETRES_CAS.md"

# `URef` (solveur) est renommée `U_aval` dans le CSV : vitesse moyenne relevée EN AVAL du disque, pas une avance.
OUT_COLUMNS = ["U_aval" if c == "URef" else c for c in COLUMNS] + ["tours", "angle_deg"]

_RADIUS_RE = re.compile(r"#\s*Radius\s*:\s*([\d.eE+-]+)")
_D_CORRECT_RE = re.compile(r"\|\s*D \(diamètre\)\s*\|\s*([\d,]+)\s*\|\s*m\s*\|")


def _d_historique(paths: list[Path]) -> float:
    """Lit le radius historique dans l'en-tête du PREMIER élément de `paths`.
    **N'est PAS forcément le même sur tous les segments d'un cas repris** (voir
    correction du 17/09 dans le docstring du module) -- appeler UN SEGMENT À LA
    FOIS (`_read_rows_rescaled` ci-dessous), jamais sur `paths` en entier en
    supposant l'ancien invariant « tous identiques »."""
    with open(paths[0]) as f:
        for line in f:
            m = _RADIUS_RE.match(line)
            if m:
                return 2.0 * float(m.group(1))
    raise SystemExit(f"En-tête '# Radius' introuvable dans {paths[0]} -- brut inattendu.")


def _d_correct() -> float:
    """Lit le D établi dans PARAMETRES_CAS.md -- source unique de vérité, jamais recopié."""
    text = PARAMETRES_CAS.read_text(encoding="utf-8")
    m = _D_CORRECT_RE.search(text)
    if not m:
        raise SystemExit(f"Ligne 'D (diamètre)' introuvable dans {PARAMETRES_CAS}.")
    return float(m.group(1).replace(",", "."))


def _rescale(row: dict, ratio: float) -> dict:
    """ratio = D_historique / D_correct -- multiplie J^1, K_T^4, 10K_Q^5 ; eta0 inchangé."""
    out = dict(row)
    out["J"] = f"{float(row['J']) * ratio:.6e}"
    out["KT"] = f"{float(row['KT']) * ratio**4:.6e}"
    out["10KQ"] = f"{float(row['10KQ']) * ratio**5:.6e}"
    return out


## Garde sur la chaîne de données (LOT 4, consigne du 18/09 « Rayon-explosion-et-
## relance ») -- ce que le bug du 17/09 aurait dû faire échouer AVANT de publier.
## Aucune de ces règles ne corrige : elles REFUSENT (sys.exit, code non nul, nomme
## le fichier) -- corriger reste un choix humain, jamais automatique.

_GAPS_CONNUS = {
    # (case, t0, t1) déjà documentés -- METHODO_DONNEES.md §5 défaut ①. Un trou hors
    # de cette liste est un défaut NOUVEAU, jamais un défaut déjà accepté.
    "case_kOmegaSST": [(0.00819355, 0.0220323)],
}


def _garde_fichier_ambigu(seg_dir: Path) -> None:
    """(a) REFORMULÉE le 20/09. Avant : tout `propellerPerformance_N.dat` coexistant avec le fichier
    normal était refusé comme « ambigu ». Or OpenFOAM crée ce suffixe précisément quand le fichier
    normal existe déjà dans le dossier de redémarrage : le suffixé est le PLUS RÉCENT, et
    `compare_turbulence.recoller` le traite comme tel (il remplace tout ce que le précédent contient
    à t >= son début). Cette règle bloquait laminar à 1,52 tour alors que le suffixé va à 4,00.
    Ne reste refusé que ce dont on ne connaît pas la provenance : `propellerPerformance_*_recupere*.dat`
    (fichier reconstitué à la main -- lequel est le bon ?)."""
    recup = sorted(p for p in seg_dir.glob("propellerPerformance_*recupere*.dat") if p.stat().st_size > 0)
    if recup:
        sys.exit(f"GARDE (a) -- {seg_dir} : {', '.join(p.name for p in recup)} -- fichier reconstitué, "
                 f"provenance inconnue. Ne pas choisir en silence.")


def _garde_octets_nuls(path: Path) -> None:
    """(b) Un .dat qui contient des octets NUL -- écriture interrompue/corrompue."""
    if not path.exists() or path.stat().st_size == 0:
        return
    with open(path, "rb") as f:
        if b"\x00" in f.read():
            sys.exit(f"GARDE (b) -- {path} contient des octets NUL -- fichier tronqué/corrompu, "
                     f"ne pas l'utiliser tel quel.")


# GARDE (c) (recouvrement incohérent) vit désormais dans compare_turbulence.recoller : elle comparait
# ICI une valeur déjà rééchelonnée du segment précédent à la valeur BRUTE du suivant, ce qui donnait un
# faux positif dès que deux segments se recouvraient avec un rayon d'en-tête différent de D_correct
# (kOmegaSST, 20/09 : « 0,2219 contre 0,3707 », écart brut réel nul).


def _garde_trous(case: str, rows: list[dict]) -> None:
    """(d) Le recollement laisse un trou > 5 échantillons (par rapport à l'écart
    typique mesuré sur CE cas) -- sauf trou déjà documenté (_GAPS_CONNUS)."""
    times = sorted(float(r["time"]) for r in rows)
    if len(times) < 3:
        return
    ecarts = sorted(times[i + 1] - times[i] for i in range(len(times) - 1))
    mediane = ecarts[len(ecarts) // 2]
    connus = _GAPS_CONNUS.get(case, [])
    for i in range(len(times) - 1):
        gap = times[i + 1] - times[i]
        if gap <= 5 * mediane:
            continue
        t0, t1 = times[i], times[i + 1]
        if any(abs(t0 - c0) < 1e-6 and abs(t1 - c1) < 1e-6 for (c0, c1) in connus):
            continue  # trou déjà documenté, METHODO_DONNEES.md §5
        sys.exit(f"GARDE (d) -- {case} : trou NON documenté entre t={t0} et t={t1} "
                 f"({gap / mediane:.0f}x l'écart typique {mediane:.3g} s) -- pas dans "
                 f"_GAPS_CONNUS, à documenter avant d'accepter ou à corriger.")


def _garde_ratios_declares(case: str, ratio_par_segment: dict) -> None:
    """(e) Deux segments d'un même cas avec des ratios de réechelonnement
    DIFFÉRENTS -- toléré UNIQUEMENT si déclaré ici, daté. C'est cette règle,
    appliquée hier, qui aurait attrapé le bug du 17/09 (ratio unique appliqué à
    des segments qui en demandaient deux différents, sans qu'aucune déclaration
    de ce genre n'existe encore)."""
    distinct = sorted(set(ratio_par_segment.values()))
    if len(distinct) <= 1:
        return
    detail = ", ".join(f"{seg}={r:.6f}" for seg, r in ratio_par_segment.items())
    print(f"  GARDE (e) -- {case} : ratios hétérogènes entre segments ({detail}) -- "
          f"DÉCLARÉ le 18/09 (bug du 17/09 corrigé, chaque segment est réechelonné "
          f"avec SON PROPRE radius d'en-tête -- voir JOURNAL.md, ENSM-Enseignement).")


def _read_rows_rescaled(case: str, paths: list[Path], d_correct: float) -> tuple[list[dict], list[float]]:
    """Lit CHAQUE segment avec SON PROPRE `D_hist` d'en-tête (correction du 17/09), le rééchelonne,
    puis recolle avec `compare_turbulence.recoller` (le segment le plus récent remplace ce qui suit son
    début, brut comparé à brut). Gardes (a) (variantes reconstituées), (b) (octets NUL), (d) (trous),
    (e) (ratios déclarés). Retourne (lignes recollées et rééchelonnées, ratios un par segment)."""
    for path in paths:
        _garde_fichier_ambigu(path.parent)
        _garde_octets_nuls(path)

    segments: list[dict] = []
    ratio_par_segment: dict[str, float] = {}
    ratios = []
    for path in paths:
        ratio_i = _d_historique([path]) / d_correct
        ratios.append(ratio_i)
        ratio_par_segment[f"{path.parent.name}/{path.name}"] = ratio_i
        brut, sortie = [], []
        with open(path) as f:
            for l in f:
                if l.startswith("#") or not l.strip():
                    continue
                parts = l.split()
                if len(parts) < len(COLUMNS):
                    continue
                row_brut = dict(zip(COLUMNS, parts))
                brut.append(row_brut)
                sortie.append(_rescale(row_brut, ratio_i))
        segments.append({"path": path, "brut": brut, "sortie": sortie})
    try:
        rows, rapport = recoller(segments)
    except RecollementError as e:
        sys.exit(f"GARDE (c) -- {case} : {e}")
    for ligne in rapport:
        print(ligne)
    _garde_trous(case, rows)
    _garde_ratios_declares(case, ratio_par_segment)
    return rows, ratios


def verifier_seul(case_dir_name: str) -> None:
    """Lance les règles de garde (a)-(e) sur UN cas, SANS produire de CSV --
    utile pour un cas hors de `CASES` (ex. `case_kEpsilon_layers`, à couches).
    Usage : python3 scripts/extraire_kit_donnees.py --verifier case_kEpsilon_layers"""
    d_correct = _d_correct()
    perf_files = find_performance_files(ROOT / case_dir_name)
    if not perf_files:
        sys.exit(f"{case_dir_name} : aucun postProcessing/propellerInfo1/*/propellerPerformance*.dat trouvé.")
    rows, ratios = _read_rows_rescaled(case_dir_name, perf_files, d_correct)
    print(f"OK -- {case_dir_name} : {len(rows)} lignes acceptées, aucune garde déclenchée "
          f"(ratios : {sorted(set(ratios))}).")


def _appliquer_avance_imposee(rows: list[dict], j_imp_fn) -> list[dict]:
    """Remplace `J` par l'avance imposée et recalcule `eta0` ; `KT`, `10KQ` et `URef` ne sont PAS touchés.
    eta0 = J K_T / (2 pi K_Q) est proportionnel à J : eta0_nouveau = eta0_solveur × J_imposé / J_solveur
    (exact, sans diviser par K_Q, qui s'annule pendant le démarrage impulsif)."""
    out = []
    for r in rows:
        j_old = float(r["J"])
        j_new = j_imp_fn(float(r["n"]))
        r2 = dict(r)
        r2["J"] = f"{j_new:.6e}"
        r2["eta0"] = f"{float(r['eta0']) * j_new / j_old:.6e}"
        out.append(r2)
    return out


def _lire_avant(out: Path) -> dict:
    if not out.is_file():
        return {}
    with open(out, newline="") as f:
        return {r["time"]: (r["KT"], r["10KQ"], r["n"]) for r in csv.DictReader(f)}


def _garde_kt_kq_inchanges(out: Path, avant: dict) -> None:
    """Garde-fou central de la correction du 20/09 : `KT`, `10KQ` et `n` du fichier écrit doivent être
    IDENTIQUES, chaîne pour chaîne, à ceux de la version précédente (`avant`, lue avant l'écriture).
    Un écart signifierait qu'un calcul touche à ce qu'il ne devrait pas : on refuse."""
    if not avant:
        return
    apres = _lire_avant(out)
    if set(apres) != set(avant):
        sys.exit(f"GARDE K_T/10K_Q -- {out.name} : l'ensemble des temps a changé "
                 f"({len(set(avant) ^ set(apres))} différence(s)) -- ce n'est pas la correction de J.")
    diff = [t for t in avant if avant[t] != apres[t]]
    if diff:
        sys.exit(f"GARDE K_T/10K_Q -- {out.name} : KT, 10KQ ou n ont changé à {len(diff)} ligne(s) "
                 f"(premier temps {diff[0]}) -- la correction de J ne doit toucher ni K_T ni K_Q. ARRÊT.")
    print(f"  garde K_T/10K_Q : {len(apres)} lignes, KT, 10KQ, n identiques à la version précédente.")


def make_csv() -> None:
    DATA.mkdir(exist_ok=True)
    d_correct = _d_correct()
    n_tr_s = 158 / (2 * math.pi)  # dynamicMeshDict:29, omega/2pi -- même valeur que le BLOC A

    for case, short in CASES.items():
        perf_files = find_performance_files(ROOT / case)
        rows, ratios = _read_rows_rescaled(case, perf_files, d_correct)
        v_inlet = vitesse_inlet(ROOT / case)
        rows = _appliquer_avance_imposee(rows, lambda n: j_impose(v_inlet, n, d_correct))

        out = DATA / f"perf_{short}.csv"
        avant = _lire_avant(out)
        with open(out, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(OUT_COLUMNS)
            for r in rows:
                t = float(r["time"])
                tours = t * n_tr_s
                angle_deg = (360.0 * t * n_tr_s) % 360.0
                w.writerow([r[c] for c in COLUMNS] + [f"{tours:.6f}", f"{angle_deg:.4f}"])
        _garde_kt_kq_inchanges(out, avant)
        kb = out.stat().st_size / 1024
        ratios_str = ", ".join(f"{r:.6f}" for r in sorted(set(ratios)))
        print(f"  {out.relative_to(ROOT)}  ({len(rows)} lignes, {kb:.0f} Ko, "
              f"D_correct={d_correct:.6f} m, V_inlet={v_inlet:g} m/s, "
              f"ratio(s) par segment={{{ratios_str}}})")


# Configurations hors de CASES : (fichier de sortie, dossier de cas, fichier brut choisi EXPLICITEMENT, stationnaire ?).
# Le fichier brut est nommé, jamais globé : `case_kEpsilon_layers` porte aussi un `propellerPerformance_0_recupere.dat`
# (reconstitué, 2 tours, pas de 2e-5) et un `propellerPerformance.dat` partiel d'avant la reprise, qu'il ne faut PAS lire.
SUPPLEMENTAIRES = {
    "kEpsilon_layers": ("case_kEpsilon_layers", "postProcessing/propellerInfo1/0/propellerPerformance_0.dat", False),
    "kEpsilon_MRF": ("case_kEpsilon_MRF", "postProcessing/propellerInfo1/0/propellerPerformance.dat", True),
    "kOmegaSST_MRF": ("case_kOmegaSST_MRF", "postProcessing/propellerInfo1/0/propellerPerformance.dat", True),
    "laminar_MRF": ("case_laminar_MRF", "postProcessing/propellerInfo1/0/propellerPerformance.dat", True),
}


def make_csv_supplementaires(noms: list[str] | None = None) -> None:
    """Écrit `data/perf_<nom>.csv` pour les configurations de SUPPLEMENTAIRES (mêmes colonnes que les CSV du kit).
    Un segment unique, rééchelonné avec SON `# Radius` (rapport 1 ici : ces cas sont postérieurs au 14/09), J = avance
    imposée, eta0 recalculé, `URef` renommée `U_aval`. Stationnaire : `time` = itération, `tours` et `angle_deg` vides."""
    d_correct = _d_correct()
    n_tr_s = 158 / (2 * math.pi)
    for nom in (noms or list(SUPPLEMENTAIRES)):
        dossier, brut, stationnaire = SUPPLEMENTAIRES[nom]
        path = ROOT / dossier / brut
        if not path.is_file():
            print(f"  ⚠ {nom} : {path.relative_to(ROOT)} introuvable -- non écrit.")
            continue
        _garde_octets_nuls(path)
        ratio = _d_historique([path]) / d_correct
        v_inlet = vitesse_inlet(ROOT / dossier)
        rows = []
        for l in open(path):
            if l.startswith("#") or not l.strip():
                continue
            parts = l.split()
            if len(parts) < len(COLUMNS):
                continue
            rows.append(_rescale(dict(zip(COLUMNS, parts)), ratio))
        rows = _appliquer_avance_imposee(rows, lambda n: j_impose(v_inlet, n, d_correct))
        out = DATA / f"perf_{nom}.csv"
        with open(out, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(OUT_COLUMNS)
            for r in rows:
                if stationnaire:
                    extra = ["", ""]
                else:
                    t = float(r["time"])
                    extra = [f"{t * n_tr_s:.6f}", f"{(360.0 * t * n_tr_s) % 360.0:.4f}"]
                w.writerow([r[c] for c in COLUMNS] + extra)
        print(f"  {out.relative_to(ROOT)}  ({len(rows)} lignes, {out.stat().st_size / 1024:.0f} Ko, ratio D={ratio:.6f}, "
              f"V_inlet={v_inlet:g} m/s, {'stationnaire : time = itération' if stationnaire else 'instationnaire'})")


def _reconstructed_times(case_dir: Path) -> list[str]:
    return sorted(
        (p.name for p in case_dir.iterdir() if p.is_dir() and _isfloat(p.name) and p.name != "0"),
        key=float,
    )


def _isfloat(s: str) -> bool:
    try:
        float(s)
        return True
    except ValueError:
        return False


def make_champs(n_last: int = 5) -> None:
    kit = DATA / "paraview_kit"
    if kit.exists():
        shutil.rmtree(kit)
    for case in CASES:
        src = ROOT / case
        times = _reconstructed_times(src)
        if not times:
            print(f"  ⚠ {case} : aucun pas reconstruit — lancer reconstructPar d'abord.")
            continue
        keep = times[-n_last:] if case == "case_kOmegaSST" else times[-1:]
        dst = kit / case
        dst.mkdir(parents=True)
        for sub in ("constant", "system"):
            if (src / sub).exists():
                shutil.copytree(src / sub, dst / sub, ignore=shutil.ignore_patterns("polyMesh"))
        shutil.copytree(src / "constant" / "polyMesh", dst / "constant" / "polyMesh")
        for t in keep:
            shutil.copytree(src / t, dst / t)
        (dst / f"{case}.foam").touch()
        print(f"  {dst.relative_to(ROOT)} : pas {keep}")
    total = sum(f.stat().st_size for f in kit.rglob("*") if f.is_file()) / 1e6
    print(f"  total kit champs : {total:.0f} Mo")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", action="store_true", help="produit data/perf_*.csv (versionné)")
    ap.add_argument("--csv-supplementaires", action="store_true", dest="supp",
                    help="produit data/perf_kEpsilon_layers.csv et data/perf_<modele>_MRF.csv (versionnés)")
    ap.add_argument("--champs", action="store_true", help="produit data/paraview_kit/ (~750 Mo, non versionné)")
    ap.add_argument("--n-last", type=int, default=5, help="nb de pas du dernier tour pour case_kOmegaSST")
    ap.add_argument("--verifier", metavar="CASE_DIR",
                     help="lance seulement les gardes (a)-(e) sur ce dossier de cas, sans produire de CSV "
                          "(utile pour un cas hors de CASES, ex. case_kEpsilon_layers)")
    a = ap.parse_args()
    if not (a.csv or a.champs or a.verifier or a.supp):
        ap.error("préciser --csv, --csv-supplementaires, --champs et/ou --verifier CASE_DIR")
    if a.verifier:
        verifier_seul(a.verifier)
    if a.csv:
        print("CSV (séances 1-2) :")
        make_csv()
    if a.supp:
        print("CSV supplémentaires (couches, MRF) :")
        make_csv_supplementaires()
    if a.champs:
        print("Champs ParaView (séance 3) :")
        make_champs(a.n_last)
