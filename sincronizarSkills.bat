@echo off
setlocal enabledelayedexpansion

echo ======================================================
echo Sincronizando Skills Publicas para FoodStore-SDD
echo ======================================================

REM Directorio base de skills publicas
set PUBLIC_SKILLS_DIR=.opencode\skills\public

REM Crear el directorio si no existe
if not exist %PUBLIC_SKILLS_DIR% (
    mkdir %PUBLIC_SKILLS_DIR%
)

echo.
echo [1/1] Descargando skill: python-design-patterns...
REM Usamos npx skills add para descargar la skill completa en la ruta del repo
call npx skills add https://github.com/wshobson/agents --skill python-design-patterns --out %PUBLIC_SKILLS_DIR%\python-design-patterns
REM Skill para buscar skills
call npx skills add https://github.com/vercel-labs/skills --skill find-skills --out %PUBLIC_SKILLS_DIR%\find-skills
REM Skill para mejorar testeo con Python
call npx skills add https://github.com/wshobson/agents --skill python-testing-patterns --out %PUBLIC_SKILLS_DIR%\python-testing-patterns
REM Skill para mejorar JWT
call npx skills add https://github.com/mindrally/skills --skill jwt-security --out %PUBLIC_SKILLS_DIR%\jwt-security
REM Skill para generar bases de conocimiento
call npx skills add https://github.com/JuanCruzRobledo/kb-creator --skill kb-creator --out %PUBLIC_SKILLS_DIR%\kb-creator
REM Skill para mejorar FastAPI Python
call npx skills add https://github.com/mindrally/skills --skill fastapi-python --out %PUBLIC_SKILLS_DIR%\fastapi-python


echo ======================================================
echo Sincronizacion completa. 
echo Recuerda registrar las nuevas rutas en opencode.json
echo ======================================================
pause