# TP OpenFOAM — Simulation d'un Propulseur en Eau Libre
### Environnement : Windows 11 · WSL Ubuntu 24.04 · OpenFOAM ESI v2412

---

## Table des matières

1. [Installation d'OpenFOAM ESI v2412 sous WSL](#1-installation-dopenfoam-esi-v2412-sous-wsl)
2. [Installation de ParaView pour la visualisation](#2-installation-de-paraview-pour-la-visualisation)
3. [Démarrage rapide — Tutoriel natif v2412](#3-démarrage-rapide--tutoriel-natif-v2412)
4. [Présentation du cas tutoriel Propeller](#4-présentation-du-cas-tutoriel-propeller)
5. [Structure du cas](#5-structure-du-cas)
6. [Étape 1 — Copier et préparer le cas](#6-étape-1--copier-et-préparer-le-cas)
7. [Étape 2 — Génération du maillage](#7-étape-2--génération-du-maillage)
8. [Étape 3 — Conditions aux limites et initiales](#8-étape-3--conditions-aux-limites-et-initiales)
9. [Étape 4 — Paramètres de simulation](#9-étape-4--paramètres-de-simulation)
10. [Étape 5 — Lancement du calcul](#10-étape-5--lancement-du-calcul)
11. [Étape 6 — Post-traitement avec ParaView](#11-étape-6--post-traitement-avec-paraview)
12. [Annexe — Pour aller plus loin : Comparaison des approches](#12-annexe--pour-aller-plus-loin--comparaison-des-approches-de-simulation)
13. [Référence des fichiers de configuration](#13-référence-des-fichiers-de-configuration)
14. [Commandes utiles OpenFOAM](#14-commandes-utiles-openfoam)
15. [Dépannage](#15-dépannage)
---

## 1. Installation d'OpenFOAM ESI v2412 sous WSL

### 1.1 Prérequis WSL

Ouvrez **PowerShell en administrateur** et vérifiez votre version WSL :

```powershell
wsl --version
wsl --list --verbose
```

Assurez-vous d'avoir **WSL2** avec Ubuntu 24.04. Si ce n'est pas le cas :

```powershell
wsl --set-default-version 2
wsl --install -d Ubuntu-24.04
```

### 1.2 Mise à jour du système Ubuntu

Lancez Ubuntu 24.04 depuis le menu Démarrer, puis :

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y build-essential cmake git wget curl vim
```

### 1.3 Installation d'OpenFOAM ESI v2412 via le dépôt officiel

```bash
# Ajout du dépôt OpenCFD (ESI)
curl -s https://dl.openfoam.com/add-debian-repo.sh | sudo bash

# Installation d'OpenFOAM v2412
sudo apt install -y openfoam2412

# Activation des variables d'environnement (à ajouter dans ~/.bashrc)
echo "source /usr/lib/openfoam/openfoam2412/etc/bashrc" >> ~/.bashrc
source ~/.bashrc
```

### 1.4 Vérification de l'installation

```bash
# Vérifier que foamVersion fonctionne
foamVersion
# Attendu : OpenFOAM-v2412

# Vérifier que les tutoriels sont présents
ls $FOAM_TUTORIALS/incompressible/pimpleFoam/RAS/
# Vous devriez voir : propeller  airFoil2D  ...

# Créer le répertoire de travail utilisateur
mkdir -p $FOAM_RUN
echo "Répertoire de travail : $FOAM_RUN"
```

---

## 2. Installation de ParaView pour la visualisation

### Option A — ParaView natif Windows (recommandé pour WSL)

1. Téléchargez ParaView depuis [https://www.paraview.org/download/](https://www.paraview.org/download/)
2. Installez-le sous Windows normalement
3. Depuis WSL, générez le fichier `.foam` et ouvrez-le depuis l'explorateur Windows

```bash
# Dans le dossier du cas, créer un fichier .foam vide
touch propeller.foam
# Ouvrir l'explorateur Windows dans le dossier WSL
explorer.exe .
```

### Option B — ParaView dans WSL avec affichage X11

```bash
# Installer un serveur X11 sous Windows : VcXsrv ou X410 (Microsoft Store)
# Puis dans WSL :
sudo apt install -y paraview

# Configurer l'affichage (ajouter dans ~/.bashrc)
echo "export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0" >> ~/.bashrc
source ~/.bashrc

# Lancer ParaView
paraview &
```

---

## 3. Démarrage rapide — Tutoriel natif v2412

### 3.1 Vérifier que le tutoriel est présent

```bash
# S'assurer que l'environnement OpenFOAM est chargé
source /usr/lib/openfoam/openfoam2412/etc/bashrc

# Vérifier la présence du tutoriel propeller
ls $FOAM_TUTORIALS/incompressible/pimpleFoam/RAS/propeller
```

Résultat attendu :
```
0/  constant/  system/  Allrun  Allclean  Allmesh
```

> Si le répertoire `propeller` est absent, le tutoriel peut aussi se trouver ici :
> ```bash
> find $FOAM_TUTORIALS -name "*propeller*" -type d
> # Autres chemins possibles :
> # $FOAM_TUTORIALS/incompressible/pimpleDyMFoam/propeller
> # $FOAM_TUTORIALS/multiphase/interFoam/RAS/propeller
> ```

### 3.2 Copier le cas dans ton répertoire de travail

```bash
# Créer le répertoire de travail si absent
mkdir -p $FOAM_RUN

# Copier le tutoriel
cp -r $FOAM_TUTORIALS/incompressible/pimpleFoam/RAS/propeller $FOAM_RUN/propeller_eau_libre

# Se placer dans le cas
cd $FOAM_RUN/propeller_eau_libre
```

### 3.3 Explorer la structure du cas

```bash
# Lister tous les fichiers du cas
ls -R .

# Lire le script de lancement automatique
cat Allrun

# Lire le script de maillage
cat Allmesh
```

### 3.4 Lancement en une commande (script Allrun)

```bash
# Rendre les scripts exécutables
chmod +x Allrun Allclean Allmesh

# Option A — Tout lancer d'un coup (maillage + calcul)
./Allrun

# Option B — Étape par étape (recommandé pour comprendre)
./Allmesh          # Génère le maillage uniquement
pimpleFoam         # Lance le calcul
```

Surveiller la progression :
```bash
# Dans un second terminal WSL
tail -f $FOAM_RUN/propeller_eau_libre/log.pimpleFoam
```

### 3.5 Vérification rapide après Allrun

```bash
# Vérifier que des dossiers de temps ont été créés
ls $FOAM_RUN/propeller_eau_libre/
# Attendu : 0/  0.01/  0.02/  ...  constant/  system/  log.*

# Vérifier la convergence (chercher "PIMPLE: converged" dans les logs)
grep "PIMPLE: converged" log.pimpleFoam | tail -5

# Vérifier les forces calculées
ls postProcessing/
cat postProcessing/forces*/0/force.dat | tail -10
```

### 3.6 Ouvrir dans ParaView

```bash
# Créer le fichier .foam pour ParaView
touch propeller_eau_libre.foam

# Si ParaView est installé dans WSL
paraFoam &

# Si ParaView est installé sous Windows
# Ouvrir l'explorateur Windows dans ce dossier :
explorer.exe .
# Puis double-clic sur propeller_eau_libre.foam
```

---

## 4. Présentation du cas tutoriel Propeller

### Contexte physique

Le cas **`propeller`** simule une hélice navale tournant en eau libre (*open-water*). L'objectif est de calculer :

- Les **forces et moments** exercés sur les pales (poussée KT, couple KQ)
- Le **champ de vitesse** et de **pression** autour de l'hélice
- Les **structures tourbillonnaires** (vortex de bord de fuite)

### Solveur utilisé : `pimpleFoam` (RAS)

| Paramètre | Valeur |
|---|---|
| Solveur | `pimpleFoam` (instationnaire, incompressible) |
| Modèle de turbulence | k-ε (RAS) |
| Mouvement du maillage | `MRF` (Moving Reference Frame) ou rotation solide |
| Fluide | Eau (ρ = 1000 kg/m³, ν = 1×10⁻⁶ m²/s) |

### Fichiers de géométrie

L'hélice est définie via une **surface triangulaire (STL)** importée dans `snappyHexMesh`. La géométrie type utilisée dans les études académiques est le propulseur **INSEAN E779A** ou **KP505**.

---

## 5. Structure du cas

```
propeller/
├── 0/                          # Conditions initiales et aux limites
│   ├── U                       # Champ de vitesse
│   ├── p                       # Champ de pression
│   ├── k                       # Énergie cinétique turbulente
│   ├── epsilon                 # Taux de dissipation turbulente
│   └── nut                     # Viscosité turbulente
│
├── constant/
│   ├── polyMesh/               # Maillage (généré par blockMesh + snappyHexMesh)
│   ├── triSurface/             # Géométrie STL de l'hélice
│   │   └── propeller.obj.gz    # Surface de l'hélice
│   ├── transportProperties     # Propriétés du fluide (ν, ρ)
│   ├── turbulenceProperties    # Modèle de turbulence
│   └── MRFProperties           # Zone de rotation (MRF)
│
└── system/
    ├── blockMeshDict           # Maillage de fond (boîte hexaédrique)
    ├── snappyHexMeshDict       # Raffinement autour de l'hélice
    ├── surfaceFeatureExtractDict # Extraction des arêtes
    ├── controlDict             # Paramètres temporels, fonctions de post-traitement
    ├── fvSchemes               # Schémas numériques
    └── fvSolution              # Solveurs linéaires et tolérances
```

---

## 6. Étape 1 — Copier et préparer le cas

```bash
# Se placer dans le répertoire de travail OpenFOAM
cd $FOAM_RUN

# Copier le tutoriel propeller
cp -r $FOAM_TUTORIALS/incompressible/pimpleFoam/RAS/propeller ./propeller_eau_libre

# Entrer dans le dossier
cd propeller_eau_libre

# Lister le contenu pour vérifier
ls -la
```

---

## 7. Étape 2 — Génération du maillage

### 6.1 Contenu de `system/blockMeshDict`

Ce fichier définit le domaine de calcul (boîte englobante) en hexaèdres :

```cpp
/*--------------------------------*- C++ -*----------------------------------*\
  =========                 |
  \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\    /   O peration     | Version:  v2412
    \\  /    A nd           | Website:  www.openfoam.com
     \\/     M anipulation  |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      blockMeshDict;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

scale   1;

vertices
(
    (-1.5 -1.5 -1.5)   // 0
    ( 3.0 -1.5 -1.5)   // 1
    ( 3.0  1.5 -1.5)   // 2
    (-1.5  1.5 -1.5)   // 3
    (-1.5 -1.5  1.5)   // 4
    ( 3.0 -1.5  1.5)   // 5
    ( 3.0  1.5  1.5)   // 6
    (-1.5  1.5  1.5)   // 7
);

blocks
(
    hex (0 1 2 3 4 5 6 7) (30 20 20) simpleGrading (1 1 1)
);

boundary
(
    inlet
    {
        type patch;
        faces ((0 4 7 3));
    }
    outlet
    {
        type patch;
        faces ((1 2 6 5));
    }
    sides
    {
        type patch;
        faces
        (
            (0 1 5 4)
            (3 7 6 2)
            (0 3 2 1)
            (4 5 6 7)
        );
    }
);
```

### 6.2 Extraction des arêtes (surfaceFeatureExtract)

```bash
surfaceFeatureExtract
```

Cela lit `system/surfaceFeatureExtractDict` et génère les fichiers d'arêtes dans `constant/extendedFeatureEdgeMesh/`.

### 6.3 Génération du maillage de fond

```bash
blockMesh
```

Vérification du maillage :

```bash
checkMesh
# Chercher : "Mesh OK" à la fin du rapport
```

### 6.4 Raffinement avec snappyHexMesh

```bash
snappyHexMesh -overwrite
```

> **Note :** L'option `-overwrite` écrase directement les dossiers de temps plutôt que de créer des sous-dossiers numérotés.

Vérification après raffinement :

```bash
checkMesh
```

### 6.5 Script Allrun.pre (alternative)

Le tutoriel fournit un script qui automatise les étapes de maillage :

```bash
# Rendre le script exécutable si nécessaire
chmod +x Allrun.pre

# Lancer le pré-traitement complet
./Allrun.pre
```

---

## 8. Étape 3 — Conditions aux limites et initiales

### 7.1 Fichier `0/U` — Vitesse

```cpp
FoamFile
{
    version     2.0;
    format      ascii;
    class       volVectorField;
    object      U;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [0 1 -1 0 0 0 0];

// Vitesse d'avance (eau libre) : Va = 1.0 m/s en direction X
internalField   uniform (1.0 0 0);

boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform (1.0 0 0);
    }
    outlet
    {
        type            zeroGradient;
    }
    sides
    {
        type            slip;
    }
    propeller
    {
        type            movingWallVelocity;
        value           uniform (0 0 0);
    }
    hub
    {
        type            movingWallVelocity;
        value           uniform (0 0 0);
    }
}
```

### 7.2 Fichier `0/p` — Pression

```cpp
FoamFile
{
    version     2.0;
    format      ascii;
    class       volScalarField;
    object      p;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [0 2 -2 0 0 0 0];

internalField   uniform 0;

boundaryField
{
    inlet
    {
        type            zeroGradient;
    }
    outlet
    {
        type            fixedValue;
        value           uniform 0;
    }
    sides
    {
        type            slip;
    }
    propeller
    {
        type            zeroGradient;
    }
    hub
    {
        type            zeroGradient;
    }
}
```

### 7.3 Fichier `0/k` — Énergie cinétique turbulente

```cpp
FoamFile
{
    version     2.0;
    format      ascii;
    class       volScalarField;
    object      k;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [0 2 -2 0 0 0 0];

// k = 1.5 * (I * U)^2  avec I = 5% (turbulence intensity)
// k ≈ 1.5 * (0.05 * 1.0)^2 = 0.00375 m²/s²
internalField   uniform 0.00375;

boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform 0.00375;
    }
    outlet
    {
        type            zeroGradient;
    }
    sides
    {
        type            slip;
    }
    propeller
    {
        type            kqRWallFunction;
        value           uniform 0.00375;
    }
    hub
    {
        type            kqRWallFunction;
        value           uniform 0.00375;
    }
}
```

### 7.4 Fichier `0/epsilon` — Taux de dissipation

```cpp
FoamFile
{
    version     2.0;
    format      ascii;
    class       volScalarField;
    object      epsilon;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [0 2 -3 0 0 0 0];

// epsilon = C_mu^(3/4) * k^(3/2) / L  avec L = 0.1 * D (longueur intégrale)
// epsilon ≈ 0.09^(0.75) * 0.00375^(1.5) / 0.025 ≈ 0.001 m²/s³
internalField   uniform 0.001;

boundaryField
{
    inlet
    {
        type            fixedValue;
        value           uniform 0.001;
    }
    outlet
    {
        type            zeroGradient;
    }
    sides
    {
        type            slip;
    }
    propeller
    {
        type            epsilonWallFunction;
        value           uniform 0.001;
    }
    hub
    {
        type            epsilonWallFunction;
        value           uniform 0.001;
    }
}
```

### 7.5 Fichier `0/nut` — Viscosité turbulente

```cpp
FoamFile
{
    version     2.0;
    format      ascii;
    class       volScalarField;
    object      nut;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [0 2 -1 0 0 0 0];

internalField   uniform 0;

boundaryField
{
    inlet
    {
        type            calculated;
        value           uniform 0;
    }
    outlet
    {
        type            calculated;
        value           uniform 0;
    }
    sides
    {
        type            slip;
    }
    propeller
    {
        type            nutkWallFunction;
        value           uniform 0;
    }
    hub
    {
        type            nutkWallFunction;
        value           uniform 0;
    }
}
```

---

## 9. Étape 4 — Paramètres de simulation

### 8.1 Fichier `constant/transportProperties`

```cpp
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      transportProperties;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

transportModel  Newtonian;

// Viscosité cinématique de l'eau à 20°C
nu              [0 2 -1 0 0 0 0] 1e-06;
```

### 8.2 Fichier `constant/turbulenceProperties`

```cpp
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      turbulenceProperties;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

simulationType  RAS;

RAS
{
    RASModel        kEpsilon;
    turbulence      on;
    printCoeffs     on;
}
```

### 8.3 Fichier `constant/MRFProperties` — Zone de rotation MRF

```cpp
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      MRFProperties;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

MRF1
{
    cellZone        rotating;       // Zone cellulaire en rotation (définie dans snappyHexMesh)
    active          yes;

    // Axe de rotation : ici l'axe X (axe de l'arbre)
    origin          (0 0 0);
    axis            (1 0 0);

    // Vitesse de rotation : n = 20 tr/s → ω = 2π×20 ≈ 125.66 rad/s
    omega           125.66;         // rad/s
}
```

> **Paramètres eau libre importants :**
> - Vitesse d'avance : **Va = 1.0 m/s**
> - Vitesse de rotation : **n = 20 tr/s** (1200 tr/min)
> - Coefficient d'avance : **J = Va / (n × D)** (ex: J = 1.0 / (20 × 0.25) = 0.2)

### 8.4 Fichier `system/controlDict`

```cpp
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      controlDict;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

application     pimpleFoam;

startFrom       startTime;
startTime       0;
stopAt          endTime;
endTime         0.5;            // Durée de simulation [s]

deltaT          0.001;          // Pas de temps [s]
writeControl    timeStep;
writeInterval   50;             // Écriture toutes les 50 itérations
purgeWrite      3;              // Garder seulement les 3 derniers temps

writeFormat     binary;
writePrecision  8;
writeCompression off;

timeFormat      general;
timePrecision   6;

runTimeModifiable true;

// -----------------------------------------------
// Fonctions de post-traitement
// -----------------------------------------------
functions
{
    // Calcul des forces et moments sur l'hélice
    forces_propeller
    {
        type            forces;
        libs            ("libforces.so");

        writeControl    timeStep;
        writeInterval   10;

        patches         (propeller hub);    // Patches de l'hélice

        rho             rhoInf;             // Densité constante (incompressible)
        rhoInf          1000;               // kg/m³ (eau)

        CofR            (0 0 0);            // Centre de référence pour les moments
        pitchAxis       (0 1 0);

        log             yes;
    }

    // Calcul des coefficients aérodynamiques (hydrodynamiques ici)
    forceCoeffs_propeller
    {
        type            forceCoeffs;
        libs            ("libforces.so");

        writeControl    timeStep;
        writeInterval   10;

        patches         (propeller hub);

        rho             rhoInf;
        rhoInf          1000;

        liftDir         (0 0 1);
        dragDir         (1 0 0);
        pitchAxis       (0 1 0);
        magUInf         1.0;            // Vitesse de référence [m/s]
        lRef            0.25;           // Diamètre de référence [m]
        Aref            0.0491;         // Surface de référence = π*D²/4 [m²]

        CofR            (0 0 0);

        log             yes;
    }

    // Résidu de convergence
    residuals
    {
        type            solverInfo;
        libs            ("libutilityFunctionObjects.so");
        fields          (U p k epsilon);
    }
}
```

### 8.5 Fichier `system/fvSchemes`

```cpp
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      fvSchemes;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

ddtSchemes
{
    default         Euler;              // Schéma temporel du 1er ordre
}

gradSchemes
{
    default         Gauss linear;
    grad(U)         cellLimited Gauss linear 1;
}

divSchemes
{
    default         none;
    div(phi,U)      Gauss linearUpwind grad(U);
    div(phi,k)      Gauss upwind;
    div(phi,epsilon) Gauss upwind;
    div((nuEff*dev(T(grad(U))))) Gauss linear;
}

laplacianSchemes
{
    default         Gauss linear corrected;
}

interpolationSchemes
{
    default         linear;
}

snGradSchemes
{
    default         corrected;
}
```

### 8.6 Fichier `system/fvSolution`

```cpp
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      fvSolution;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

solvers
{
    p
    {
        solver          GAMG;
        smoother        GaussSeidel;
        tolerance       1e-06;
        relTol          0.05;
    }

    pFinal
    {
        $p;
        relTol          0;
    }

    U
    {
        solver          smoothSolver;
        smoother        symGaussSeidel;
        tolerance       1e-05;
        relTol          0.1;
    }

    UFinal
    {
        $U;
        relTol          0;
    }

    "(k|epsilon|nut)"
    {
        solver          smoothSolver;
        smoother        symGaussSeidel;
        tolerance       1e-05;
        relTol          0.1;
    }
}

PIMPLE
{
    nOuterCorrectors    2;          // Itérations PIMPLE (outer)
    nCorrectors         2;          // Corrections de pression (inner)
    nNonOrthogonalCorrectors 1;     // Corrections non-orthogonales

    residualControl
    {
        U
        {
            tolerance   1e-04;
            relTol      0;
        }
        p
        {
            tolerance   5e-04;
            relTol      0;
        }
    }
}

relaxationFactors
{
    fields
    {
        p               0.3;
    }
    equations
    {
        U               0.7;
        k               0.5;
        epsilon         0.5;
    }
}
```

---

## 10. Étape 5 — Lancement du calcul

### 9.1 Exécution séquentielle (simple)

```bash
cd $FOAM_RUN/propeller_eau_libre

# Lancer le calcul
pimpleFoam 2>&1 | tee log.pimpleFoam

# Surveiller les résidus en temps réel
tail -f log.pimpleFoam
```

### 9.2 Exécution parallèle (recommandé pour réduire le temps de calcul)

```bash
# 1. Décomposer le domaine en N sous-domaines (ici N=4)
decomposePar -force

# Contenu de system/decomposeParDict à créer si absent :
cat > system/decomposeParDict << 'EOF'
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      decomposeParDict;
}
numberOfSubdomains  4;
method          scotch;
EOF

# Relancer la décomposition
decomposePar -force

# 2. Lancer en parallèle
mpirun -np 4 pimpleFoam -parallel 2>&1 | tee log.pimpleFoam

# 3. Reconstruire les résultats après le calcul
reconstructPar
```

### 9.3 Utilisation du script Allrun fourni

```bash
chmod +x Allrun
./Allrun
```

### 9.4 Surveillance des forces en temps réel

```bash
# Pendant le calcul, surveiller les forces calculées
tail -f postProcessing/forces_propeller/0/force.dat

# Voir les coefficients
tail -f postProcessing/forceCoeffs_propeller/0/forceCoeffs.dat
```

---

## 11. Étape 6 — Post-traitement avec ParaView

### 10.1 Ouverture du cas

```bash
# Créer le fichier .foam pour ParaView
touch propeller_eau_libre.foam

# Option A : Si ParaView est installé dans WSL
paraFoam &

# Option B : Ouvrir depuis Windows
explorer.exe .
# Puis double-clic sur propeller_eau_libre.foam dans ParaView Windows
```

### 10.2 Visualisations recommandées

**Champ de pression :**
1. Dans ParaView → Properties → Coloring → choisir `p`
2. Apply → Rescale to Data Range

**Vecteurs de vitesse :**
1. Filters → Common → Glyph
2. Glyph Type : Arrow, Scale Array : U

**Iso-surfaces de vitesse (Q-criterion pour tourbillons) :**
1. Filters → Common → Calculator
2. Entrer la formule Q : `0.5*(mag(grad_U)^2 - mag(S)^2)`
3. Filters → Contour → iso-surface à une valeur positive

**Lignes de courant :**
1. Filters → Common → Stream Tracer
2. Seed Type : Line Source (à l'entrée)
3. Integration Direction : Forward

### 10.3 Extraction des courbes de performance (eau libre)

Pour obtenir la courbe KT–KQ–η en fonction du coefficient d'avance J :

```bash
# Calculer les forces pour plusieurs vitesses Va (modifier blockMeshDict + 0/U)
# Puis post-traiter avec le script Python suivant :
```

```python
#!/usr/bin/env python3
"""
Script de post-traitement : Courbes de performance eau libre
KT = T / (rho * n^2 * D^4)
KQ = Q / (rho * n^2 * D^5)
eta = J * KT / (2*pi*KQ)
"""
import numpy as np
import matplotlib.pyplot as plt

# Paramètres de l'hélice
rho = 1000.0    # kg/m³
n   = 20.0      # tr/s
D   = 0.25      # m (diamètre)

# Lire les forces depuis postProcessing
def lire_forces(fichier):
    """Lit le fichier force.dat et retourne la moyenne des dernières valeurs."""
    data = np.loadtxt(fichier, comments='#')
    # Colonne 0 : temps, colonnes 1-3 : force pression, colonnes 4-6 : force visqueuse
    # Poussée T = Fx_pression + Fx_visqueux (direction X)
    n_moy = max(1, len(data) // 5)  # Moyenne sur le dernier 1/5 du calcul
    T = np.mean(data[-n_moy:, 1] + data[-n_moy:, 4])
    Q = np.mean(data[-n_moy:, 3] + data[-n_moy:, 6])  # Moment My
    return T, Q

# Exemple avec plusieurs J
J_vals = [0.2, 0.4, 0.6, 0.8, 1.0]
KT_vals, KQ_vals, eta_vals = [], [], []

for J in J_vals:
    Va = J * n * D
    # Adapter le chemin selon le cas calculé
    T, Q = lire_forces(f"resultats_J{J}/postProcessing/forces_propeller/0/force.dat")

    KT = T / (rho * n**2 * D**4)
    KQ = Q / (rho * n**2 * D**5)
    eta = J * KT / (2 * np.pi * KQ) if KQ != 0 else 0

    KT_vals.append(KT)
    KQ_vals.append(KQ)
    eta_vals.append(eta)

# Tracé des courbes
fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(J_vals, KT_vals, 'b-o', label='KT (poussée)')
ax.plot(J_vals, KQ_vals, 'r-s', label='10·KQ (couple)')
ax.plot(J_vals, eta_vals, 'g-^', label='η (rendement)')
ax.set_xlabel('Coefficient d\'avance J = Va/(nD)')
ax.set_ylabel('KT, 10·KQ, η')
ax.set_title('Courbes de performance en eau libre')
ax.legend()
ax.grid(True)
plt.tight_layout()
plt.savefig('courbes_eau_libre.png', dpi=150)
plt.show()
```

---

## 12. Annexe — Pour aller plus loin : Comparaison des approches de simulation

> Cette annexe présente les trois grandes méthodes de simulation d'un propulseur sous OpenFOAM, du plus simple au plus avancé, pour permettre une comparaison éclairée et servir de feuille de route vers des simulations plus réalistes.

---

### A. Vue d'ensemble des trois approches

| Critère | MRF (steady) | Sliding Grid / AMI (transitoire) | Overset / Chimère (transitoire) |
|---|---|---|---|
| **Solveur OpenFOAM** | `simpleFoam` | `pimpleFoam` + `pimpleDyMFoam` | `overPimpleDyMFoam` |
| **Type de maillage** | Fixe avec zone tournante fictive | Deux zones jointives glissantes | Deux maillages superposés indépendants |
| **Rotation simulée** | Fictive (cadre de référence) | Réelle (interface AMI glissante) | Réelle (interpolation overset) |
| **Instationnaire** | Non (moyenné en temps) | Oui | Oui |
| **Qualité résultats KT/KQ** | Bonne pour J nominal | Très bonne | Excellente |
| **Effets de sillage** | Approchés | Réels | Réels |
| **Complexité mise en œuvre** | Faible ✅ | Modérée | Élevée |
| **Coût calcul** | Faible ✅ | Modéré | Élevé |
| **Cas d'usage typique** | TP, design préliminaire | Eau libre précise, certification | Manœuvre, cavitation, couplage carène |
| **Cas tutoriel natif v2412** | ✅ `pimpleFoam/RAS/propeller` | ✅ `pimpleDyMFoam/propeller` | ✅ `overPimpleDyMFoam/propeller` |

---

### B. Approche 1 — MRF (Moving Reference Frame)

#### Principe

Le maillage ne bouge pas. On ajoute un **terme de force fictive** (Coriolis + centrifuge) dans les équations de Navier-Stokes dans une zone cylindrique entourant l'hélice. C'est une hypothèse de **régime permanent** : on calcule comme si tout était figé dans un repère tournant.

```
Domaine fixe
┌─────────────────────────────────────┐
│                                     │
│   ┌─────────────────┐               │
│   │  Zone MRF       │               │
│   │  (fictive)      │               │
│   │  forces Coriolis│               │
│   │  + centrifuge   │               │
│   └─────────────────┘               │
│                                     │
└─────────────────────────────────────┘
Aucune cellule ne bouge réellement.
```

#### Quand l'utiliser

- Design préliminaire d'une hélice
- Courbe KT-KQ pour un seul point de fonctionnement J
- Ressources de calcul limitées
- TP et formations

#### Fichier clé : `constant/MRFProperties`

```cpp
MRF1
{
    cellZone        rotating;
    active          yes;
    origin          (0 0 0);
    axis            (1 0 0);
    omega           125.66;     // rad/s = 20 tr/s
}
```

#### Limitations

- Ne capture pas les effets instationnaires (passage de pale)
- Sillage non physique en aval
- Erreurs croissantes aux J faibles (forte charge)

---

### C. Approche 2 — Sliding Grid / AMI (Arbitrary Mesh Interface)

#### Principe

Le domaine est découpé en **deux zones jointives** séparées par une **interface cylindrique**. La zone intérieure (hélice) tourne réellement à chaque pas de temps. Les valeurs sont interpolées à travers l'interface AMI par projection sur les faces glissantes.

```
Domaine fixe (extérieur)
┌──────────────────────────────────────┐
│                 ┆                    │
│   ┌─────────────┆──────────┐         │
│   │  Zone AMI   ┆ tournante│         │
│   │        ↺    ┆          │         │
│   │  Interface AMI (cylindre)        │
│   └─────────────┆──────────┘         │
│                 ┆                    │
└──────────────────────────────────────┘
Interface commune — les cellules restent jointives.
```

#### Quand l'utiliser

- Courbe KT-KQ complète (plusieurs J)
- Analyse du sillage en aval de l'hélice
- Étude des effets de passage de pale (fluctuations de pression)
- Résultats de qualité pour rapport ou certification

#### Fichier clé : `constant/dynamicMeshDict`

```cpp
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      dynamicMeshDict;
}

dynamicFvMesh   dynamicMotionSolverFvMesh;

motionSolverLibs ("libfvMotionSolvers.so");

motionSolver    solidBody;

solidBodyMotionFunctions
{
    propellerRotation
    {
        solidBodyMotionFunction  rotatingMotion;
        rotatingMotionCoeffs
        {
            origin      (0 0 0);
            axis        (1 0 0);
            omega       125.66;     // rad/s
        }
    }
}
```

#### Fichier clé : interface AMI dans `constant/polyMesh/boundary`

```cpp
// Les deux faces de l'interface doivent être de type cyclicAMI
AMI_rotating_to_static
{
    type            cyclicAMI;
    neighbourPatch  AMI_static_to_rotating;
    transform       noOrdering;
}
AMI_static_to_rotating
{
    type            cyclicAMI;
    neighbourPatch  AMI_rotating_to_static;
    transform       noOrdering;
}
```

#### Lancement

```bash
cp -r $FOAM_TUTORIALS/incompressible/pimpleDyMFoam/propeller $FOAM_RUN/propeller_AMI
cd $FOAM_RUN/propeller_AMI
./Allrun
```

#### Limitations

- L'interface AMI doit être **strictement cylindrique** et bien alignée
- Difficile à mettre en œuvre si la géométrie est complexe (carène + hélice)
- Pas adapté aux mouvements non-rotatifs

---

### D. Approche 3 — Overset / Chimère

#### Principe

Deux maillages **complètement indépendants** se superposent dans l'espace. Le maillage rotatif (hélice) est posé par-dessus le maillage de fond fixe. Les cellules du fond recouvertes par le maillage rotatif sont **désactivées** (holes). Les valeurs sont interpolées en 3D aux frontières de superposition.

```
Maillage de fond (fixe)
┌──────────────────────────────────────┐
│                                      │
│    ┌────────────────────┐            │
│    │  Maillage rotatif  │            │
│    │  (indépendant)     │            │
│    │        ↺           │            │
│    │  [HOLES dans fond] │            │
│    └────────────────────┘            │
│                                      │
└──────────────────────────────────────┘
Les deux maillages se superposent — interpolation volumique.
```

#### Cas tutoriel natif : KP505 (OpenFOAM ESI v2412)

Le propulseur **KP505** est une géométrie publique issue de la campagne SIMMAN 2008, utilisée comme référence internationale pour la validation des codes CFD navals.

| Paramètre | Valeur |
|---|---|
| Solveur | `overPimpleDyMFoam` |
| Géométrie | KP505 (5 pales, D = 0.25 m) |
| Vitesse de rotation | 100 rad/s (≈ 955 tr/min) |
| Vitesse d'avance | Variable (plusieurs J) |
| Version OpenFOAM | ESI v2406+ (compatible v2412) |

```bash
# Trouver le tutoriel KP505 dans v2412
find $FOAM_TUTORIALS -name "*KP505*" -o -name "*overset*propeller*" 2>/dev/null

# Chemin probable :
ls $FOAM_TUTORIALS/incompressible/overPimpleDyMFoam/propeller/
```

#### Fichier clé : `constant/dynamicMeshDict`

```cpp
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      dynamicMeshDict;
}

dynamicFvMesh       dynamicOversetFvMesh;

solver              solidBody;

solidBodyMotionFunctions
{
    propellerRotation
    {
        solidBodyMotionFunction  rotatingMotion;
        rotatingMotionCoeffs
        {
            origin      (0 0 0);
            axis        (1 0 0);        // Axe X = axe de l'arbre
            omega       100;            // rad/s
        }
    }
}
```

#### Fichier clé : zones overset dans `system/topoSetDict`

```cpp
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      topoSetDict;
}

actions
(
    {
        name    overset;
        type    cellSet;
        action  new;
        source  cylinderToCell;
        sourceInfo
        {
            p1      (-0.1 0 0);
            p2      ( 0.3 0 0);
            radius  0.2;
        }
    }
    {
        name    overset;
        type    cellZoneSet;
        action  new;
        source  setToCellZone;
        sourceInfo { set overset; }
    }
);
```

#### Condition limite overset dans `0/U`

```cpp
overset
{
    type            overset;
    value           uniform (0 0 0);
}
```

#### Lancement

```bash
# Décomposition des deux maillages
decomposePar -allRegions

# Lancement parallèle (coûteux — prévoir 8+ cœurs)
mpirun -np 8 overPimpleDyMFoam -parallel 2>&1 | tee log.overPimpleDyMFoam

# Reconstruction
reconstructPar -allRegions
```

#### Quand l'utiliser

- Propulseur derrière une carène (géométries incompatibles pour AMI)
- Simulation de manœuvre (rotation + translation simultanées)
- Hélices contrarotatives (deux rotors en sens opposés)
- Couplage avec surface libre (`overInterDyMFoam`)
- Résultats de recherche et validation internationale

#### Limitations

- Mise en œuvre complexe (deux maillages, zones holes, interpolation)
- Temps de calcul nettement plus élevé (~3× AMI)
- Sensible à la qualité de l'interpolation dans les zones de superposition

---

### E. Tableau de décision — Quelle approche choisir ?

```
Mon objectif est...
│
├─ Comprendre le cas / TP / design rapide
│   └──► MRF (pimpleFoam/RAS/propeller)  ✅ commencer ici
│
├─ Courbe KT-KQ complète + sillage précis
│   └──► Sliding Grid AMI (pimpleDyMFoam/propeller)
│
├─ Propulseur + carène, manœuvre, cavitation, recherche
│   └──► Overset Chimère (overPimpleDyMFoam/propeller KP505)
```

---

### F. Comparaison des résultats attendus

| Grandeur | MRF | AMI | Overset |
|---|---|---|---|
| KT moyen | ✅ Bon | ✅✅ Très bon | ✅✅✅ Référence |
| KQ moyen | ✅ Bon | ✅✅ Très bon | ✅✅✅ Référence |
| Fluctuations de pression | ❌ Non | ✅ Oui | ✅ Oui |
| Sillage aval | ❌ Approché | ✅ Réel | ✅ Réel |
| Interaction carène-hélice | ❌ Impossible | ⚠️ Difficile | ✅ Naturel |
| Temps de calcul (relatif) | 1× | 5-10× | 15-30× |

---

## 13. Référence des fichiers de configuration

### Résumé des paramètres physiques clés

| Paramètre | Symbole | Valeur typique | Unité OpenFOAM |
|---|---|---|---|
| Viscosité cinématique eau | ν | 1×10⁻⁶ | `[0 2 -1 0 0 0 0]` |
| Densité eau | ρ | 1000 | `rhoInf` dans controlDict |
| Vitesse d'avance | Va | 1.0 | m/s |
| Vitesse rotation | n | 20 tr/s | ω = 125.66 rad/s |
| Diamètre hélice | D | 0.25 | m |
| Coeff. avance | J | 0.2 à 1.0 | adimensionnel |

### Formules des coefficients de performance

```
Coefficient de poussée   : KT = T / (ρ × n² × D⁴)
Coefficient de couple    : KQ = Q / (ρ × n² × D⁵)
Coefficient d'avance     : J  = Va / (n × D)
Rendement propulsif      : η  = J × KT / (2π × KQ)
```

### Nombre de Reynolds de l'hélice

```
Re = Va × D / ν = 1.0 × 0.25 / 1e-6 = 250 000
```

---

## 14. Commandes utiles OpenFOAM

### Navigation et environnement

```bash
# Variables d'environnement importantes
echo $FOAM_TUTORIALS      # Chemin des tutoriels
echo $FOAM_RUN            # Répertoire de travail utilisateur
echo $FOAM_SOLVERS        # Chemin des solveurs compilés

# Aller rapidement dans le répertoire de run
run                       # Alias OpenFOAM = cd $FOAM_RUN
tut                       # Alias = cd $FOAM_TUTORIALS
```

### Maillage

```bash
blockMesh                 # Générer le maillage de fond
snappyHexMesh -overwrite  # Raffiner autour des surfaces
checkMesh                 # Vérifier la qualité du maillage
checkMesh -allTopology    # Vérification complète
surfaceFeatureExtract     # Extraire les arêtes des STL
```

### Calcul

```bash
pimpleFoam                          # Lancer le calcul (séquentiel)
pimpleFoam 2>&1 | tee log.solver    # Avec sauvegarde des logs
foamRun -solver pimpleFoam          # Syntaxe alternative ESI v2412
decomposePar                        # Décomposer pour parallèle
mpirun -np 4 pimpleFoam -parallel   # Lancement parallèle
reconstructPar                      # Reconstruire après parallèle
```

### Post-traitement

```bash
paraFoam &                          # Ouvrir ParaView (si installé WSL)
foamToVTK                           # Convertir en VTK
postProcess -func forceCoeffs       # Recalculer une fonction
foamLog log.pimpleFoam              # Extraire les résidus du log
gnuplot                             # Tracer les courbes de résidus
```

### Gestion des cas

```bash
foamCleanCase                       # Nettoyer un cas (garder 0/ et constant/)
foamCleanTutorials                  # Nettoyer tous les tutoriels
cp -r $FOAM_TUTORIALS/... .         # Copier un tutoriel
./Allrun                            # Lancer le script de calcul complet
./Allclean                          # Nettoyer un cas
```

---

## 15. Dépannage

### Problèmes fréquents sous WSL

**OpenFOAM non trouvé après installation :**
```bash
source /usr/lib/openfoam/openfoam2412/etc/bashrc
# Si le chemin est différent :
find /usr -name "bashrc" 2>/dev/null | grep openfoam
```

**ParaView ne s'affiche pas depuis WSL :**
```bash
# Vérifier le display
echo $DISPLAY

# Si vide, configurer (pour VcXsrv lancé sous Windows) :
export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0
export LIBGL_ALWAYS_INDIRECT=1
```

**Mémoire insuffisante pour snappyHexMesh :**
```bash
# Augmenter la mémoire WSL dans C:\Users\<user>\.wslconfig
[wsl2]
memory=8GB
processors=4

# Redémarrer WSL
wsl --shutdown
```

**Erreur "face orientation" dans checkMesh :**
```bash
# Corriger l'orientation des normales STL
surfaceOrient constant/triSurface/propeller.stl constant/triSurface/propeller_oriented.stl true
```

**Calcul diverge (CFL > 1) :**
```bash
# Réduire le pas de temps dans controlDict
# Passer de deltaT 0.001 à 0.0005
# Ou utiliser le contrôle automatique du CFL :
adjustTimeStep  yes;
maxCo           0.8;
maxDeltaT       0.005;
```

**Forces nulles dans les résultats :**
```bash
# Vérifier que les noms de patches dans controlDict correspondent
# à ceux dans constant/polyMesh/boundary
cat constant/polyMesh/boundary | grep -A3 "propeller"
```

### Vérification rapide de santé du cas

```bash
# Script de vérification rapide
echo "=== Version OpenFOAM ==="
foamVersion

echo "=== Maillage ==="
checkMesh 2>&1 | grep -E "(cells|faces|Mesh OK|FAILED|non-orthogonality)"

echo "=== Patches disponibles ==="
foamListTimes
cat constant/polyMesh/boundary

echo "=== Logs de calcul ==="
tail -20 log.pimpleFoam 2>/dev/null || echo "Pas encore de log de calcul"
```

---

## Ressources complémentaires

| Ressource | Lien |
|---|---|
| Documentation officielle OpenFOAM ESI | https://www.openfoam.com/documentation/user-guide |
| Tutoriels GitHub OpenFOAM Foundation | https://github.com/OpenFOAM/OpenFOAM-7/tree/master/tutorials |
| Tutoriels OpenFOAM ESI (GitLab) | https://develop.openfoam.com/Development/openfoam/-/tree/master/tutorials |
| CFD-Training : tutoriel KP505 overset | https://cfd-training.com/produit/openfoam-tutorial-open-water-propeller-kp-505overset-mesh/ |
| Article Chalmers (propulseur naval OpenFOAM) | https://publications.lib.chalmers.se/records/fulltext/201623/local_201623.pdf |
| Forum CFD Online OpenFOAM | https://www.cfd-online.com/Forums/openfoam/ |
| Wiki OpenFOAM | https://openfoamwiki.net |

---

*Document généré pour OpenFOAM ESI v2412 sous WSL Ubuntu 24.04 / Windows 11*
