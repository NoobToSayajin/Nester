# Étapes

## 1. Création de l'Utilisateur

- **Commande** :

  ```bash
  sudo useradd -m -s /bin/nologin monutilisateur
  ```

  - L'option `-m` crée un répertoire personnel pour l'utilisateur.
  - L'option `-s /sbin/nologin` définit le shell de l'utilisateur sur `/sbin/nologin`, ce qui empêche l'utilisateur de se connecter.

- **Répertoire `/home`** :

  ```bash
  sudo mkdir /home/monutilisateur
  sudo chown monutilisateur:monutilisateur /home/monutilisateur
  ```

  - **Explication** : Crée un répertoire `/home` pour l'utilisateur et lui attribue les droits nécessaires pour y écrire.

## 2. Préparation du Script

- **Emplacement** : `/home/monutilisateur/setup_and_run.sh`
- **Permissions** :

  ```bash
  sudo chmod +x /home/monutilisateur/setup_and_run.sh
  ```

  - **Explication** : Rend le script exécutable.

- **Contenu du Script** :

  ```bash
  #!/bin/bash

  # Répertoire du projet
  PROJECT_DIR="/chemin/vers/votre/projet"
  REPO_URL="https://github.com/utilisateur/depot.git"
  VENV_DIR="$PROJECT_DIR/venv"

  # Vérifier si le répertoire du projet est un dépôt Git
  if [ ! -d "$PROJECT_DIR/.git" ]; then
    # Si ce n'est pas un dépôt Git, cloner le dépôt
    echo "Le répertoire n'est pas un dépôt Git. Clonage du dépôt..."
    git clone "$REPO_URL" "$PROJECT_DIR"
  else
    # Si c'est un dépôt Git, mettre à jour le dépôt
    echo "Le répertoire est un dépôt Git. Mise à jour du dépôt..."
    cd "$PROJECT_DIR"
    git pull origin main
  fi

  # Vérifier si l'environnement virtuel existe
  if [ ! -d "$VENV_DIR" ]; then
    # Si l'environnement virtuel n'existe pas, le créer
    echo "L'environnement virtuel n'existe pas. Création d'un nouvel environnement virtuel..."
    python3.13 -m venv "$VENV_DIR"
  fi

  # Activer l'environnement virtuel
  source "$VENV_DIR/bin/activate"

  # Installer les dépendances
  pip install -r requirements.txt

  # Lancer l'application
  python app.py
  ```

  - **Explication détaillée** :
    - **Variables** :
      - `PROJECT_DIR` : Chemin vers le répertoire du projet.
      - `REPO_URL` : URL du dépôt Git à cloner.
      - `VENV_DIR` : Chemin vers l'environnement virtuel.

    - **Vérification du dépôt Git** :
      - `if [ ! -d "$PROJECT_DIR/.git" ]; then` : Vérifie si le sous-répertoire `.git` n'existe pas dans `PROJECT_DIR`. Si c'est le cas, cela signifie que le répertoire n'est pas un dépôt Git.
      - `git clone "$REPO_URL" "$PROJECT_DIR"` : Clone le dépôt Git dans `PROJECT_DIR` si ce n'est pas déjà un dépôt Git.
      - `else` : Si le répertoire est un dépôt Git, il se déplace dans `PROJECT_DIR` et exécute `git pull` pour mettre à jour le dépôt avec les dernières modifications de la branche `main`.

    - **Gestion de l'environnement virtuel** :
      - `if [ ! -d "$VENV_DIR" ]; then` : Vérifie si le répertoire de l'environnement virtuel n'existe pas.
      - `python3.13 -m venv "$VENV_DIR"` : Crée un nouvel environnement virtuel en utilisant Python 3.13 si le répertoire n'existe pas.

    - **Activation de l'environnement virtuel** :
      - `source "$VENV_DIR/bin/activate"` : Active l'environnement virtuel pour que les commandes suivantes soient exécutées dans cet environnement.

    - **Installation des dépendances** :
      - `pip install -r requirements.txt` : Utilise `pip` pour installer les dépendances Python listées dans le fichier `requirements.txt`.

    - **Lancement de l'application** :
      - `python app.py` : Exécute le script principal de l'application (`app.py`) dans l'environnement virtuel activé.

## 3. Configuration du Service `systemd`

- **Fichier de service** : `/etc/systemd/system/monapp.service`
- **Contenu** :

  ```ini
  [Unit]
  Description=Mon Application Python
  After=network.target

  [Service]
  ExecStart=/home/monutilisateur/setup_and_run.sh
  WorkingDirectory=/chemin/vers/votre/projet
  Restart=always
  User=monutilisateur
  Environment="PATH=/usr/local/bin/python3.13:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

  [Install]
  WantedBy=multi-user.target
  ```

  - **Explication** :
    - **ExecStart** : Chemin vers le script à exécuter.
    - **User** : Le service s'exécute sous l'utilisateur `monutilisateur`.
    - **Restart** : Redémarre automatiquement le service en cas de plantage.
    - **Environment** : Assure que le chemin vers Python 3.13 est correct.

## 4. Gestion du Service

- **Recharger `systemd`** :

  ```bash
  sudo systemctl daemon-reload
  ```

- **Démarrer le service** :

  ```bash
  sudo systemctl start monapp.service
  ```

- **Activer au démarrage** :

  ```bash
  sudo systemctl enable monapp.service
  ```

- **Vérifier le statut** :

  ```bash
  sudo systemctl status monapp.service
  ```

### Explications

- **Sécurité** : L'utilisateur dédié ne peut pas se connecter interactivement, réduisant ainsi les risques de sécurité.
- **Automatisation** : Le script automatise les tâches de mise à jour du dépôt Git, de gestion de l'environnement virtuel, et de lancement de l'application.
- **Gestion des Services** : `systemd` assure que le script est exécuté au démarrage et redémarre le service en cas de plantage, garantissant ainsi la disponibilité de l'application.
