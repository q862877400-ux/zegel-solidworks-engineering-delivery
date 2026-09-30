# ★ 不使用 scriptblock（PowerShell 闭包捕获 $IX/$R 会失效——已踩 4 轮）
#   做法：先把 9 个列的索引一次性算成普通变量，再用 $R[$iD] 直接索引。
$v = "C:\Users\Zegel\solidpilot-mcp\adapters\claude\.venv\Lib\site-packages\bd_warehouse\data"
$out = "C:\Users\Zegel\solidpilot-mcp\知识库\bearing_specs.yaml"
$map = [ordered]@{
 'single_row_deep_groove_ball_bearing'       = '深沟球轴承(最通用)'
 'single_row_capped_deep_groove_ball_bearing' = '深沟球轴承_带防尘盖'
 'single_row_cylindrical_roller_bearing'     = '圆柱滚子轴承(高径向载荷)'
 'single_row_tapered_roller_bearing'         = '圆锥滚子轴承(轴向+径向)'
 'single_row_angular_contact_ball_bearing'   = '角接触球轴承(成对使用)'
}
$sb = [System.Text.StringBuilder]::new()
[void]$sb.AppendLine("# 滚动轴承规格库（数据源：本机 bd-warehouse / EPL-INA 原厂参数表）")
[void]$sb.AppendLine("# d内径 D外径 B宽度 C动载荷(kN) C0静载荷(kN) n_ref参考转速 n_lim极限转速 da轴肩")
[void]$sb.AppendLine("# 单位: 尺寸mm 载荷kN 转速r/min")
$total = 0; $bad = 0
foreach ($k in $map.Keys) {
    $p = Join-Path $v "$k`_parameters.csv"
    if (-not (Test-Path $p)) { continue }
    $L = @(Get-Content $p | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
    if ($L.Count -lt 2) { continue }
    $H = @(); foreach ($s in $L[0].Split(',')) { $H += $s.Trim() }
    $iDsn=-1; $id=-1; $iD=-1; $iB=-1; $iC=-1; $iC0=-1; $iNr=-1; $iNl=-1; $iDa=-1
    for ($i = 0; $i -lt $H.Count; $i++) {
        $n = $H[$i]; $nl = $n.ToLower()
        if ($n -ceq 'SKT:Designation') { $iDsn = $i }
        elseif ($n -ceq 'SKT:d') { $id = $i }
        elseif ($n -ceq 'SKT:D') { $iD = $i }
        elseif ($n -ceq 'SKT:B') { $iB = $i }
        elseif ($n -ceq 'SKT:C') { $iC = $i }
        elseif ($n -ceq 'SKT:C0') { $iC0 = $i }
        elseif ($nl -eq 'skt:speed-reference') { $iNr = $i }
        elseif ($nl -eq 'skt:speed-limit') { $iNl = $i }
        elseif ($n -ceq 'SKT:da') { $iDa = $i }
    }
    if ($id -lt 0 -or $iD -lt 0) { continue }
    [void]$sb.AppendLine("")
    [void]$sb.AppendLine("$($map[$k]):")
    [void]$sb.AppendLine("  型号                   d     D     B       C      C0   n_ref   n_lim     da")
    for ($n = 1; $n -lt $L.Count; $n++) {
        $R = $L[$n].Split(',')
        if ($R.Count -le [Math]::Max($id,$iD)) { $bad++; continue }
        $d = $R[$id].Trim(); $D = $R[$iD].Trim()
        if (-not ($d -match '^-?[\d.]+$' -and $D -match '^-?[\d.]+$')) { $bad++; continue }
        if ([double]$d -ge [double]$D) { $bad++; continue }
        $total++
        $g = { param($ix) if ($ix -ge 0 -and $ix -lt $R.Count) { $R[$ix].Trim() } else { '-' } }
        $line = "  {0,-20} {1,5} {2,5} {3,5} {4,7} {5,7} {6,7} {7,7} {8,6}" -f `
            (& $g $iDsn), $d, $D, (& $g $iB), (& $g $iC), (& $g $iC0), (& $g $iNr), (& $g $iNl), (& $g $iDa)
        [void]$sb.AppendLine($line)
    }
}
[IO.File]::WriteAllText($out, $sb.ToString(), (New-Object Text.UTF8Encoding($false)))
Write-Output "OK 有效 $total 条 / 剔除 $bad 条 / $([int]((Get-Item $out).Length/1KB))KB"