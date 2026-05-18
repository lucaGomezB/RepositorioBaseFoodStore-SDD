@echo off
title FoodStore - Seed de Base de Datos
setlocal enabledelayedexpansion

:: ============================================
::  FOOD STORE - Cargar Datos Iniciales (Seed)
:: ============================================

:: --- Obtener directorio raiz del proyecto ---
for %%I in ("%~dp0..") do set "ROOT=%%~fI"

:: --- Verificar que backend\.env existe ---
if not exist "%ROOT%\backend\.env" (
    echo ============================================
    echo   ERROR: No se encuentra backend\.env
    echo ============================================
    echo.
    echo Ejecute primero scripts\instalar.bat o copie
    echo backend\.env.example a backend\.env
    echo.
    pause
    exit /b 1
)

:: --- Verificar que el .venv existe ---
if not exist "%ROOT%\backend\.venv\Scripts\python.exe" (
    echo ============================================
    echo   ERROR: Entorno virtual no encontrado
    echo ============================================
    echo.
    echo Ejecute primero scripts\instalar.bat
    echo.
    pause
    exit /b 1
)

cls
echo ============================================
echo    FOOD STORE - Carga de Datos Iniciales
echo ============================================
echo.

:: Ejecutar seed desde el directorio backend
pushd "%ROOT%\backend"

echo   Conectando a la base de datos...
echo   (debe estar corriendo PostgreSQL)
echo.
echo   %ROOT%\backend\.venv\Scripts\python.exe -m app.db.seed
echo.

"%ROOT%\backend\.venv\Scripts\python.exe" -m app.db.seed

if !ERRORLEVEL! equ 0 (
    echo.
    echo ============================================
    echo   DATOS INICIALES CARGADOS EXITOSAMENTE
    echo ============================================
    echo.
    echo   Usuario admin creado:
    echo     Email: admin@foodstore.com
    echo     Pass:  admin123
    echo.
) else (
    echo.
    echo ============================================
    echo   ERROR: No se pudieron cargar los datos.
    echo ============================================
    echo.
    echo   Posibles causas:
    echo   - PostgreSQL no esta corriendo (use scripts\iniciar.bat)
    echo   - La base de datos no existe
    echo   - Las migraciones no se ejecutaron
    echo.
    echo   Solucion:
    echo   1. scripts\iniciar.bat  (inicia PostgreSQL)
    echo   2. cd backend ^& .venv\Scripts\python.exe -m alembic upgrade head
    echo   3. scripts\seedear.bat  (vuelva a intentar)
    echo.
)

popd
pause
