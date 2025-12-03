@echo off
set PYTHONPATH=%~dp0app;%PYTHONPATH%
cd /d %~dp0app
echo Запуск Taskiq воркера из директории: %CD%
echo PYTHONPATH: %PYTHONPATH%
taskiq worker task_queue:broker --fs-discover --tasks-pattern "**/tasks/*.py"

