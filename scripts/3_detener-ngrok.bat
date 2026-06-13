@echo off
title FoodStore - Detener servicios ngrok

:: ============================================
::  FOOD STORE - Detener servicios ngrok
:: ============================================

echo ============================================
echo   DETENIENDO SERVICIOS...
echo ============================================
echo.

echo [1/3] Deteniendo ngrok...
taskkill /F /FI "WindowTitle eq FoodStore-ngrok" /T >nul 2>&1
taskkill /F /IM ngrok.exe >nul 2>&1
echo   * ngrok detenido.
echo.

echo [2/3] Deteniendo Backend...
taskkill /F /FI "WindowTitle eq FoodStore-Backend" /T >nul 2>&1
for /f "tokens=5" %%a in ('netstat -ano ^| findstr /R ":8000 "') do (
    taskkill /F /PID %%a >nul 2>&1
)
echo   * Backend detenido.
echo.

echo [3/3] Deteniendo Frontend...
taskkill /F /FI "WindowTitle eq FoodStore-Frontend" /T >nul 2>&1
for /f "tokens=5" %%a in ('netstat -ano ^| findstr /R ":5173 "') do (
    taskkill /F /PID %%a >nul 2>&1
)
echo   * Frontend detenido.
echo.

echo ============================================
echo   TODOS LOS SERVICIOS DETENIDOS
echo ============================================
echo.
pause
