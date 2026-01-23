#!/bin/bash

conda init

conda env create -f environment.yml


if [[ "$SHELL" == */zsh ]]; then
    SHELL_CONFIG="$HOME/.zshrc"
elif [[ "$SHELL" == */bash ]]; then
    SHELL_CONFIG="$HOME/.bashrc"
elif [[ "$SHELL" == */fish ]]; then
    SHELL_CONFIG="$HOME/.config/fish/config.fish"
else
    echo "Shell no reconocida, carga manualmente tu configuración."
    exit 1
fi

source "$SHELL_CONFIG"

conda activate Seminario_EM


