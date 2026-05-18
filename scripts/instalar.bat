@echo off
title FoodStore - Instalacion Completa
setlocal enabledelayedexpansion

:: ============================================
::  FOOD STORE - Instalacion de Dependencias
::  Ejecutar como Administrador
:: ============================================

:: --- Obtener directorio raiz del proyecto ---
for %%I in ("%~dp0..") do set "ROOT=%%~fI"

:: --- Verificar permisos de Administrador ---
net session >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ============================================
    echo   ERROR: Se requieren permisos de Administrador
    echo ============================================
    echo.
    echo Haga clic derecho sobre este archivo y seleccione
    echo "Ejecutar como administrador".
    echo.
    pause
    exit /b 1
)

cls
echo ============================================
echo    FOOD STORE - Instalacion Completa
echo ============================================
echo.
echo Proyecto: %ROOT%
echo.
echo Este script instalara TODAS las dependencias
echo necesarias para ejecutar el proyecto.
echo.

:: Contador de errores
set ERRORS=0

:: ============================================
::  0. Verificar herramientas base
:: ============================================
echo [---] Verificando herramientas base...
echo.

:: Python
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo   [FAIL] Python no encontrado. Instale Python 3.12+ desde python.org
    set /a ERRORS+=1
) else (
    for /f "delims=" %%v in ('python --version 2^>^&1') do echo   [OK] %%v
)

:: Node
where node >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo   [FAIL] Node.js no encontrado. Instale Node 18+ desde nodejs.org
    set /a ERRORS+=1
) else (
    for /f "delims=" %%v in ('node --version') do echo   [OK] Node.js %%v
)

:: npm
where npm >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo   [FAIL] npm no encontrado.
    set /a ERRORS+=1
) else (
    for /f "delims=" %%v in ('npm --version') do echo   [OK] npm %%v
)

:: PostgreSQL service
sc query postgresql-x64-18 >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo   [WARN] Servicio postgresql-x64-18 no encontrado.
    echo         Verifique que PostgreSQL 18 este instalado.
) else (
    echo   [OK] Servicio PostgreSQL encontrado.
)

echo.

:: Si faltan herramientas base, abortar
if %ERRORS% gtr 0 (
    echo ============================================
    echo   ERRORES CRITICOS: Instale las herramientas
    echo   faltantes y vuelva a ejecutar este script.
    echo ============================================
    pause
    exit /b 1
)

:: ============================================
::  1. BACKEND - Python Virtual Environment
:: ============================================
echo ============================================
echo   1/4 - BACKEND: Entorno Virtual
echo ============================================
echo.

set "VENV_DIR=%ROOT%\backend\.venv"

if exist "%VENV_DIR%" (
    echo   [OK] Entorno virtual ya existe.
) else (
    echo   [....] Creando entorno virtual...
    python -m venv "%VENV_DIR%"
    if !ERRORLEVEL! equ 0 (
        echo   [OK] Entorno virtual creado.
    ) else (
        echo   [FAIL] Error al crear el entorno virtual.
        set /a ERRORS+=1
    )
)
echo.

:: ============================================
::  2. BACKEND - Python Dependencies
:: ============================================
echo ============================================
echo   2/4 - BACKEND: Dependencias Python
echo ============================================
echo.

echo   Instalando dependencias desde requirements.txt...
echo   (Esto puede tomar varios minutos)
echo.
"%VENV_DIR%\Scripts\python.exe" -m pip install --upgrade pip >nul 2>&1
"%VENV_DIR%\Scripts\pip.exe" install -r "%ROOT%\backend\requirements.txt"
if !ERRORLEVEL! equ 0 (
    echo.
    echo   [OK] Dependencias Python instaladas.
) else (
    echo.
    echo   [FAIL] Error instalando dependencias Python.
    set /a ERRORS+=1
)
echo.

:: ============================================
::  3. BACKEND - Configuracion .env
:: ============================================
echo ============================================
echo   3/4 - BACKEND: Archivo .env
echo ============================================
echo.

if exist "%ROOT%\backend\.env" (
    echo   [OK] backend\.env ya existe.
) else (
    echo   [WARN] backend\.env NO encontrado.
    echo.
    echo   Creando backend\.env desde .env.example...
    copy "%ROOT%\backend\.env.example" "%ROOT%\backend\.env" >nul
    if !ERRORLEVEL! equ 0 (
        echo   [OK] backend\.env creado.
        echo   [i] Revise y ajuste las credenciales en backend\.env
    ) else (
        echo   [FAIL] Error creando backend\.env
        set /a ERRORS+=1
    )
)
echo.

:: ============================================
::  4. FRONTEND - Dependencias Node
:: ============================================
echo ============================================
echo   4/4 - FRONTEND: Dependencias Node
echo ============================================
echo.

pushd "%ROOT%\frontend"

if exist "node_modules" (
    echo   [OK] node_modules ya existe.
    echo.
    echo   Verificando actualizaciones...
    npm install 2>&1 | findstr /V "added removed changed" >nul
    if !ERRORLEVEL! equ 0 (
        echo   [OK] Dependencias frontend actualizadas.
    ) else (
        echo   [OK] Dependencias frontend ya instaladas.
    )
) else (
    echo   Instalando dependencias del frontend...
    echo   (Esto puede tomar varios minutos)
    echo.
    call npm install
    if !ERRORLEVEL! equ 0 (
        echo.
        echo   [OK] Dependencias frontend instaladas.
    ) else (
        echo.
        echo   [FAIL] Error instalando dependencias frontend.
        set /a ERRORS+=1
    )
)

popd
echo.

:: ============================================
::  Resumen Final
:: ============================================
echo ============================================
echo            INSTALACION COMPLETADA
echo ============================================
echo.
if %ERRORS% gtr 0 (
    echo   Se encontraron %ERRORS% errores. Revise los mensajes arriba.
    echo   Puede intentar ejecutar el instalador nuevamente.
) else (
    echo   Todas las dependencias instaladas correctamente.
    echo.
    echo   ANTES DE INICIAR:
    echo   1. Revise backend\.env y ajuste DATABASE_URL si es necesario
    echo   2. Verifique que PostgreSQL este corriendo:
    echo      scripts\iniciar.bat
    echo   3. Ejecute migraciones de base de datos:
    echo      cd backend ^& .venv\Scripts\python.exe -m alembic upgrade head
    echo   4. (Opcional) Cargar datos iniciales:
    echo      cd backend ^& .venv\Scripts\python.exe -m app.db.seed
)
echo.
pause
