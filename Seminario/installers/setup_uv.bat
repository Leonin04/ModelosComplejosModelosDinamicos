@echo off
TITLE Instalador Rapido (UV) - Seminario Grupo 4
CLS

:: 1. Moverse al directorio raiz del proyecto (Seminario)
cd /d "%~dp0.."
ECHO Directorio de trabajo: %CD%
ECHO.

ECHO ======================================================
ECHO   INSTALACION ULTRA-RAPIDA CON UV (WINDOWS)
ECHO ======================================================

:: 2. Verificar si uv existe
WHERE uv >nul 2>nul
IF %ERRORLEVEL% NEQ 0 (
    ECHO [INFO] 'uv' no encontrado. Descargando instalador oficial...
    
    :: Usamos PowerShell para instalar uv sin depender de pip
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    
    :: Actualizamos el PATH para la sesion actual (truco para no reiniciar consola)
    SET "PATH=%USERPROFILE%\.cargo\bin;%LOCALAPPDATA%\bin;%PATH%"
)

:: 3. Crear entorno virtual
IF NOT EXIST ".venv" (
    ECHO [INFO] Creando entorno virtual...
    :: Si no encuentra python, uv intentara descargar uno automaticamente
    uv venv
)

:: 4. Activar entorno (Windows usa Scripts\activate)
CALL .venv\Scripts\activate

:: 5. Sincronizar librerias
ECHO [INFO] Instalando dependencias a velocidad luz...
uv pip install -r requirements.txt

:: 6. Ejecutar
ECHO.
ECHO [EXITO] Lanzando aplicacion...
streamlit run Home.py

PAUSE