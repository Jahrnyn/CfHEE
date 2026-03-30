# Forras mappa
$path = 'D:\Saját\Copilot for hostile enterprise environment\CfHEE\docs'

# Kimeneti fajl nev timestamp-pel
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$outputFile = "D:\Saját\Copilot for hostile enterprise environment\CfHEE\docs\summary_$timestamp.txt"

# osszes fajl beolvasasa es egyesitese
Get-ChildItem -Path $path -Filter *.md | ForEach-Object {
    $fullPath = $_.FullName
    Get-Content -LiteralPath $fullPath | Add-Content -Path $outputFile
}