# === Automatisch in STA neu starten falls nötig ===
if ([System.Threading.Thread]::CurrentThread.GetApartmentState() -ne 'STA') {
    Start-Process powershell.exe -ArgumentList "-STA -NoExit -File `"$PSCommandPath`"" -Wait
    exit
}

Add-Type -AssemblyName System.Windows.Forms

# === Ordner-Auswahl ===
$dialog = New-Object System.Windows.Forms.FolderBrowserDialog
$dialog.Description = "Ordner auswählen, dessen Unterordner analysiert werden sollen"
$dialog.ShowNewFolderButton = $false
$dialog.RootFolder = [System.Environment+SpecialFolder]::MyComputer

$rootPath = $null
if ($dialog.ShowDialog() -eq 'OK') {
    $rootPath = $dialog.SelectedPath
}

# === Papierkorb-Abfrage ===
$includeRecycle = $false
$answer = Read-Host "Papierkorb mit analysieren? (j/n)"
if ($answer -match '^[jJ]') { $includeRecycle = $true }

if (-not $rootPath -and -not $includeRecycle) {
    Write-Host "Nichts ausgewählt – Abbruch." -ForegroundColor Yellow
    Read-Host "Enter zum Beenden"
    exit
}

$results = [System.Collections.Generic.List[pscustomobject]]::new()

# === Unterordner analysieren ===
if ($rootPath) {
    Write-Host "Analysiere Unterordner von: $rootPath" -ForegroundColor Cyan
    Get-ChildItem -Path $rootPath -Directory -ErrorAction SilentlyContinue | ForEach-Object {
        $size = 0L
        try {
            $sum = Get-ChildItem $_.FullName -Recurse -File -ErrorAction SilentlyContinue |
                   Measure-Object -Property Length -Sum -ErrorAction SilentlyContinue
            if ($sum -and $null -ne $sum.Sum) { $size = [long]$sum.Sum }
        } catch { }

        $results.Add([pscustomobject]@{
            Ordner     = $_.FullName
            Groesse_MB = [math]::Round($size / 1MB, 2)
            Groesse_GB = [math]::Round($size / 1GB, 2)
            Bytes      = $size
            Typ        = "Ordner"
        })
    }
}

# === Papierkorb ===
if ($includeRecycle) {
    Write-Host "Analysiere Papierkorb..." -ForegroundColor Cyan
    $size = 0L
    try {
        $shell = New-Object -ComObject Shell.Application
        $bin = $shell.NameSpace(0xA)
        if ($bin) {
            $items = $bin.Items()
            if ($items.Count -gt 0) {
                $sum = $items | Measure-Object -Property Size -Sum -ErrorAction SilentlyContinue
                if ($sum -and $null -ne $sum.Sum) { $size = [long]$sum.Sum }
            }
        }
    } catch {
        Write-Host "Papierkorb-Fehler: $_" -ForegroundColor Red
    }

    $results.Add([pscustomobject]@{
        Ordner     = "Papierkorb"
        Groesse_MB = [math]::Round($size / 1MB, 2)
        Groesse_GB = [math]::Round($size / 1GB, 2)
        Bytes      = $size
        Typ        = "Papierkorb"
    })
}

# === Ausgabe ===
if ($results.Count -eq 0) {
    Write-Host "Keine Daten gefunden." -ForegroundColor Yellow
} else {
    $outFile = Join-Path $env:USERPROFILE "Desktop\Ordnergroessen.csv"
    $results | Sort-Object Bytes -Descending |
        Export-Csv -Path $outFile -NoTypeInformation -Encoding UTF8

    Write-Host "`nFertig! Datei gespeichert unter:" -ForegroundColor Green
    Write-Host $outFile -ForegroundColor Green
    Start-Process $outFile
}

Read-Host "`nEnter zum Beenden"