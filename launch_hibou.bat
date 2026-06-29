@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
set "SCRIPT_NAME=hibou_automation.py"
set "STREAMLIT_APP=app_streamlit.py"
set "SCRIPT_PATH=%SCRIPT_DIR%%SCRIPT_NAME%"
set "STREAMLIT_PATH=%SCRIPT_DIR%%STREAMLIT_APP%"
set "VENV_DIR=%SCRIPT_DIR%.venv"
set "VENV_PYTHON=%VENV_DIR%\Scripts\python.exe"
set "VENV_STREAMLIT=%VENV_DIR%\Scripts\streamlit.exe"

if not exist "%SCRIPT_PATH%" (
    echo Script Python introuvable : %SCRIPT_PATH%
    pause
    exit /b 1
)

if not exist "%STREAMLIT_PATH%" (
    echo Interface Streamlit introuvable : %STREAMLIT_PATH%
    pause
    exit /b 1
)

where py >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    set "PYTHON_CMD=py"
    set "PYTHON_ARGS=-3"
) else (
    where python >nul 2>nul
    if %ERRORLEVEL% EQU 0 (
        set "PYTHON_CMD=python"
        set "PYTHON_ARGS="
    ) else (
        echo Python non detecte. Installation en cours...
        winget install --id Python.Python.3.11 -e --source winget
        if %ERRORLEVEL% NEQ 0 (
            echo Echec de l'installation de Python. Installez Python manuellement puis relancez ce script.
            pause
            exit /b 1
        )
        where py >nul 2>nul
        if %ERRORLEVEL% EQU 0 (
            set "PYTHON_CMD=py"
            set "PYTHON_ARGS=-3"
        ) else (
            where python >nul 2>nul
            if %ERRORLEVEL% EQU 0 (
                set "PYTHON_CMD=python"
                set "PYTHON_ARGS="
            ) else (
                echo Python toujours introuvable apres installation.
                pause
                exit /b 1
            )
        )
    )
)

if not exist "%VENV_PYTHON%" (
    echo Creation de l'environnement virtuel dans %VENV_DIR%...
    %PYTHON_CMD% %PYTHON_ARGS% -m venv "%VENV_DIR%"
    if %ERRORLEVEL% NEQ 0 (
        echo Echec de la creation de l'environnement virtuel.
        pause
        exit /b 1
    )
)

echo Installation des dependances dans l'environnement virtuel...
"%VENV_PYTHON%" -m pip install --upgrade pip
"%VENV_PYTHON%" -m pip install selenium streamlit pandas pynput
if %ERRORLEVEL% NEQ 0 (
    echo Echec de l'installation des dependances.
    pause
    exit /b 1
)

echo Lancement de l'interface Streamlit depuis l'environnement virtuel...
"%VENV_STREAMLIT%" run "%STREAMLIT_PATH%"

if %ERRORLEVEL% NEQ 0 (
    echo L'interface Streamlit s'est terminee avec une erreur.
)

pause
endlocal
