$env:PYTHONPATH = "$PSScriptRoot\app;$env:PYTHONPATH"
Set-Location "$PSScriptRoot\app"
Write-Host "Запуск Taskiq воркера из директории: $(Get-Location)" -ForegroundColor Green
Write-Host "PYTHONPATH: $env:PYTHONPATH" -ForegroundColor Yellow
taskiq worker task_queue:broker --fs-discover --tasks-pattern "**/tasks/*.py"

