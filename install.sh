#!/usr/bin/env bash
set -e

# Script de instalação / ativação das skills de finanças para Antigravity / Gemini CLI

TARGET_DIR=""

if [[ "$1" == "--global" ]]; then
    TARGET_DIR="$HOME/.gemini/config/skills"
    echo "Instalando skills globalmente em: $TARGET_DIR"
else
    TARGET_DIR="$(pwd)/.gemini/skills"
    echo "Instalando skills localmente no workspace em: $TARGET_DIR"
fi

mkdir -p "$TARGET_DIR"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_DIR="$SCRIPT_DIR/skills"

for skill in "$SKILLS_DIR"/*; do
    if [ -d "$skill" ]; then
        skill_name="$(basename "$skill")"
        dest="$TARGET_DIR/$skill_name"
        if [ -L "$dest" ] || [ -d "$dest" ]; then
            rm -rf "$dest"
        fi
        ln -s "$skill" "$dest"
        echo "  ✓ Link criado: $skill_name -> $dest"
    fi
done

echo ""
echo "Sucesso! As skills de finanças estão ativas e disponíveis."
echo "Para instalar globalmente em qualquer projeto, execute: ./install.sh --global"
