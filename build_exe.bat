@echo off

echo Building CrimeLens AI...

python -m PyInstaller --onefile --add-data "templates;templates" --add-data "static;static" --add-data "uploads;uploads" app.py

pause