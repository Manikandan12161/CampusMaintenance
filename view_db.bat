@echo off
if exist "D:\cygwin64\bin\python3.9.exe" (
    D:\cygwin64\bin\python3.9.exe view_db.py
) else (
    python view_db.py
)
