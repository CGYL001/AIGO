# Set environment variables for AIgo development
$env:PYTHONPATH = (Get-Location).Path

Write-Host "Development environment set!"
Write-Host "Current directory: $((Get-Location).Path)"
Write-Host "PYTHONPATH: $env:PYTHONPATH"
Write-Host ""
Write-Host "Run 'python -m aigo.cli.__main__ --help' to see CLI help" 