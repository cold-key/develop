Add-Type -AssemblyName System.Drawing

$dir = "d:\CodeSpace\Code\develop\agent\MyGOTest\Gemini_4_Hydrogen_High"
$origPath    = "d:\CodeSpace\Code\develop\agent\MyGOTest\千早爱音.jpg"
$purePath    = "$dir\千早爱音_纯函数轮廓.png"
$overlayPath = "$dir\千早爱音_函数叠加图.png"
$globalPath  = "$dir\千早爱音_全局分离函数_fg.png"
$outPath     = "$dir\千早爱音_函数描图_对比.png"

$imgOrig    = [System.Drawing.Image]::FromFile($origPath)
$imgPure    = [System.Drawing.Image]::FromFile($purePath)
$imgOverlay = [System.Drawing.Image]::FromFile($overlayPath)
$imgGlobal  = [System.Drawing.Image]::FromFile($globalPath)

$W = 2400
$H = 1920
$bmp = New-Object System.Drawing.Bitmap($W, $H)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::HighQuality
$g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
$g.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::AntiAliasGridFit
$g.Clear([System.Drawing.Color]::FromArgb(248, 250, 252))

$titleFont = New-Object System.Drawing.Font("Microsoft YaHei UI", 24, [System.Drawing.FontStyle]::Bold)
$subFont   = New-Object System.Drawing.Font("Microsoft YaHei UI", 14, [System.Drawing.FontStyle]::Regular)
$panelFont = New-Object System.Drawing.Font("Microsoft YaHei UI", 15, [System.Drawing.FontStyle]::Bold)
$axisFont  = New-Object System.Drawing.Font("Consolas", 11, [System.Drawing.FontStyle]::Regular)

$darkBrush  = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(24, 32, 48))
$mutedBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(85, 98, 118))
$borderPen  = New-Object System.Drawing.Pen([System.Drawing.Color]::FromArgb(203, 213, 225), 2)
$gridPen    = New-Object System.Drawing.Pen([System.Drawing.Color]::FromArgb(65, 148, 163, 184), 1)
$axisPen    = New-Object System.Drawing.Pen([System.Drawing.Color]::FromArgb(140, 71, 85, 105), 1.5)

$g.DrawString("千早爱音.jpg — 拉格朗日插值与分离隐函数 f(x) = g(y) 函数描图报告", $titleFont, $darkBrush, 60, 28)
$g.DrawString("坐标系: [-4, 4] × [-3, 3] (1:1 等比例)  |  分段方程: 5,308 段 (Chebyshev-Lobatto 节点拉格朗日插值 + 分离椭圆)  |  骨架->曲线平均误差: 0.345 px (99.97% <= 2 px)", $subFont, $mutedBrush, 60, 78)

$pw = 1092
$ph = 819
$panels = @(
    @{ Img = $imgOrig;    X = 60;   Y = 160; Title = "1. 原图 (1092 × 819)" },
    @{ Img = $imgPure;    X = 1248; Y = 160; Title = "2. 纯数学函数图像 f_k(x) = g_k(y) (无原图背景)" },
    @{ Img = $imgOverlay; X = 60;   Y = 1055; Title = "3. 拟合函数叠加原图 (红: y=L(x), 蓝: x=L(y), 绿: 分离椭圆)" },
    @{ Img = $imgGlobal;  X = 1248; Y = 1055; Title = "4. 严格单对全局函数 f_global(x) = g_global(y) 零点集 (4,673/4,673 零伪影)" }
)

foreach ($p in $panels) {
    $g.DrawString($p.Title, $panelFont, $darkBrush, $p.X, $p.Y - 34)
    $g.DrawImage($p.Img, $p.X, $p.Y, $pw, $ph)
    $g.DrawRectangle($borderPen, $p.X, $p.Y, $pw, $ph)

    # Draw subtle coordinate grid and ticks on panels 2, 3, 4
    if ($p -ne $panels[0]) {
        for ($ux = -3; $ux -le 3; $ux++) {
            $gx = $p.X + ($ux + 4.0) / 8.0 * $pw
            $pen = if ($ux -eq 0) { $axisPen } else { $gridPen }
            $g.DrawLine($pen, [float]$gx, [float]$p.Y, [float]$gx, [float]($p.Y + $ph))
            $g.DrawString("$ux", $axisFont, $mutedBrush, [float]($gx - 8), [float]($p.Y + $ph + 4))
        }
        for ($uy = -2; $uy -le 2; $uy++) {
            $gy = $p.Y + (3.0 - $uy) / 6.0 * $ph
            $pen = if ($uy -eq 0) { $axisPen } else { $gridPen }
            $g.DrawLine($pen, [float]$p.X, [float]$gy, [float]($p.X + $pw), [float]$gy)
            $g.DrawString("$uy", $axisFont, $mutedBrush, [float]($p.X - 28), [float]($gy - 8))
        }
    }
}

$bmp.Save($outPath, [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $bmp.Dispose()
$imgOrig.Dispose(); $imgPure.Dispose(); $imgOverlay.Dispose(); $imgGlobal.Dispose()
Write-Host "Saved comparison board -> $outPath"
