@echo off
setlocal enabledelayedexpansion

:: --- Obtener directorio raiz del proyecto (padre de scripts\) ---
for %%I in ("%~dp0..") do set "ROOT=%%~fI"

echo ======================================================
echo Sincronizando Skills Publicas para FoodStore-SDD
echo ======================================================
echo.
echo Proyecto: %ROOT%

:: Directorio base de skills publicas (ruta absoluta desde ROOT)
set "PUBLIC_SKILLS_DIR=%ROOT%\.opencode\skills\public"

:: Crear el directorio si no existe
if not exist "%PUBLIC_SKILLS_DIR%" (
    mkdir "%PUBLIC_SKILLS_DIR%"
    if !ERRORLEVEL! neq 0 (
        echo ERROR: No se pudo crear %PUBLIC_SKILLS_DIR%
        pause
        exit /b 1
    )
)

:: Ir al root del proyecto para ejecutar npx
pushd "%ROOT%"

echo.
echo [1/7] Descargando skill: python-design-patterns...
call npx skills add https://github.com/wshobson/agents --skill python-design-patterns --out "%PUBLIC_SKILLS_DIR%\python-design-patterns"

echo [2/7] Descargando skill: find-skills...
call npx skills add https://github.com/vercel-labs/skills --skill find-skills --out "%PUBLIC_SKILLS_DIR%\find-skills"

echo [3/7] Descargando skill: python-testing-patterns...
call npx skills add https://github.com/wshobson/agents --skill python-testing-patterns --out "%PUBLIC_SKILLS_DIR%\python-testing-patterns"

echo [4/7] Descargando skill: jwt-security...
call npx skills add https://github.com/mindrally/skills --skill jwt-security --out "%PUBLIC_SKILLS_DIR%\jwt-security"

echo [5/7] Descargando skill: kb-creator...
call npx skills add https://github.com/JuanCruzRobledo/kb-creator --skill kb-creator --out "%PUBLIC_SKILLS_DIR%\kb-creator"

echo [6/7] Descargando skill: fastapi-python...
call npx skills add https://github.com/mindrally/skills --skill fastapi-python --out "%PUBLIC_SKILLS_DIR%\fastapi-python"

echo [7/7] Registrando skills...
REM Registrar las nuevas rutas en opencode.json si es necesario
echo.

popd

echo ======================================================
echo Sincronizacion completa.
echo Skills instaladas en: %PUBLIC_SKILLS_DIR%
echo ======================================================
pause
