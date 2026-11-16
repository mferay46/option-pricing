#!/bin/zsh

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR" || exit 1

if [[ ! -x ".venv/bin/python" ]]; then
    echo "L’environnement Python du projet est introuvable."
    echo "Ouvre Terminal dans le dossier du projet et installe les dépendances avec :"
    echo "python3 -m venv .venv && .venv/bin/python -m pip install -r requirements.txt"
    read -r "REPLY?Appuie sur Entrée pour fermer..."
    exit 1
fi

export PYTHONPATH="$PROJECT_DIR/src"
exec "$PROJECT_DIR/.venv/bin/python" -m option_pricing.gui
