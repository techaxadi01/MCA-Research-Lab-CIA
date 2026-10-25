param(
    [string]$docxPath,
    [string]$pdfPath
)
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$absDocx = (Resolve-Path $docxPath).Path
$absPdf = [System.IO.Path]::GetFullPath($pdfPath)
$doc = $word.Documents.Open($absDocx)
$doc.SaveAs2($absPdf, 17)
$doc.Close()
$word.Quit()
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($word) | Out-Null
Write-Host "Successfully exported $absPdf"
