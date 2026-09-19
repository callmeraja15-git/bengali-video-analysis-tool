$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$parent = Split-Path $root -Parent
$name = Split-Path $root -Leaf
$out = Join-Path $parent ($name + '.zip')
if (Test-Path $out) { Remove-Item $out -Force }
$items = Get-ChildItem $root -Force | Where-Object { $_.Name -notin @('.git','__pycache__','clips','results') -and $_.Name -notlike '*.pyc' -and $_.Name -notlike '*.zip' }
Compress-Archive -Path $items.FullName -DestinationPath $out -Force
Write-Host "Created: $out"
