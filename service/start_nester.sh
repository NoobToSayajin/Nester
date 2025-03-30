#!/bin/bash

# Répertoire du projet
PROJECT_DIR="/usr/local/bin/nester"
REPO_URL="http://10.2.0.106/mspr/nester"
VENV_DIR="$PROJECT_DIR/.venv"

if [ ! -d "$PROJECT_DIR/.git" ]; then
        # Si le depot nexiste pas, clone du depot
        echo "Le dépot n'existe pas. Clonage du dépôt..."
        git clone "$REPO_URL" "$PROJECT_DIR"
else
        # Si le repertoire existe, mise a jour du depot
        echo "Le répertoire existe. Mise à jour du dépôt..."
        cd "$PROJECT_DIR"
        git pull mspr main
fi

# Vérifier si l'environnement virtuel existe
if [ ! -d "$VENV_DIR" ]; then
  # Si l environnement virtuel n existe pas, le creer
  echo "L'environnement virtuel n'existe pas. Création d'un nouvel environnement virtuel avec python3.13..."
  python3.13 -m venv "$VENV_DIR"
fi

# Activer l'environnement virtuel
source $VENV_DIR/bin/activate

# Installer les dépendances
pip install -r requirements

# Lancer l'application
python nester.py