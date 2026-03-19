# Forrás mappa
$path = 'D:\Saját\Copilot for hostile enterprise environment\CfHEE\docs'

# Kimeneti fájl
$outputFile = 'D:\Saját\Copilot for hostile enterprise environment\CfHEE\docs\summary.txt'

# Ha már létezik a kimeneti fájl, töröljük
if (Test-Path $outputFile) {
    Remove-Item $outputFile
}

# Összes .al fájl beolvasása és egyesítése
Get-ChildItem -Path $path -Filter *.md | ForEach-Object {
    $fullPath = $_.FullName

    Get-Content -LiteralPath $fullPath | Add-Content -Path $outputFile
}
