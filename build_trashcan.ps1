# Wrapper – bitte build.py verwenden (Versionierung inkl. alpha/beta/release)
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
python "$PSScriptRoot\build.py" @args