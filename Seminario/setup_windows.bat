@echo off
TITLE Instalador y Lanzador - Seminario Modelizacion Grupo 4
CLS

ECHO ======================================================
ECHO    INICIANDO CONFIGURACION DEL PROYECTO
ECHO    Seminario de Modelizacion - Grupo 4
ECHO ======================================================
ECHO.

:: 1. Verificar si Conda esta instalado
WHERE conda >nul 2>nul
IF %ERRORLEVEL% NEQ 0 (
    ECHO [ERROR] No se ha encontrado 'conda'.
    ECHO Por favor, instale Anaconda o Miniconda antes de continuar.
    ECHO Descarga: https://docs.conda.io/en/latest/miniconda.html
    PAUSE
    EXIT /B
)

:: 2. Inicializar Conda para la sesion actual
:: Esto es necesario para que 'conda activate' funcione en el script bat
FOR /F "tokens=*" %%g IN ('where conda') DO (
    SET CONDA_PATH=%%~dpg
)
IF EXIST "%CONDA_PATH%..\Scripts\activate.bat" (
    CALL "%CONDA_PATH%..\Scripts\activate.bat"
) ELSE (
    ECHO [AVISO] Intentando activar base por metodo alternativo...
    CALL conda activate base
)

:: 3. Verificar si el entorno ya existe
conda info --envs | findstr "Seminario_EM" >nul
IF %ERRORLEVEL% EQU 0 (
    ECHO [INFO] El entorno 'Seminario_EM' ya existe.
) ELSE (
    ECHO [INFO] Creando el entorno virtual 'Seminario_EM'...
    ECHO Esto puede tardar unos minutos dependiendo de su conexion.
    conda env create -f environment.yml
    IF %ERRORLEVEL% NEQ 0 (
        ECHO [ERROR] Fallo al crear el entorno. Revise el archivo environment.yml.
        PAUSE
        EXIT /B
    )
)

:: 4. Activar entorno y ejecutar
ECHO.
ECHO [INFO] Activando entorno...
CALL conda activate Seminario_EM

ECHO [INFO] Lanzando la aplicacion...
streamlit run Home.py

PAUSE