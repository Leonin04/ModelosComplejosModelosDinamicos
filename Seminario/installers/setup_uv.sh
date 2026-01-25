#!/bin/bash

# ======================================================
#   INSTALACION ULTRA-RAPIDA CON UV (LINUX/MAC)
#   Seminario de Modelizacion - Grupo 4
# ======================================================

# 1. Moverse al directorio padre (Raíz del proyecto 'Seminario')
cd "$(dirname "$0")/.." || exit

echo "Directorio de trabajo: $(pwd)"
echo ""

# 2. Verificar si uv está instalado
if ! command -v uv &> /dev/null
then
    echo "[INFO] 'uv' no encontrado."
    echo "[INFO] Instalando 'uv' mediante el instalador oficial (standalone)..."
    
    # Usamos el script oficial de instalación (evita el error de pip externally-managed)
    if command -v curl &> /dev/null; then
        curl -LsSf https://astral.sh/uv/install.sh | sh
        
        # Cargamos las variables de entorno para poder usar uv inmediatamente
        # uv suele instalarse en ~/.cargo/bin o ~/.local/bin
        if [ -f "$HOME/.cargo/env" ]; then
            source "$HOME/.cargo/env"
        else
            export PATH="$HOME/.local/bin:$PATH"
            export PATH="$HOME/.cargo/bin:$PATH"
        fi
    else
        echo "[ERROR] No tienes 'curl' instalado. Por favor instala 'uv' manualmente."
        echo "Comando: curl -LsSf https://astral.sh/uv/install.sh | sh"
        exit 1
    fi
fi

# 3. Crear entorno virtual (si no existe)
if [ ! -d ".venv" ]; then
    echo "[INFO] Creando entorno virtual (.venv)..."
    # Forzamos el uso de python3 para crear el venv si uv falla al encontrarlo
    uv venv --python python3
fi

# 4. Activar el entorno
source .venv/bin/activate

# 5. Sincronizar librerías
echo "[INFO] Instalando dependencias a velocidad luz..."
uv pip install -r requirements.txt

# 6. Ejecutar
echo ""
echo "[EXITO] Lanzando aplicación..."
streamlit run Home.py