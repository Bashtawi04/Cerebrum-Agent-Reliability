# Create a virtual environment inside a target agent folder and install what its requirements.txt asks for.
#   .\tools\setup_target.ps1 targets\<folder>
# Not tested by the mentors (we ran the shell version on Linux). Tell us if it fails.
# If PowerShell refuses to run it: powershell -ExecutionPolicy Bypass -File tools\setup_target.ps1 targets\<folder>
param([Parameter(Mandatory = $true)][string]$Target)
$ErrorActionPreference = "Stop"
Push-Location $Target
try {
    python -m venv .venv
    & .\.venv\Scripts\python.exe -m pip install --quiet --upgrade pip
    & .\.venv\Scripts\python.exe -m pip install --quiet -r requirements.txt
    $here = ((Get-Location).Path) -replace "\\", "/"
    Write-Host "ready. Use this interpreter in --agent: $here/.venv/Scripts/python.exe"
    Write-Host "and this folder in --agent-dir: $here"
}
finally {
    Pop-Location
}
