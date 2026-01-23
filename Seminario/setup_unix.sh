#!/bin/bash

# Titulo
echo "======================================================"
echo "   INICIANDO CONFIGURACION DEL PROYECTO"
echo "   Seminario de Modelizacion - Grupo 4"
echo "======================================================"
echo ""

# 1. Verificar si Conda esta instalado
if ! command -v conda &> /dev/null
then
    echo "[ERROR] No se ha encontrado 'conda'."
    echo "Por favor, instale Anaconda o Miniconda antes de continuar."
    exit 1
fi

# 2. Inicializar Conda en el subshell script
# Intentamos encontrar la ruta base de conda
CONDA_BASE=$(conda info --base)
source "$CONDA_BASE/etc/profile.d/conda.sh"

# 3. Verificar o Crear el entorno
if conda info --envs | grep -q "Seminario_EM"; then
    echo "[INFO] El entorno 'Seminario_EM' ya existe."
    echo "[INFO] Verificando actualizaciones de dependencias..."
    conda env update -f environment.yml --prune
else
    echo "[INFO] Creando el entorno virtual 'Seminario_EM'..."
    echo "Esto puede tardar unos minutos..."
    conda env create -f environment.yml
fi

# 4. Activar y Ejecutar
echo ""
echo "[INFO] Activando entorno..."
conda activate Seminario_EM

echo "[INFO] Lanzando la aplicacion..."
streamlit run Home.py