@echo off
REM ============================================
REM Script de actualización automatizado REM
REM ============================================
echo Iniciando proceso de actualización...
echo.

REM Cambiar al directorio de trabajo
echo [1/6] Cambiando directorio...
cd /d "C:\Users\fariass\OneDrive - SUBSECRETARIA DE SALUD PUBLICA\Escritorio\Salud Pública\MS_2025"

echo Directorio actual: %CD%
echo.

REM Ejecutar scripts Python
echo [2/6] Ejecutando Calculo MS-2025_version2.py...
python "Calculo MS-2025_version2.py"
if %errorlevel% neq 0 (
    echo Error al ejecutar el primer script Python.
    pause
    exit /b 1
)
echo.

echo [3/6] Ejecutando Calculo_fecha_corte_REM.py...
python "Calculo_fecha_corte_REM.py"
if %errorlevel% neq 0 (
    echo Error al ejecutar el segundo script Python.
    pause
    exit /b 1
)
echo.

REM Proceso GIT (orden correcto: add -> commit -> push)
echo [4/6] Añadiendo cambios al stage...
git add .
if %errorlevel% neq 0 (
    echo Error al ejecutar git add.
    pause
    exit /b 1
)

echo [5/6] Realizando commit...
git commit -m "Actualización de datos"
if %errorlevel% neq 0 (
    echo Error al ejecutar git commit.
    pause
    exit /b 1
)

echo [6/6] Enviando cambios al repositorio remoto...
git push
if %errorlevel% neq 0 (
    echo Error al ejecutar git push.
    pause
    exit /b 1
)

echo.
echo ============================================
echo ¡Proceso completado exitosamente!
echo ============================================
pause