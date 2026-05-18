@echo off
title FoodStore - Centro de Control
setlocal enabledelayedexpansion

:: ============================================
::  FOOD STORE - Iniciar / Detener Todo
::  Ejecutar como Administrador
:: ============================================

:: --- Obtener directorio raiz del proyecto (padre de scripts\) ---
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
echo    FOOD STORE - Centro de Control
echo ============================================
echo.
echo Proyecto: %ROOT%
echo.
echo Iniciando todos los servicios...
echo.

:: ============================================
::  1. PostgreSQL (servicio de Windows)
:: ============================================
echo [1/4] PostgreSQL...
net start postgresql-x64-18 >nul 2>&1
if %ERRORLEVEL% equ 2 (
    echo   * PostgreSQL ya estaba en ejecucion.
) else if %ERRORLEVEL% equ 0 (
    echo   * PostgreSQL iniciado correctamente.
) else (
    echo   * ERROR: No se pudo iniciar PostgreSQL.
    echo     Verifique que el servicio postgresql-x64-18 existe.
)
echo.

:: ============================================
::  2. Seed - Datos iniciales (idempotente)
:: ============================================
echo [2/4] Seed de datos iniciales...
if exist "%ROOT%\backend\.venv\Scripts\python.exe" (
    pushd "%ROOT%\backend"
    "%ROOT%\backend\.venv\Scripts\python.exe" -m app.db.seed >nul 2>&1
    if !ERRORLEVEL! equ 0 (
        echo   * Datos iniciales verificados/cargados.
    ) else (
        echo   * WARN: Seed no ejecutado (verificar DB y migraciones).
    )
    popd
) else (
    echo   * WARN: Seed omitido — .venv no encontrado.
    echo     Ejecute scripts\instalar.bat primero.
)
echo.

:: ============================================
::  3. Backend - FastAPI (puerto 8000)
:: ============================================
echo [3/4] Backend (FastAPI - puerto 8000)...
start "FoodStore-Backend" /D "%ROOT%\backend" cmd /c "title FoodStore-Backend && .venv\Scripts\python.exe -m uvicorn app.main:app --reload"
echo   * Backend iniciado en ventana aparte.
echo   * http://localhost:8000
echo   * http://localhost:8000/docs
echo.

:: ============================================
::  4. Frontend - React + Vite (puerto 5173)
:: ============================================
echo [4/4] Frontend (React + Vite - puerto 5173)...
start "FoodStore-Frontend" /D "%ROOT%\frontend" cmd /c "title FoodStore-Frontend && npm run dev"
echo   * Frontend iniciado en ventana aparte.
echo   * http://localhost:5173
echo.

:: Pequena pausa para que arranquen las ventanas
timeout /t 2 /nobreak >nul

:: ============================================
::  Menu principal - esperar comando "quit"
:: ============================================
echo ============================================
echo   TODOS LOS SERVICIOS EN EJECUCION
echo ============================================
echo.
echo   Backend:  http://localhost:8000
echo   Frontend: http://localhost:5173
echo   API Docs: http://localhost:8000/docs
echo.
echo   Escriba "quit" y presione Enter para
echo   detener todos los servicios.
echo ============================================
echo.

:loop
set /p "INPUT=^> "
if /i "!INPUT!"=="quit" goto shutdown
echo Escriba "quit" para detener todos los servicios.
goto loop

:: ============================================
::  Apagado de servicios
:: ============================================
:shutdown
echo.
echo ============================================
echo   DETENIENDO SERVICIOS...
echo ============================================
echo.

:: --- Detener Backend ---
echo [1/3] Deteniendo Backend...
echo   * Seed de datos: no requiere detencion (idempotente).
taskkill /F /FI "WindowTitle eq FoodStore-Backend" /T >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo   * Backend detenido.
) else (
    :: Fallback: matar por puerto 8000
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr /R ":8000 "') do (
        taskkill /F /PID %%a >nul 2>&1
    )
    echo   * Backend detenido (por puerto).
)
echo.

:: --- Detener Frontend ---
echo [2/3] Deteniendo Frontend...
taskkill /F /FI "WindowTitle eq FoodStore-Frontend" /T >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo   * Frontend detenido.
) else (
    :: Fallback: matar por puerto 5173
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr /R ":5173 "') do (
        taskkill /F /PID %%a >nul 2>&1
    )
    echo   * Frontend detenido (por puerto).
)
echo.

:: --- Detener PostgreSQL ---
echo [3/3] Deteniendo PostgreSQL...
net stop postgresql-x64-18 >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo   * PostgreSQL detenido.
) else if %ERRORLEVEL% equ 2 (
    echo   * PostgreSQL no estaba en ejecucion.
) else (
    echo   * ERROR al detener PostgreSQL.
)
echo.

echo ============================================
echo   TODOS LOS SERVICIOS DETENIDOS
echo ============================================
timeout /t 3 /nobreak >nul
exit /b 0
