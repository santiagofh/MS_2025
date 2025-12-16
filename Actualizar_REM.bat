@echo off
REM ============================================
REM Script de Descarga y Actualización REM
REM =============================================
echo Iniciando proceso de descarga y actualización de REM...
echo.

REM Cambiar al directorio de trabajo
echo [1/2] Cambiando al directorio de REM...
cd /d "C:\Users\fariass\OneDrive - SUBSECRETARIA DE SALUD PUBLICA\Escritorio\DATA\REM"
echo Directorio actual: %CD%
echo.

REM Ejecutar script de descarga
echo [2/2] Ejecutando script de descarga...
python "descarga_REMSAS_2025.py"
if %errorlevel% neq 0 (
    echo ERROR: El script de Python falló.
    echo Verifica que Python esté instalado y el script sea correcto.
    pause
    exit /b 1
)

echo.
echo ============================================
echo ¡Proceso completado exitosamente!
echo ============================================
pause