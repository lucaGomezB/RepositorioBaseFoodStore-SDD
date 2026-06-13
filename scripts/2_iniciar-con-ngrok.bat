@echo off
title FoodStore - Ngrok + Dev Environment

:: ============================================
::  FOOD STORE - Iniciar con ngrok
:: ============================================
::  Inicia ngrok, extrae la URL publica, configura
::  APP_URL en el .env del backend, y levanta
::  backend + frontend en ventanas separadas.
::
;;  PREREQUISITO: Ejecutar scripts\1_iniciar.bat primero
;;  (para PostgreSQL + seed de datos).
:: ============================================

:: --- Obtener directorio raiz del proyecto ---
for %%I in ("%~dp0..") do set "ROOT=%%~fI"

cls
echo ============================================
echo   FOOD STORE - Ngrok + Development
echo ============================================
echo.
echo Proyecto: %ROOT%
echo.
echo PREREQUISITO: PostgreSQL debe estar corriendo
echo y los datos seedeados (scripts\1_iniciar.bat).
echo.

:: ============================================
::  1. Limpiar procesos anteriores
:: ============================================
echo [1/6] Limpiando procesos anteriores...
taskkill /F /IM ngrok.exe >nul 2>&1
taskkill /F /IM python.exe >nul 2>&1
for /f "tokens=5" %%a in ('netstat -ano ^| findstr /R ":8000 "') do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -ano ^| findstr /R ":5173 "') do taskkill /F /PID %%a >nul 2>&1
echo   * OK - Procesos anteriores detenidos.
echo.

:: ============================================
::  2. Iniciar ngrok
:: ============================================
echo [2/6] Iniciando ngrok (tunel a puerto 8000)...
powershell -NoProfile -Command "Start-Process -WindowStyle Normal -FilePath 'ngrok.exe' -ArgumentList 'http','8000','--log=stdout'"
echo   * ngrok iniciado en ventana aparte.
echo.

:: ============================================
::  3. Esperar URL publica de ngrok
:: ============================================
echo [3/6] Esperando URL publica de ngrok...
set "NGROK_URL="

for /l %%i in (1,1,20) do (
    timeout /t 2 /nobreak >nul
    for /f "tokens=*" %%a in ('
        powershell -NoProfile -Command "& {
            try {
                $d = Invoke-RestMethod -Uri 'http://127.0.0.1:4040/api/tunnels' -ErrorAction Stop;
                if ($d.tunnels -and $d.tunnels.Count -gt 0) {
                    $u = $d.tunnels[0].public_url;
                    Write-Output $u
                } else { Write-Output '' }
            } catch { Write-Output '' }
        }"
    ') do (
        if not "%%a"=="" set "NGROK_URL=%%a"
    )
    if not "%NGROK_URL%"=="" goto ngrok_ready
)

echo   * ERROR: No se pudo obtener URL de ngrok tras 40 segundos.
echo     Verifique que ngrok este instalado y autenticado.
echo     (Ejecute: ngrok config add-authtoken <su-token>)
pause
exit /b 1

:ngrok_ready
echo   * URL obtenida: %NGROK_URL%
echo.

:: ============================================
::  4. Configurar APP_URL en backend\.env
:: ============================================
echo [4/6] Configurando APP_URL en backend\.env...
set "ENV_FILE=%ROOT%\backend\.env"

powershell -NoProfile -Command "& {
    $envFile = '%ENV_FILE%';
    $url = '%NGROK_URL%';
    $content = Get-Content $envFile;
    $found = $false;
    for ($i = 0; $i -lt $content.Count; $i++) {
        if ($content[$i] -match '^APP_URL=') {
            $content[$i] = 'APP_URL=' + $url;
            $found = $true;
            break
        }
    };
    if (-not $found) {
        $content += @('', '# ---------------------------------------------', '# APP URL - Public ngrok URL for MercadoPago webhooks', '# ---------------------------------------------', 'APP_URL=' + $url)
    };
    Set-Content $envFile $content
}"

echo   * APP_URL=%NGROK_URL%
echo.

:: ============================================
::  5. Iniciar Backend (FastAPI)
:: ============================================
echo [5/6] Iniciando Backend (FastAPI - puerto 8000)...
powershell -NoProfile -Command "Start-Process -WindowStyle Normal -FilePath '%ROOT%\backend\.venv\Scripts\python.exe' -ArgumentList '-m','uvicorn','app.main:app','--reload' -WorkingDirectory '%ROOT%\backend'"
echo   * Backend iniciado en ventana aparte.
echo   * http://localhost:8000
echo   * http://localhost:8000/docs
echo.

:: ============================================
::  6. Iniciar Frontend (React + Vite)
:: ============================================
echo [6/6] Iniciando Frontend (React + Vite - puerto 5173)...
powershell -NoProfile -Command "Start-Process -WindowStyle Normal -FilePath 'cmd.exe' -ArgumentList '/c','npm','run','dev' -WorkingDirectory '%ROOT%\frontend'"
echo   * Frontend iniciado en ventana aparte.
echo   * http://localhost:5173
echo.

:: Pequena pausa para que arranquen las ventanas
timeout /t 3 /nobreak >nul

:: ============================================
::  Resumen final
:: ============================================
cls
echo ============================================
echo   FOOD STORE - LISTO
echo ============================================
echo.
echo   ngrok URL:     %NGROK_URL%
echo   Backend:       http://localhost:8000
echo   API Docs:      http://localhost:8000/docs
echo   Frontend:      http://localhost:5173
echo.
echo   =========================================
echo   Configura este webhook en MercadoPago:
echo   %NGROK_URL%/api/v1/pagos/webhook
echo   =========================================
echo.
echo   Las ventanas (ngrok + backend + frontend)
echo   estan abiertas para supervision.
echo.
echo   Presione una tecla para cerrar.
echo.
pause
