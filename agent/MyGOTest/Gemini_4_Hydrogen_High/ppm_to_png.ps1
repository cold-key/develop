param(
    [Parameter(Mandatory=$true)][string]$InputPpm,
    [Parameter(Mandatory=$true)][string]$OutputPng
)
Add-Type -AssemblyName System.Drawing
$sr = New-Object System.IO.FileStream($InputPpm, [System.IO.FileMode]::Open, [System.IO.FileAccess]::Read)
$br = New-Object System.IO.BinaryReader($sr)
$hdr = ""
$nl = 0
while ($nl -lt 3) {
    $b = $br.ReadByte()
    if ($b -eq 10) { $nl++ }
    $hdr += [char]$b
}
$parts = $hdr.Trim().Split("`n")
$dims = $parts[1].Trim().Split(" ")
$w = [int]$dims[0]
$h = [int]$dims[1]
$raw = $br.ReadBytes($w * $h * 3)
$br.Close()
$sr.Close()

$bmp = New-Object System.Drawing.Bitmap($w, $h, [System.Drawing.Imaging.PixelFormat]::Format24bppRgb)
$rect = New-Object System.Drawing.Rectangle(0, 0, $w, $h)
$bd = $bmp.LockBits($rect, [System.Drawing.Imaging.ImageLockMode]::WriteOnly, [System.Drawing.Imaging.PixelFormat]::Format24bppRgb)
$row = New-Object byte[] $bd.Stride
for ($y = 0; $y -lt $h; $y++) {
    $base = $y * $w * 3
    for ($x = 0; $x -lt $w; $x++) {
        $i = $base + $x * 3
        $row[$x * 3]     = $raw[$i + 2]
        $row[$x * 3 + 1] = $raw[$i + 1]
        $row[$x * 3 + 2] = $raw[$i]
    }
    [System.Runtime.InteropServices.Marshal]::Copy($row, 0, [IntPtr]::Add($bd.Scan0, $y * $bd.Stride), $bd.Stride)
}
$bmp.UnlockBits($bd)
$bmp.Save($OutputPng, [System.Drawing.Imaging.ImageFormat]::Png)
$bmp.Dispose()
Write-Host "Converted $InputPpm -> $OutputPng ($w x $h)"
