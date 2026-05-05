@echo off
title Compare BFSPMiner Baseline
echo =======================================================
echo Running Python vs Java Baseline Comparison
echo =======================================================

cd /d "%~dp0"

set PYTHON_EXE=python
if exist "C:\Users\ASUS\miniconda3\python.exe" (
    set PYTHON_EXE="C:\Users\ASUS\miniconda3\python.exe"
)

set DATASET=%1
if "%DATASET%"=="" set DATASET=redd

echo Running for dataset: %DATASET%
%PYTHON_EXE% evaluation\compare_baseline.py --dataset %DATASET%

echo.
pause
