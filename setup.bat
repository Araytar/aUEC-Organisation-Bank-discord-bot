@echo off
setlocal
echo Installing Python packages...

python --version 2>NUL
if errorlevel 1 goto errorNoPython

pip install py-cord
pip install discord
pip install configparser

echo Python modules installed successfully.
echo Setting up run.bat file...

if exist run.bat (
    echo Run file already created.
    pause
) else (

    (
        echo @echo off
        echo python ./src/main.py
    ) > run.bat
    echo Successfully Created run.bat
    pause
)

goto:eof

:errorNoPython
echo.
echo Error^: Python not installed

