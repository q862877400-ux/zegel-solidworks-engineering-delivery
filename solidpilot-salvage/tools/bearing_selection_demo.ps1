# ★ 闭环验证：用轴承库 + 配合库 + 材料库 做一次真实选型
# 题目：设计一根传动轴，传递 P=2.2kW, n=1450 rpm，要求寿命 L10h=10000h
# 判据自检：算出的 C/C比 是否符合工程常识；选的型号是否真的在表里、n_lim 是否够

$csv = "C:\Users\Zegel\solidpilot-mcp\知识库\bearings\single_row_deep_groove_ball_bearing_parameters.csv"
$L = @(Get-Content $csv | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })

# 列位置（已验证）：1=d 2=D 3=B 4=C 5=C0 6=Pu 7=n_ref 8=n_lim 9=mass 10=Designation 15=da 17=ra
function Parse($line) {
    $r = $line.Split(',')
    [pscustomobject]@{
        bore = [double]$r[1]; shell = [double]$r[2]; wid = [double]$r[3]
        C  = [double]$r[4];  C0 = [double]$r[5];  Pu = [double]$r[6]
        nRef = [double]$r[7]; nLim = [double]$r[8]; mass = [double]$r[9]
        Desig = $r[10].Trim(); da = $r[15].Trim(); ra = $r[17].Trim()
    }
}

Write-Output "════ 工况 ════"
$P = 2.2; $n = 1450; $Lh = 10000
Write-Output "  功率 P = $P kW，转速 n = $n rpm，要求寿命 L10h = $Lh h"
# 1) 载荷系数（design_rules: 中等工况 K_A=1.3~1.5，轻载1.3）
$K_A = 1.3
Write-Output "  工况系数 K_A = $K_A（中等冲击）"

# 2) 当量动载荷 P = K_A × (轴承当量载荷)
#    ★ 简化：设径向为主，取载荷系数 X=1, Y=1.4（球轴承，Fr/Fr > e）
#    为演示取径向载荷 Fr = 0.5 × 轴向载荷极限，按轴径初估
$Fr = 1200   # N，按轴径 φ30 估算的径向载荷
$Fa = 300    # N，轴向力
$X = 1.0; $Y = 1.4
$P_eq = [math]::Round($K_A * ($X*$Fr + $Y*$Fa), 1)
Write-Output "  径向载荷 Fr = $Fr N，轴向 Fa = $Fa N"
Write-Output "  当量动载荷 P = K_A·(X·Fr + Y·Fa) = $K_A·($X·$Fr + $Y·$Fa) = $P_eq N"

# 3) 由寿命反算所需动载荷（球轴承 ε=3）
$millions = $Lh * 60 * $n / 1e6
$eps = 3
$C_need = [math]::Round($P_eq * [math]::Pow($millions, 1/$eps), 1)
Write-Output "  寿命转数 = $Lh h × 60 × $n rpm = $([math]::Round($millions*1e6/1e6,1))×10^6 转"
Write-Output "  球轴承 ε=3 ⇒ C_需 = P × (寿命/10^6)^(1/3) = $P_eq × $([math]::Round($millions,2))^(1/3) = $C_need N = $([math]::Round($C_need/1000,2)) kN"

# 4) 查表选型
Write-Output ""
Write-Output "════ 查表选型（C ≥ $C_need N 且 n_lim ≥ $n）════"
$pick = @()
for ($i = 1; $i -lt $L.Count; $i++) {
    try { $b = Parse $L[$i] } catch { continue }
    if ($b.C -ge $C_need -and $b.nLim -ge $n) { $pick += $b }
}
$pick = $pick | Sort-Object d
if ($pick.Count -eq 0) {
    Write-Output "  ⚠ 表中无满足的型号（表内主要是小规格 M3~M5，功率偏大）"
    # 退而求其次：列出承载最接近的
    $all = @(); for ($i=1;$i -lt $L.Count;$i++){ try { $all += Parse $L[$i] } catch {} }
    $all | Sort-Object { [math]::Abs($_.C - $C_need) } | Select-Object -First 3 |
      ForEach-Object { Write-Output "     最近: $($_.Desig)  d=$(# ★ 闭环验证：用轴承库 + 配合库 + 材料库 做一次真实选型
# 题目：设计一根传动轴，传递 P=2.2kW, n=1450 rpm，要求寿命 L10h=10000h
# 判据自检：算出的 C/C比 是否符合工程常识；选的型号是否真的在表里、n_lim 是否够

$csv = "C:\Users\Zegel\solidpilot-mcp\知识库\bearings\single_row_deep_groove_ball_bearing_parameters.csv"
$L = @(Get-Content $csv | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })

# 列位置（已验证）：1=d 2=D 3=B 4=C 5=C0 6=Pu 7=n_ref 8=n_lim 9=mass 10=Designation 15=da 17=ra
function Parse($line) {
    $r = $line.Split(',')
    [pscustomobject]@{
        bore = [double]$r[1]; shell = [double]$r[2]; wid = [double]$r[3]
        C  = [double]$r[4];  C0 = [double]$r[5];  Pu = [double]$r[6]
        nRef = [double]$r[7]; nLim = [double]$r[8]; mass = [double]$r[9]
        Desig = $r[10].Trim(); da = $r[15].Trim(); ra = $r[17].Trim()
    }
}

Write-Output "════ 工况 ════"
$P = 2.2; $n = 1450; $Lh = 10000
Write-Output "  功率 P = $P kW，转速 n = $n rpm，要求寿命 L10h = $Lh h"
# 1) 载荷系数（design_rules: 中等工况 K_A=1.3~1.5，轻载1.3）
$K_A = 1.3
Write-Output "  工况系数 K_A = $K_A（中等冲击）"

# 2) 当量动载荷 P = K_A × (轴承当量载荷)
#    ★ 简化：设径向为主，取载荷系数 X=1, Y=1.4（球轴承，Fr/Fr > e）
#    为演示取径向载荷 Fr = 0.5 × 轴向载荷极限，按轴径初估
$Fr = 1200   # N，按轴径 φ30 估算的径向载荷
$Fa = 300    # N，轴向力
$X = 1.0; $Y = 1.4
$P_eq = [math]::Round($K_A * ($X*$Fr + $Y*$Fa), 1)
Write-Output "  径向载荷 Fr = $Fr N，轴向 Fa = $Fa N"
Write-Output "  当量动载荷 P = K_A·(X·Fr + Y·Fa) = $K_A·($X·$Fr + $Y·$Fa) = $P_eq N"

# 3) 由寿命反算所需动载荷（球轴承 ε=3）
$millions = $Lh * 60 * $n / 1e6
$eps = 3
$C_need = [math]::Round($P_eq * [math]::Pow($millions, 1/$eps), 1)
Write-Output "  寿命转数 = $Lh h × 60 × $n rpm = $([math]::Round($millions*1e6/1e6,1))×10^6 转"
Write-Output "  球轴承 ε=3 ⇒ C_需 = P × (寿命/10^6)^(1/3) = $P_eq × $([math]::Round($millions,2))^(1/3) = $C_need N = $([math]::Round($C_need/1000,2)) kN"

# 4) 查表选型
Write-Output ""
Write-Output "════ 查表选型（C ≥ $C_need N 且 n_lim ≥ $n）════"
$pick = @()
for ($i = 1; $i -lt $L.Count; $i++) {
    try { $b = Parse $L[$i] } catch { continue }
    if ($b.C -ge $C_need -and $b.nLim -ge $n) { $pick += $b }
}
$pick = $pick | Sort-Object d
if ($pick.Count -eq 0) {
    Write-Output "  ⚠ 表中无满足的型号（表内主要是小规格 M3~M5，功率偏大）"
    # 退而求其次：列出承载最接近的
    $all = @(); for ($i=1;$i -lt $L.Count;$i++){ try { $all += Parse $L[$i] } catch {} }
    $all | Sort-Object { [math]::Abs($_.C - $C_need) } | Select-Object -First 3 |
      ForEach-Object { Write-Output "     最近: $($_.Desig)  d=$(# ★ 闭环验证：用轴承库 + 配合库 + 材料库 做一次真实选型
# 题目：设计一根传动轴，传递 P=2.2kW, n=1450 rpm，要求寿命 L10h=10000h
# 判据自检：算出的 C/C比 是否符合工程常识；选的型号是否真的在表里、n_lim 是否够

$csv = "C:\Users\Zegel\solidpilot-mcp\知识库\bearings\single_row_deep_groove_ball_bearing_parameters.csv"
$L = @(Get-Content $csv | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })

# 列位置（已验证）：1=d 2=D 3=B 4=C 5=C0 6=Pu 7=n_ref 8=n_lim 9=mass 10=Designation 15=da 17=ra
function Parse($line) {
    $r = $line.Split(',')
    [pscustomobject]@{
        bore = [double]$r[1]; shell = [double]$r[2]; wid = [double]$r[3]
        C  = [double]$r[4];  C0 = [double]$r[5];  Pu = [double]$r[6]
        nRef = [double]$r[7]; nLim = [double]$r[8]; mass = [double]$r[9]
        Desig = $r[10].Trim(); da = $r[15].Trim(); ra = $r[17].Trim()
    }
}

Write-Output "════ 工况 ════"
$P = 2.2; $n = 1450; $Lh = 10000
Write-Output "  功率 P = $P kW，转速 n = $n rpm，要求寿命 L10h = $Lh h"
# 1) 载荷系数（design_rules: 中等工况 K_A=1.3~1.5，轻载1.3）
$K_A = 1.3
Write-Output "  工况系数 K_A = $K_A（中等冲击）"

# 2) 当量动载荷 P = K_A × (轴承当量载荷)
#    ★ 简化：设径向为主，取载荷系数 X=1, Y=1.4（球轴承，Fr/Fr > e）
#    为演示取径向载荷 Fr = 0.5 × 轴向载荷极限，按轴径初估
$Fr = 1200   # N，按轴径 φ30 估算的径向载荷
$Fa = 300    # N，轴向力
$X = 1.0; $Y = 1.4
$P_eq = [math]::Round($K_A * ($X*$Fr + $Y*$Fa), 1)
Write-Output "  径向载荷 Fr = $Fr N，轴向 Fa = $Fa N"
Write-Output "  当量动载荷 P = K_A·(X·Fr + Y·Fa) = $K_A·($X·$Fr + $Y·$Fa) = $P_eq N"

# 3) 由寿命反算所需动载荷（球轴承 ε=3）
$millions = $Lh * 60 * $n / 1e6
$eps = 3
$C_need = [math]::Round($P_eq * [math]::Pow($millions, 1/$eps), 1)
Write-Output "  寿命转数 = $Lh h × 60 × $n rpm = $([math]::Round($millions*1e6/1e6,1))×10^6 转"
Write-Output "  球轴承 ε=3 ⇒ C_需 = P × (寿命/10^6)^(1/3) = $P_eq × $([math]::Round($millions,2))^(1/3) = $C_need N = $([math]::Round($C_need/1000,2)) kN"

# 4) 查表选型
Write-Output ""
Write-Output "════ 查表选型（C ≥ $C_need N 且 n_lim ≥ $n）════"
$pick = @()
for ($i = 1; $i -lt $L.Count; $i++) {
    try { $b = Parse $L[$i] } catch { continue }
    if ($b.C -ge $C_need -and $b.nLim -ge $n) { $pick += $b }
}
$pick = $pick | Sort-Object d
if ($pick.Count -eq 0) {
    Write-Output "  ⚠ 表中无满足的型号（表内主要是小规格 M3~M5，功率偏大）"
    # 退而求其次：列出承载最接近的
    $all = @(); for ($i=1;$i -lt $L.Count;$i++){ try { $all += Parse $L[$i] } catch {} }
    $all | Sort-Object { [math]::Abs($_.C - $C_need) } | Select-Object -First 3 |
      ForEach-Object { Write-Output "     最近: $($_.Desig)  d=$(# ★ 闭环验证：用轴承库 + 配合库 + 材料库 做一次真实选型
# 题目：设计一根传动轴，传递 P=2.2kW, n=1450 rpm，要求寿命 L10h=10000h
# 判据自检：算出的 C/C比 是否符合工程常识；选的型号是否真的在表里、n_lim 是否够

$csv = "C:\Users\Zegel\solidpilot-mcp\知识库\bearings\single_row_deep_groove_ball_bearing_parameters.csv"
$L = @(Get-Content $csv | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })

# 列位置（已验证）：1=d 2=D 3=B 4=C 5=C0 6=Pu 7=n_ref 8=n_lim 9=mass 10=Designation 15=da 17=ra
function Parse($line) {
    $r = $line.Split(',')
    [pscustomobject]@{
        bore = [double]$r[1]; shell = [double]$r[2]; wid = [double]$r[3]
        C  = [double]$r[4];  C0 = [double]$r[5];  Pu = [double]$r[6]
        nRef = [double]$r[7]; nLim = [double]$r[8]; mass = [double]$r[9]
        Desig = $r[10].Trim(); da = $r[15].Trim(); ra = $r[17].Trim()
    }
}

Write-Output "════ 工况 ════"
$P = 2.2; $n = 1450; $Lh = 10000
Write-Output "  功率 P = $P kW，转速 n = $n rpm，要求寿命 L10h = $Lh h"
# 1) 载荷系数（design_rules: 中等工况 K_A=1.3~1.5，轻载1.3）
$K_A = 1.3
Write-Output "  工况系数 K_A = $K_A（中等冲击）"

# 2) 当量动载荷 P = K_A × (轴承当量载荷)
#    ★ 简化：设径向为主，取载荷系数 X=1, Y=1.4（球轴承，Fr/Fr > e）
#    为演示取径向载荷 Fr = 0.5 × 轴向载荷极限，按轴径初估
$Fr = 1200   # N，按轴径 φ30 估算的径向载荷
$Fa = 300    # N，轴向力
$X = 1.0; $Y = 1.4
$P_eq = [math]::Round($K_A * ($X*$Fr + $Y*$Fa), 1)
Write-Output "  径向载荷 Fr = $Fr N，轴向 Fa = $Fa N"
Write-Output "  当量动载荷 P = K_A·(X·Fr + Y·Fa) = $K_A·($X·$Fr + $Y·$Fa) = $P_eq N"

# 3) 由寿命反算所需动载荷（球轴承 ε=3）
$millions = $Lh * 60 * $n / 1e6
$eps = 3
$C_need = [math]::Round($P_eq * [math]::Pow($millions, 1/$eps), 1)
Write-Output "  寿命转数 = $Lh h × 60 × $n rpm = $([math]::Round($millions*1e6/1e6,1))×10^6 转"
Write-Output "  球轴承 ε=3 ⇒ C_需 = P × (寿命/10^6)^(1/3) = $P_eq × $([math]::Round($millions,2))^(1/3) = $C_need N = $([math]::Round($C_need/1000,2)) kN"

# 4) 查表选型
Write-Output ""
Write-Output "════ 查表选型（C ≥ $C_need N 且 n_lim ≥ $n）════"
$pick = @()
for ($i = 1; $i -lt $L.Count; $i++) {
    try { $b = Parse $L[$i] } catch { continue }
    if ($b.C -ge $C_need -and $b.nLim -ge $n) { $pick += $b }
}
$pick = $pick | Sort-Object d
if ($pick.Count -eq 0) {
    Write-Output "  ⚠ 表中无满足的型号（表内主要是小规格 M3~M5，功率偏大）"
    # 退而求其次：列出承载最接近的
    $all = @(); for ($i=1;$i -lt $L.Count;$i++){ try { $all += Parse $L[$i] } catch {} }
    $all | Sort-Object { [math]::Abs($_.C - $C_need) } | Select-Object -First 3 |
      ForEach-Object { Write-Output "     最近: $($_.Desig)  d=$($_.d) C=$($_.C)kN  差 $([math]::Round($_.C*1000-$C_need,0))N" }
} else {
    Write-Output "  满足条件的型号 $($pick.Count) 个（按内径排序，前 6 个）:"
    $pick | Select-Object -First 6 | ForEach-Object {
        Write-Output ("     {0,-10} d={1,4} D={2,4} B={3,4}  C={4,6}N  n_lim={5,7}  轴肩da={6,5}  ra={7}" -f `
            $_.Desig, $_.d, $_.D, $_.B, ($_.C*1000), $_.nLim, $_.da, $_.ra)
    }
    $best = $pick | Select-Object -First 1
    Write-Output ""
    Write-Output "════ 校核 ════"
    Write-Output "  选用 $($best.Desig)：C=$($best.C)kN / 需 $C_need N ⇒ 实际富余 $([math]::Round($best.C*1000-$C_need,0))N"
    $lifeChk = [math]::Round(($best.C*1000/$P_eq) * 3 * 1e6 / (60*$n) / 1e6, 2)
    Write-Output "  反算寿命 L10h = (C/P)³·10⁶/(60n) = $lifeChk 万小时（要求 $Lh h）"
    Write-Output "  转速校核：n_lim=$($best.nLim) ≥ $n ⇒ $(if($best.nLim -ge $n){'✅'}else{'❌'})"
}

# 5) 配合：按知识库 fits_iso286，φ30 的 H7/k6
Write-Output ""
Write-Output "════ 配合校核（fits_iso286.yaml，24~30 段）════"
$holeES = 21.0; $holeEI = 0.0     # H7
$axEs = 15.0;  $axEi = 2.0       # k6
$Xmax = $holeES - $axEi
$Xmin = $holeEI - $axEs
Write-Output "  H7 孔 (24~30): ES=+$holeES EI=$holeEI"
Write-Output "  k6 轴 (24~30): es=+$axEs ei=+$axEi"
Write-Output "  ⇒ Xmax = ES孔 − ei轴 = $Xmax μm（最大间隙）"
Write-Output "  ⇒ Xmin = EI孔 − es轴 = $Xmin μm（最大过盈）"
Write-Output "  ⇒ 过渡配合，过盈约 $([math]::Abs($Xmin)) μm = $([math]::Abs($Xmin)/1000) mm"
Write-Output "  ⇒ $(if($Xmin -lt 0){'✅ 轻中载旋转内圈：有过盈但小，便于装拆'}else{'⚠ 无过盈，是间隙配合'})"
.bore) C=$($_.C)kN  差 $([math]::Round($_.C*1000-$C_need,0))N" }
} else {
    Write-Output "  满足条件的型号 $($pick.Count) 个（按内径排序，前 6 个）:"
    $pick | Select-Object -First 6 | ForEach-Object {
        Write-Output ("     {0,-10} d={1,4} D={2,4} B={3,4}  C={4,6}N  n_lim={5,7}  轴肩da={6,5}  ra={7}" -f `
            $_.Desig, # ★ 闭环验证：用轴承库 + 配合库 + 材料库 做一次真实选型
# 题目：设计一根传动轴，传递 P=2.2kW, n=1450 rpm，要求寿命 L10h=10000h
# 判据自检：算出的 C/C比 是否符合工程常识；选的型号是否真的在表里、n_lim 是否够

$csv = "C:\Users\Zegel\solidpilot-mcp\知识库\bearings\single_row_deep_groove_ball_bearing_parameters.csv"
$L = @(Get-Content $csv | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })

# 列位置（已验证）：1=d 2=D 3=B 4=C 5=C0 6=Pu 7=n_ref 8=n_lim 9=mass 10=Designation 15=da 17=ra
function Parse($line) {
    $r = $line.Split(',')
    [pscustomobject]@{
        bore = [double]$r[1]; shell = [double]$r[2]; wid = [double]$r[3]
        C  = [double]$r[4];  C0 = [double]$r[5];  Pu = [double]$r[6]
        nRef = [double]$r[7]; nLim = [double]$r[8]; mass = [double]$r[9]
        Desig = $r[10].Trim(); da = $r[15].Trim(); ra = $r[17].Trim()
    }
}

Write-Output "════ 工况 ════"
$P = 2.2; $n = 1450; $Lh = 10000
Write-Output "  功率 P = $P kW，转速 n = $n rpm，要求寿命 L10h = $Lh h"
# 1) 载荷系数（design_rules: 中等工况 K_A=1.3~1.5，轻载1.3）
$K_A = 1.3
Write-Output "  工况系数 K_A = $K_A（中等冲击）"

# 2) 当量动载荷 P = K_A × (轴承当量载荷)
#    ★ 简化：设径向为主，取载荷系数 X=1, Y=1.4（球轴承，Fr/Fr > e）
#    为演示取径向载荷 Fr = 0.5 × 轴向载荷极限，按轴径初估
$Fr = 1200   # N，按轴径 φ30 估算的径向载荷
$Fa = 300    # N，轴向力
$X = 1.0; $Y = 1.4
$P_eq = [math]::Round($K_A * ($X*$Fr + $Y*$Fa), 1)
Write-Output "  径向载荷 Fr = $Fr N，轴向 Fa = $Fa N"
Write-Output "  当量动载荷 P = K_A·(X·Fr + Y·Fa) = $K_A·($X·$Fr + $Y·$Fa) = $P_eq N"

# 3) 由寿命反算所需动载荷（球轴承 ε=3）
$millions = $Lh * 60 * $n / 1e6
$eps = 3
$C_need = [math]::Round($P_eq * [math]::Pow($millions, 1/$eps), 1)
Write-Output "  寿命转数 = $Lh h × 60 × $n rpm = $([math]::Round($millions*1e6/1e6,1))×10^6 转"
Write-Output "  球轴承 ε=3 ⇒ C_需 = P × (寿命/10^6)^(1/3) = $P_eq × $([math]::Round($millions,2))^(1/3) = $C_need N = $([math]::Round($C_need/1000,2)) kN"

# 4) 查表选型
Write-Output ""
Write-Output "════ 查表选型（C ≥ $C_need N 且 n_lim ≥ $n）════"
$pick = @()
for ($i = 1; $i -lt $L.Count; $i++) {
    try { $b = Parse $L[$i] } catch { continue }
    if ($b.C -ge $C_need -and $b.nLim -ge $n) { $pick += $b }
}
$pick = $pick | Sort-Object d
if ($pick.Count -eq 0) {
    Write-Output "  ⚠ 表中无满足的型号（表内主要是小规格 M3~M5，功率偏大）"
    # 退而求其次：列出承载最接近的
    $all = @(); for ($i=1;$i -lt $L.Count;$i++){ try { $all += Parse $L[$i] } catch {} }
    $all | Sort-Object { [math]::Abs($_.C - $C_need) } | Select-Object -First 3 |
      ForEach-Object { Write-Output "     最近: $($_.Desig)  d=$($_.d) C=$($_.C)kN  差 $([math]::Round($_.C*1000-$C_need,0))N" }
} else {
    Write-Output "  满足条件的型号 $($pick.Count) 个（按内径排序，前 6 个）:"
    $pick | Select-Object -First 6 | ForEach-Object {
        Write-Output ("     {0,-10} d={1,4} D={2,4} B={3,4}  C={4,6}N  n_lim={5,7}  轴肩da={6,5}  ra={7}" -f `
            $_.Desig, $_.d, $_.D, $_.B, ($_.C*1000), $_.nLim, $_.da, $_.ra)
    }
    $best = $pick | Select-Object -First 1
    Write-Output ""
    Write-Output "════ 校核 ════"
    Write-Output "  选用 $($best.Desig)：C=$($best.C)kN / 需 $C_need N ⇒ 实际富余 $([math]::Round($best.C*1000-$C_need,0))N"
    $lifeChk = [math]::Round(($best.C*1000/$P_eq) * 3 * 1e6 / (60*$n) / 1e6, 2)
    Write-Output "  反算寿命 L10h = (C/P)³·10⁶/(60n) = $lifeChk 万小时（要求 $Lh h）"
    Write-Output "  转速校核：n_lim=$($best.nLim) ≥ $n ⇒ $(if($best.nLim -ge $n){'✅'}else{'❌'})"
}

# 5) 配合：按知识库 fits_iso286，φ30 的 H7/k6
Write-Output ""
Write-Output "════ 配合校核（fits_iso286.yaml，24~30 段）════"
$holeES = 21.0; $holeEI = 0.0     # H7
$axEs = 15.0;  $axEi = 2.0       # k6
$Xmax = $holeES - $axEi
$Xmin = $holeEI - $axEs
Write-Output "  H7 孔 (24~30): ES=+$holeES EI=$holeEI"
Write-Output "  k6 轴 (24~30): es=+$axEs ei=+$axEi"
Write-Output "  ⇒ Xmax = ES孔 − ei轴 = $Xmax μm（最大间隙）"
Write-Output "  ⇒ Xmin = EI孔 − es轴 = $Xmin μm（最大过盈）"
Write-Output "  ⇒ 过渡配合，过盈约 $([math]::Abs($Xmin)) μm = $([math]::Abs($Xmin)/1000) mm"
Write-Output "  ⇒ $(if($Xmin -lt 0){'✅ 轻中载旋转内圈：有过盈但小，便于装拆'}else{'⚠ 无过盈，是间隙配合'})"
.bore, # ★ 闭环验证：用轴承库 + 配合库 + 材料库 做一次真实选型
# 题目：设计一根传动轴，传递 P=2.2kW, n=1450 rpm，要求寿命 L10h=10000h
# 判据自检：算出的 C/C比 是否符合工程常识；选的型号是否真的在表里、n_lim 是否够

$csv = "C:\Users\Zegel\solidpilot-mcp\知识库\bearings\single_row_deep_groove_ball_bearing_parameters.csv"
$L = @(Get-Content $csv | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })

# 列位置（已验证）：1=d 2=D 3=B 4=C 5=C0 6=Pu 7=n_ref 8=n_lim 9=mass 10=Designation 15=da 17=ra
function Parse($line) {
    $r = $line.Split(',')
    [pscustomobject]@{
        bore = [double]$r[1]; shell = [double]$r[2]; wid = [double]$r[3]
        C  = [double]$r[4];  C0 = [double]$r[5];  Pu = [double]$r[6]
        nRef = [double]$r[7]; nLim = [double]$r[8]; mass = [double]$r[9]
        Desig = $r[10].Trim(); da = $r[15].Trim(); ra = $r[17].Trim()
    }
}

Write-Output "════ 工况 ════"
$P = 2.2; $n = 1450; $Lh = 10000
Write-Output "  功率 P = $P kW，转速 n = $n rpm，要求寿命 L10h = $Lh h"
# 1) 载荷系数（design_rules: 中等工况 K_A=1.3~1.5，轻载1.3）
$K_A = 1.3
Write-Output "  工况系数 K_A = $K_A（中等冲击）"

# 2) 当量动载荷 P = K_A × (轴承当量载荷)
#    ★ 简化：设径向为主，取载荷系数 X=1, Y=1.4（球轴承，Fr/Fr > e）
#    为演示取径向载荷 Fr = 0.5 × 轴向载荷极限，按轴径初估
$Fr = 1200   # N，按轴径 φ30 估算的径向载荷
$Fa = 300    # N，轴向力
$X = 1.0; $Y = 1.4
$P_eq = [math]::Round($K_A * ($X*$Fr + $Y*$Fa), 1)
Write-Output "  径向载荷 Fr = $Fr N，轴向 Fa = $Fa N"
Write-Output "  当量动载荷 P = K_A·(X·Fr + Y·Fa) = $K_A·($X·$Fr + $Y·$Fa) = $P_eq N"

# 3) 由寿命反算所需动载荷（球轴承 ε=3）
$millions = $Lh * 60 * $n / 1e6
$eps = 3
$C_need = [math]::Round($P_eq * [math]::Pow($millions, 1/$eps), 1)
Write-Output "  寿命转数 = $Lh h × 60 × $n rpm = $([math]::Round($millions*1e6/1e6,1))×10^6 转"
Write-Output "  球轴承 ε=3 ⇒ C_需 = P × (寿命/10^6)^(1/3) = $P_eq × $([math]::Round($millions,2))^(1/3) = $C_need N = $([math]::Round($C_need/1000,2)) kN"

# 4) 查表选型
Write-Output ""
Write-Output "════ 查表选型（C ≥ $C_need N 且 n_lim ≥ $n）════"
$pick = @()
for ($i = 1; $i -lt $L.Count; $i++) {
    try { $b = Parse $L[$i] } catch { continue }
    if ($b.C -ge $C_need -and $b.nLim -ge $n) { $pick += $b }
}
$pick = $pick | Sort-Object d
if ($pick.Count -eq 0) {
    Write-Output "  ⚠ 表中无满足的型号（表内主要是小规格 M3~M5，功率偏大）"
    # 退而求其次：列出承载最接近的
    $all = @(); for ($i=1;$i -lt $L.Count;$i++){ try { $all += Parse $L[$i] } catch {} }
    $all | Sort-Object { [math]::Abs($_.C - $C_need) } | Select-Object -First 3 |
      ForEach-Object { Write-Output "     最近: $($_.Desig)  d=$($_.d) C=$($_.C)kN  差 $([math]::Round($_.C*1000-$C_need,0))N" }
} else {
    Write-Output "  满足条件的型号 $($pick.Count) 个（按内径排序，前 6 个）:"
    $pick | Select-Object -First 6 | ForEach-Object {
        Write-Output ("     {0,-10} d={1,4} D={2,4} B={3,4}  C={4,6}N  n_lim={5,7}  轴肩da={6,5}  ra={7}" -f `
            $_.Desig, $_.d, $_.D, $_.B, ($_.C*1000), $_.nLim, $_.da, $_.ra)
    }
    $best = $pick | Select-Object -First 1
    Write-Output ""
    Write-Output "════ 校核 ════"
    Write-Output "  选用 $($best.Desig)：C=$($best.C)kN / 需 $C_need N ⇒ 实际富余 $([math]::Round($best.C*1000-$C_need,0))N"
    $lifeChk = [math]::Round(($best.C*1000/$P_eq) * 3 * 1e6 / (60*$n) / 1e6, 2)
    Write-Output "  反算寿命 L10h = (C/P)³·10⁶/(60n) = $lifeChk 万小时（要求 $Lh h）"
    Write-Output "  转速校核：n_lim=$($best.nLim) ≥ $n ⇒ $(if($best.nLim -ge $n){'✅'}else{'❌'})"
}

# 5) 配合：按知识库 fits_iso286，φ30 的 H7/k6
Write-Output ""
Write-Output "════ 配合校核（fits_iso286.yaml，24~30 段）════"
$holeES = 21.0; $holeEI = 0.0     # H7
$axEs = 15.0;  $axEi = 2.0       # k6
$Xmax = $holeES - $axEi
$Xmin = $holeEI - $axEs
Write-Output "  H7 孔 (24~30): ES=+$holeES EI=$holeEI"
Write-Output "  k6 轴 (24~30): es=+$axEs ei=+$axEi"
Write-Output "  ⇒ Xmax = ES孔 − ei轴 = $Xmax μm（最大间隙）"
Write-Output "  ⇒ Xmin = EI孔 − es轴 = $Xmin μm（最大过盈）"
Write-Output "  ⇒ 过渡配合，过盈约 $([math]::Abs($Xmin)) μm = $([math]::Abs($Xmin)/1000) mm"
Write-Output "  ⇒ $(if($Xmin -lt 0){'✅ 轻中载旋转内圈：有过盈但小，便于装拆'}else{'⚠ 无过盈，是间隙配合'})"
.bore, $_.B, ($_.C*1000), $_.nLim, $_.da, $_.ra)
    }
    $best = $pick | Select-Object -First 1
    Write-Output ""
    Write-Output "════ 校核 ════"
    Write-Output "  选用 $($best.Desig)：C=$($best.C)kN / 需 $C_need N ⇒ 实际富余 $([math]::Round($best.C*1000-$C_need,0))N"
    $lifeChk = [math]::Round(($best.C*1000/$P_eq) * 3 * 1e6 / (60*$n) / 1e6, 2)
    Write-Output "  反算寿命 L10h = (C/P)³·10⁶/(60n) = $lifeChk 万小时（要求 $Lh h）"
    Write-Output "  转速校核：n_lim=$($best.nLim) ≥ $n ⇒ $(if($best.nLim -ge $n){'✅'}else{'❌'})"
}

# 5) 配合：按知识库 fits_iso286，φ30 的 H7/k6
Write-Output ""
Write-Output "════ 配合校核（fits_iso286.yaml，24~30 段）════"
$holeES = 21.0; $holeEI = 0.0     # H7
$axEs = 15.0;  $axEi = 2.0       # k6
$Xmax = $holeES - $axEi
$Xmin = $holeEI - $axEs
Write-Output "  H7 孔 (24~30): ES=+$holeES EI=$holeEI"
Write-Output "  k6 轴 (24~30): es=+$axEs ei=+$axEi"
Write-Output "  ⇒ Xmax = ES孔 − ei轴 = $Xmax μm（最大间隙）"
Write-Output "  ⇒ Xmin = EI孔 − es轴 = $Xmin μm（最大过盈）"
Write-Output "  ⇒ 过渡配合，过盈约 $([math]::Abs($Xmin)) μm = $([math]::Abs($Xmin)/1000) mm"
Write-Output "  ⇒ $(if($Xmin -lt 0){'✅ 轻中载旋转内圈：有过盈但小，便于装拆'}else{'⚠ 无过盈，是间隙配合'})"
.shell) C=$($_.C)kN  差 $([math]::Round($_.C*1000-$C_need,0))N" }
} else {
    Write-Output "  满足条件的型号 $($pick.Count) 个（按内径排序，前 6 个）:"
    $pick | Select-Object -First 6 | ForEach-Object {
        Write-Output ("     {0,-10} d={1,4} D={2,4} B={3,4}  C={4,6}N  n_lim={5,7}  轴肩da={6,5}  ra={7}" -f `
            $_.Desig, # ★ 闭环验证：用轴承库 + 配合库 + 材料库 做一次真实选型
# 题目：设计一根传动轴，传递 P=2.2kW, n=1450 rpm，要求寿命 L10h=10000h
# 判据自检：算出的 C/C比 是否符合工程常识；选的型号是否真的在表里、n_lim 是否够

$csv = "C:\Users\Zegel\solidpilot-mcp\知识库\bearings\single_row_deep_groove_ball_bearing_parameters.csv"
$L = @(Get-Content $csv | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })

# 列位置（已验证）：1=d 2=D 3=B 4=C 5=C0 6=Pu 7=n_ref 8=n_lim 9=mass 10=Designation 15=da 17=ra
function Parse($line) {
    $r = $line.Split(',')
    [pscustomobject]@{
        bore = [double]$r[1]; shell = [double]$r[2]; wid = [double]$r[3]
        C  = [double]$r[4];  C0 = [double]$r[5];  Pu = [double]$r[6]
        nRef = [double]$r[7]; nLim = [double]$r[8]; mass = [double]$r[9]
        Desig = $r[10].Trim(); da = $r[15].Trim(); ra = $r[17].Trim()
    }
}

Write-Output "════ 工况 ════"
$P = 2.2; $n = 1450; $Lh = 10000
Write-Output "  功率 P = $P kW，转速 n = $n rpm，要求寿命 L10h = $Lh h"
# 1) 载荷系数（design_rules: 中等工况 K_A=1.3~1.5，轻载1.3）
$K_A = 1.3
Write-Output "  工况系数 K_A = $K_A（中等冲击）"

# 2) 当量动载荷 P = K_A × (轴承当量载荷)
#    ★ 简化：设径向为主，取载荷系数 X=1, Y=1.4（球轴承，Fr/Fr > e）
#    为演示取径向载荷 Fr = 0.5 × 轴向载荷极限，按轴径初估
$Fr = 1200   # N，按轴径 φ30 估算的径向载荷
$Fa = 300    # N，轴向力
$X = 1.0; $Y = 1.4
$P_eq = [math]::Round($K_A * ($X*$Fr + $Y*$Fa), 1)
Write-Output "  径向载荷 Fr = $Fr N，轴向 Fa = $Fa N"
Write-Output "  当量动载荷 P = K_A·(X·Fr + Y·Fa) = $K_A·($X·$Fr + $Y·$Fa) = $P_eq N"

# 3) 由寿命反算所需动载荷（球轴承 ε=3）
$millions = $Lh * 60 * $n / 1e6
$eps = 3
$C_need = [math]::Round($P_eq * [math]::Pow($millions, 1/$eps), 1)
Write-Output "  寿命转数 = $Lh h × 60 × $n rpm = $([math]::Round($millions*1e6/1e6,1))×10^6 转"
Write-Output "  球轴承 ε=3 ⇒ C_需 = P × (寿命/10^6)^(1/3) = $P_eq × $([math]::Round($millions,2))^(1/3) = $C_need N = $([math]::Round($C_need/1000,2)) kN"

# 4) 查表选型
Write-Output ""
Write-Output "════ 查表选型（C ≥ $C_need N 且 n_lim ≥ $n）════"
$pick = @()
for ($i = 1; $i -lt $L.Count; $i++) {
    try { $b = Parse $L[$i] } catch { continue }
    if ($b.C -ge $C_need -and $b.nLim -ge $n) { $pick += $b }
}
$pick = $pick | Sort-Object d
if ($pick.Count -eq 0) {
    Write-Output "  ⚠ 表中无满足的型号（表内主要是小规格 M3~M5，功率偏大）"
    # 退而求其次：列出承载最接近的
    $all = @(); for ($i=1;$i -lt $L.Count;$i++){ try { $all += Parse $L[$i] } catch {} }
    $all | Sort-Object { [math]::Abs($_.C - $C_need) } | Select-Object -First 3 |
      ForEach-Object { Write-Output "     最近: $($_.Desig)  d=$(# ★ 闭环验证：用轴承库 + 配合库 + 材料库 做一次真实选型
# 题目：设计一根传动轴，传递 P=2.2kW, n=1450 rpm，要求寿命 L10h=10000h
# 判据自检：算出的 C/C比 是否符合工程常识；选的型号是否真的在表里、n_lim 是否够

$csv = "C:\Users\Zegel\solidpilot-mcp\知识库\bearings\single_row_deep_groove_ball_bearing_parameters.csv"
$L = @(Get-Content $csv | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })

# 列位置（已验证）：1=d 2=D 3=B 4=C 5=C0 6=Pu 7=n_ref 8=n_lim 9=mass 10=Designation 15=da 17=ra
function Parse($line) {
    $r = $line.Split(',')
    [pscustomobject]@{
        bore = [double]$r[1]; shell = [double]$r[2]; wid = [double]$r[3]
        C  = [double]$r[4];  C0 = [double]$r[5];  Pu = [double]$r[6]
        nRef = [double]$r[7]; nLim = [double]$r[8]; mass = [double]$r[9]
        Desig = $r[10].Trim(); da = $r[15].Trim(); ra = $r[17].Trim()
    }
}

Write-Output "════ 工况 ════"
$P = 2.2; $n = 1450; $Lh = 10000
Write-Output "  功率 P = $P kW，转速 n = $n rpm，要求寿命 L10h = $Lh h"
# 1) 载荷系数（design_rules: 中等工况 K_A=1.3~1.5，轻载1.3）
$K_A = 1.3
Write-Output "  工况系数 K_A = $K_A（中等冲击）"

# 2) 当量动载荷 P = K_A × (轴承当量载荷)
#    ★ 简化：设径向为主，取载荷系数 X=1, Y=1.4（球轴承，Fr/Fr > e）
#    为演示取径向载荷 Fr = 0.5 × 轴向载荷极限，按轴径初估
$Fr = 1200   # N，按轴径 φ30 估算的径向载荷
$Fa = 300    # N，轴向力
$X = 1.0; $Y = 1.4
$P_eq = [math]::Round($K_A * ($X*$Fr + $Y*$Fa), 1)
Write-Output "  径向载荷 Fr = $Fr N，轴向 Fa = $Fa N"
Write-Output "  当量动载荷 P = K_A·(X·Fr + Y·Fa) = $K_A·($X·$Fr + $Y·$Fa) = $P_eq N"

# 3) 由寿命反算所需动载荷（球轴承 ε=3）
$millions = $Lh * 60 * $n / 1e6
$eps = 3
$C_need = [math]::Round($P_eq * [math]::Pow($millions, 1/$eps), 1)
Write-Output "  寿命转数 = $Lh h × 60 × $n rpm = $([math]::Round($millions*1e6/1e6,1))×10^6 转"
Write-Output "  球轴承 ε=3 ⇒ C_需 = P × (寿命/10^6)^(1/3) = $P_eq × $([math]::Round($millions,2))^(1/3) = $C_need N = $([math]::Round($C_need/1000,2)) kN"

# 4) 查表选型
Write-Output ""
Write-Output "════ 查表选型（C ≥ $C_need N 且 n_lim ≥ $n）════"
$pick = @()
for ($i = 1; $i -lt $L.Count; $i++) {
    try { $b = Parse $L[$i] } catch { continue }
    if ($b.C -ge $C_need -and $b.nLim -ge $n) { $pick += $b }
}
$pick = $pick | Sort-Object d
if ($pick.Count -eq 0) {
    Write-Output "  ⚠ 表中无满足的型号（表内主要是小规格 M3~M5，功率偏大）"
    # 退而求其次：列出承载最接近的
    $all = @(); for ($i=1;$i -lt $L.Count;$i++){ try { $all += Parse $L[$i] } catch {} }
    $all | Sort-Object { [math]::Abs($_.C - $C_need) } | Select-Object -First 3 |
      ForEach-Object { Write-Output "     最近: $($_.Desig)  d=$($_.d) C=$($_.C)kN  差 $([math]::Round($_.C*1000-$C_need,0))N" }
} else {
    Write-Output "  满足条件的型号 $($pick.Count) 个（按内径排序，前 6 个）:"
    $pick | Select-Object -First 6 | ForEach-Object {
        Write-Output ("     {0,-10} d={1,4} D={2,4} B={3,4}  C={4,6}N  n_lim={5,7}  轴肩da={6,5}  ra={7}" -f `
            $_.Desig, $_.d, $_.D, $_.B, ($_.C*1000), $_.nLim, $_.da, $_.ra)
    }
    $best = $pick | Select-Object -First 1
    Write-Output ""
    Write-Output "════ 校核 ════"
    Write-Output "  选用 $($best.Desig)：C=$($best.C)kN / 需 $C_need N ⇒ 实际富余 $([math]::Round($best.C*1000-$C_need,0))N"
    $lifeChk = [math]::Round(($best.C*1000/$P_eq) * 3 * 1e6 / (60*$n) / 1e6, 2)
    Write-Output "  反算寿命 L10h = (C/P)³·10⁶/(60n) = $lifeChk 万小时（要求 $Lh h）"
    Write-Output "  转速校核：n_lim=$($best.nLim) ≥ $n ⇒ $(if($best.nLim -ge $n){'✅'}else{'❌'})"
}

# 5) 配合：按知识库 fits_iso286，φ30 的 H7/k6
Write-Output ""
Write-Output "════ 配合校核（fits_iso286.yaml，24~30 段）════"
$holeES = 21.0; $holeEI = 0.0     # H7
$axEs = 15.0;  $axEi = 2.0       # k6
$Xmax = $holeES - $axEi
$Xmin = $holeEI - $axEs
Write-Output "  H7 孔 (24~30): ES=+$holeES EI=$holeEI"
Write-Output "  k6 轴 (24~30): es=+$axEs ei=+$axEi"
Write-Output "  ⇒ Xmax = ES孔 − ei轴 = $Xmax μm（最大间隙）"
Write-Output "  ⇒ Xmin = EI孔 − es轴 = $Xmin μm（最大过盈）"
Write-Output "  ⇒ 过渡配合，过盈约 $([math]::Abs($Xmin)) μm = $([math]::Abs($Xmin)/1000) mm"
Write-Output "  ⇒ $(if($Xmin -lt 0){'✅ 轻中载旋转内圈：有过盈但小，便于装拆'}else{'⚠ 无过盈，是间隙配合'})"
.bore) C=$($_.C)kN  差 $([math]::Round($_.C*1000-$C_need,0))N" }
} else {
    Write-Output "  满足条件的型号 $($pick.Count) 个（按内径排序，前 6 个）:"
    $pick | Select-Object -First 6 | ForEach-Object {
        Write-Output ("     {0,-10} d={1,4} D={2,4} B={3,4}  C={4,6}N  n_lim={5,7}  轴肩da={6,5}  ra={7}" -f `
            $_.Desig, # ★ 闭环验证：用轴承库 + 配合库 + 材料库 做一次真实选型
# 题目：设计一根传动轴，传递 P=2.2kW, n=1450 rpm，要求寿命 L10h=10000h
# 判据自检：算出的 C/C比 是否符合工程常识；选的型号是否真的在表里、n_lim 是否够

$csv = "C:\Users\Zegel\solidpilot-mcp\知识库\bearings\single_row_deep_groove_ball_bearing_parameters.csv"
$L = @(Get-Content $csv | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })

# 列位置（已验证）：1=d 2=D 3=B 4=C 5=C0 6=Pu 7=n_ref 8=n_lim 9=mass 10=Designation 15=da 17=ra
function Parse($line) {
    $r = $line.Split(',')
    [pscustomobject]@{
        bore = [double]$r[1]; shell = [double]$r[2]; wid = [double]$r[3]
        C  = [double]$r[4];  C0 = [double]$r[5];  Pu = [double]$r[6]
        nRef = [double]$r[7]; nLim = [double]$r[8]; mass = [double]$r[9]
        Desig = $r[10].Trim(); da = $r[15].Trim(); ra = $r[17].Trim()
    }
}

Write-Output "════ 工况 ════"
$P = 2.2; $n = 1450; $Lh = 10000
Write-Output "  功率 P = $P kW，转速 n = $n rpm，要求寿命 L10h = $Lh h"
# 1) 载荷系数（design_rules: 中等工况 K_A=1.3~1.5，轻载1.3）
$K_A = 1.3
Write-Output "  工况系数 K_A = $K_A（中等冲击）"

# 2) 当量动载荷 P = K_A × (轴承当量载荷)
#    ★ 简化：设径向为主，取载荷系数 X=1, Y=1.4（球轴承，Fr/Fr > e）
#    为演示取径向载荷 Fr = 0.5 × 轴向载荷极限，按轴径初估
$Fr = 1200   # N，按轴径 φ30 估算的径向载荷
$Fa = 300    # N，轴向力
$X = 1.0; $Y = 1.4
$P_eq = [math]::Round($K_A * ($X*$Fr + $Y*$Fa), 1)
Write-Output "  径向载荷 Fr = $Fr N，轴向 Fa = $Fa N"
Write-Output "  当量动载荷 P = K_A·(X·Fr + Y·Fa) = $K_A·($X·$Fr + $Y·$Fa) = $P_eq N"

# 3) 由寿命反算所需动载荷（球轴承 ε=3）
$millions = $Lh * 60 * $n / 1e6
$eps = 3
$C_need = [math]::Round($P_eq * [math]::Pow($millions, 1/$eps), 1)
Write-Output "  寿命转数 = $Lh h × 60 × $n rpm = $([math]::Round($millions*1e6/1e6,1))×10^6 转"
Write-Output "  球轴承 ε=3 ⇒ C_需 = P × (寿命/10^6)^(1/3) = $P_eq × $([math]::Round($millions,2))^(1/3) = $C_need N = $([math]::Round($C_need/1000,2)) kN"

# 4) 查表选型
Write-Output ""
Write-Output "════ 查表选型（C ≥ $C_need N 且 n_lim ≥ $n）════"
$pick = @()
for ($i = 1; $i -lt $L.Count; $i++) {
    try { $b = Parse $L[$i] } catch { continue }
    if ($b.C -ge $C_need -and $b.nLim -ge $n) { $pick += $b }
}
$pick = $pick | Sort-Object d
if ($pick.Count -eq 0) {
    Write-Output "  ⚠ 表中无满足的型号（表内主要是小规格 M3~M5，功率偏大）"
    # 退而求其次：列出承载最接近的
    $all = @(); for ($i=1;$i -lt $L.Count;$i++){ try { $all += Parse $L[$i] } catch {} }
    $all | Sort-Object { [math]::Abs($_.C - $C_need) } | Select-Object -First 3 |
      ForEach-Object { Write-Output "     最近: $($_.Desig)  d=$($_.d) C=$($_.C)kN  差 $([math]::Round($_.C*1000-$C_need,0))N" }
} else {
    Write-Output "  满足条件的型号 $($pick.Count) 个（按内径排序，前 6 个）:"
    $pick | Select-Object -First 6 | ForEach-Object {
        Write-Output ("     {0,-10} d={1,4} D={2,4} B={3,4}  C={4,6}N  n_lim={5,7}  轴肩da={6,5}  ra={7}" -f `
            $_.Desig, $_.d, $_.D, $_.B, ($_.C*1000), $_.nLim, $_.da, $_.ra)
    }
    $best = $pick | Select-Object -First 1
    Write-Output ""
    Write-Output "════ 校核 ════"
    Write-Output "  选用 $($best.Desig)：C=$($best.C)kN / 需 $C_need N ⇒ 实际富余 $([math]::Round($best.C*1000-$C_need,0))N"
    $lifeChk = [math]::Round(($best.C*1000/$P_eq) * 3 * 1e6 / (60*$n) / 1e6, 2)
    Write-Output "  反算寿命 L10h = (C/P)³·10⁶/(60n) = $lifeChk 万小时（要求 $Lh h）"
    Write-Output "  转速校核：n_lim=$($best.nLim) ≥ $n ⇒ $(if($best.nLim -ge $n){'✅'}else{'❌'})"
}

# 5) 配合：按知识库 fits_iso286，φ30 的 H7/k6
Write-Output ""
Write-Output "════ 配合校核（fits_iso286.yaml，24~30 段）════"
$holeES = 21.0; $holeEI = 0.0     # H7
$axEs = 15.0;  $axEi = 2.0       # k6
$Xmax = $holeES - $axEi
$Xmin = $holeEI - $axEs
Write-Output "  H7 孔 (24~30): ES=+$holeES EI=$holeEI"
Write-Output "  k6 轴 (24~30): es=+$axEs ei=+$axEi"
Write-Output "  ⇒ Xmax = ES孔 − ei轴 = $Xmax μm（最大间隙）"
Write-Output "  ⇒ Xmin = EI孔 − es轴 = $Xmin μm（最大过盈）"
Write-Output "  ⇒ 过渡配合，过盈约 $([math]::Abs($Xmin)) μm = $([math]::Abs($Xmin)/1000) mm"
Write-Output "  ⇒ $(if($Xmin -lt 0){'✅ 轻中载旋转内圈：有过盈但小，便于装拆'}else{'⚠ 无过盈，是间隙配合'})"
.bore, # ★ 闭环验证：用轴承库 + 配合库 + 材料库 做一次真实选型
# 题目：设计一根传动轴，传递 P=2.2kW, n=1450 rpm，要求寿命 L10h=10000h
# 判据自检：算出的 C/C比 是否符合工程常识；选的型号是否真的在表里、n_lim 是否够

$csv = "C:\Users\Zegel\solidpilot-mcp\知识库\bearings\single_row_deep_groove_ball_bearing_parameters.csv"
$L = @(Get-Content $csv | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })

# 列位置（已验证）：1=d 2=D 3=B 4=C 5=C0 6=Pu 7=n_ref 8=n_lim 9=mass 10=Designation 15=da 17=ra
function Parse($line) {
    $r = $line.Split(',')
    [pscustomobject]@{
        bore = [double]$r[1]; shell = [double]$r[2]; wid = [double]$r[3]
        C  = [double]$r[4];  C0 = [double]$r[5];  Pu = [double]$r[6]
        nRef = [double]$r[7]; nLim = [double]$r[8]; mass = [double]$r[9]
        Desig = $r[10].Trim(); da = $r[15].Trim(); ra = $r[17].Trim()
    }
}

Write-Output "════ 工况 ════"
$P = 2.2; $n = 1450; $Lh = 10000
Write-Output "  功率 P = $P kW，转速 n = $n rpm，要求寿命 L10h = $Lh h"
# 1) 载荷系数（design_rules: 中等工况 K_A=1.3~1.5，轻载1.3）
$K_A = 1.3
Write-Output "  工况系数 K_A = $K_A（中等冲击）"

# 2) 当量动载荷 P = K_A × (轴承当量载荷)
#    ★ 简化：设径向为主，取载荷系数 X=1, Y=1.4（球轴承，Fr/Fr > e）
#    为演示取径向载荷 Fr = 0.5 × 轴向载荷极限，按轴径初估
$Fr = 1200   # N，按轴径 φ30 估算的径向载荷
$Fa = 300    # N，轴向力
$X = 1.0; $Y = 1.4
$P_eq = [math]::Round($K_A * ($X*$Fr + $Y*$Fa), 1)
Write-Output "  径向载荷 Fr = $Fr N，轴向 Fa = $Fa N"
Write-Output "  当量动载荷 P = K_A·(X·Fr + Y·Fa) = $K_A·($X·$Fr + $Y·$Fa) = $P_eq N"

# 3) 由寿命反算所需动载荷（球轴承 ε=3）
$millions = $Lh * 60 * $n / 1e6
$eps = 3
$C_need = [math]::Round($P_eq * [math]::Pow($millions, 1/$eps), 1)
Write-Output "  寿命转数 = $Lh h × 60 × $n rpm = $([math]::Round($millions*1e6/1e6,1))×10^6 转"
Write-Output "  球轴承 ε=3 ⇒ C_需 = P × (寿命/10^6)^(1/3) = $P_eq × $([math]::Round($millions,2))^(1/3) = $C_need N = $([math]::Round($C_need/1000,2)) kN"

# 4) 查表选型
Write-Output ""
Write-Output "════ 查表选型（C ≥ $C_need N 且 n_lim ≥ $n）════"
$pick = @()
for ($i = 1; $i -lt $L.Count; $i++) {
    try { $b = Parse $L[$i] } catch { continue }
    if ($b.C -ge $C_need -and $b.nLim -ge $n) { $pick += $b }
}
$pick = $pick | Sort-Object d
if ($pick.Count -eq 0) {
    Write-Output "  ⚠ 表中无满足的型号（表内主要是小规格 M3~M5，功率偏大）"
    # 退而求其次：列出承载最接近的
    $all = @(); for ($i=1;$i -lt $L.Count;$i++){ try { $all += Parse $L[$i] } catch {} }
    $all | Sort-Object { [math]::Abs($_.C - $C_need) } | Select-Object -First 3 |
      ForEach-Object { Write-Output "     最近: $($_.Desig)  d=$($_.d) C=$($_.C)kN  差 $([math]::Round($_.C*1000-$C_need,0))N" }
} else {
    Write-Output "  满足条件的型号 $($pick.Count) 个（按内径排序，前 6 个）:"
    $pick | Select-Object -First 6 | ForEach-Object {
        Write-Output ("     {0,-10} d={1,4} D={2,4} B={3,4}  C={4,6}N  n_lim={5,7}  轴肩da={6,5}  ra={7}" -f `
            $_.Desig, $_.d, $_.D, $_.B, ($_.C*1000), $_.nLim, $_.da, $_.ra)
    }
    $best = $pick | Select-Object -First 1
    Write-Output ""
    Write-Output "════ 校核 ════"
    Write-Output "  选用 $($best.Desig)：C=$($best.C)kN / 需 $C_need N ⇒ 实际富余 $([math]::Round($best.C*1000-$C_need,0))N"
    $lifeChk = [math]::Round(($best.C*1000/$P_eq) * 3 * 1e6 / (60*$n) / 1e6, 2)
    Write-Output "  反算寿命 L10h = (C/P)³·10⁶/(60n) = $lifeChk 万小时（要求 $Lh h）"
    Write-Output "  转速校核：n_lim=$($best.nLim) ≥ $n ⇒ $(if($best.nLim -ge $n){'✅'}else{'❌'})"
}

# 5) 配合：按知识库 fits_iso286，φ30 的 H7/k6
Write-Output ""
Write-Output "════ 配合校核（fits_iso286.yaml，24~30 段）════"
$holeES = 21.0; $holeEI = 0.0     # H7
$axEs = 15.0;  $axEi = 2.0       # k6
$Xmax = $holeES - $axEi
$Xmin = $holeEI - $axEs
Write-Output "  H7 孔 (24~30): ES=+$holeES EI=$holeEI"
Write-Output "  k6 轴 (24~30): es=+$axEs ei=+$axEi"
Write-Output "  ⇒ Xmax = ES孔 − ei轴 = $Xmax μm（最大间隙）"
Write-Output "  ⇒ Xmin = EI孔 − es轴 = $Xmin μm（最大过盈）"
Write-Output "  ⇒ 过渡配合，过盈约 $([math]::Abs($Xmin)) μm = $([math]::Abs($Xmin)/1000) mm"
Write-Output "  ⇒ $(if($Xmin -lt 0){'✅ 轻中载旋转内圈：有过盈但小，便于装拆'}else{'⚠ 无过盈，是间隙配合'})"
.bore, $_.B, ($_.C*1000), $_.nLim, $_.da, $_.ra)
    }
    $best = $pick | Select-Object -First 1
    Write-Output ""
    Write-Output "════ 校核 ════"
    Write-Output "  选用 $($best.Desig)：C=$($best.C)kN / 需 $C_need N ⇒ 实际富余 $([math]::Round($best.C*1000-$C_need,0))N"
    $lifeChk = [math]::Round(($best.C*1000/$P_eq) * 3 * 1e6 / (60*$n) / 1e6, 2)
    Write-Output "  反算寿命 L10h = (C/P)³·10⁶/(60n) = $lifeChk 万小时（要求 $Lh h）"
    Write-Output "  转速校核：n_lim=$($best.nLim) ≥ $n ⇒ $(if($best.nLim -ge $n){'✅'}else{'❌'})"
}

# 5) 配合：按知识库 fits_iso286，φ30 的 H7/k6
Write-Output ""
Write-Output "════ 配合校核（fits_iso286.yaml，24~30 段）════"
$holeES = 21.0; $holeEI = 0.0     # H7
$axEs = 15.0;  $axEi = 2.0       # k6
$Xmax = $holeES - $axEi
$Xmin = $holeEI - $axEs
Write-Output "  H7 孔 (24~30): ES=+$holeES EI=$holeEI"
Write-Output "  k6 轴 (24~30): es=+$axEs ei=+$axEi"
Write-Output "  ⇒ Xmax = ES孔 − ei轴 = $Xmax μm（最大间隙）"
Write-Output "  ⇒ Xmin = EI孔 − es轴 = $Xmin μm（最大过盈）"
Write-Output "  ⇒ 过渡配合，过盈约 $([math]::Abs($Xmin)) μm = $([math]::Abs($Xmin)/1000) mm"
Write-Output "  ⇒ $(if($Xmin -lt 0){'✅ 轻中载旋转内圈：有过盈但小，便于装拆'}else{'⚠ 无过盈，是间隙配合'})"
.shell, # ★ 闭环验证：用轴承库 + 配合库 + 材料库 做一次真实选型
# 题目：设计一根传动轴，传递 P=2.2kW, n=1450 rpm，要求寿命 L10h=10000h
# 判据自检：算出的 C/C比 是否符合工程常识；选的型号是否真的在表里、n_lim 是否够

$csv = "C:\Users\Zegel\solidpilot-mcp\知识库\bearings\single_row_deep_groove_ball_bearing_parameters.csv"
$L = @(Get-Content $csv | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })

# 列位置（已验证）：1=d 2=D 3=B 4=C 5=C0 6=Pu 7=n_ref 8=n_lim 9=mass 10=Designation 15=da 17=ra
function Parse($line) {
    $r = $line.Split(',')
    [pscustomobject]@{
        bore = [double]$r[1]; shell = [double]$r[2]; wid = [double]$r[3]
        C  = [double]$r[4];  C0 = [double]$r[5];  Pu = [double]$r[6]
        nRef = [double]$r[7]; nLim = [double]$r[8]; mass = [double]$r[9]
        Desig = $r[10].Trim(); da = $r[15].Trim(); ra = $r[17].Trim()
    }
}

Write-Output "════ 工况 ════"
$P = 2.2; $n = 1450; $Lh = 10000
Write-Output "  功率 P = $P kW，转速 n = $n rpm，要求寿命 L10h = $Lh h"
# 1) 载荷系数（design_rules: 中等工况 K_A=1.3~1.5，轻载1.3）
$K_A = 1.3
Write-Output "  工况系数 K_A = $K_A（中等冲击）"

# 2) 当量动载荷 P = K_A × (轴承当量载荷)
#    ★ 简化：设径向为主，取载荷系数 X=1, Y=1.4（球轴承，Fr/Fr > e）
#    为演示取径向载荷 Fr = 0.5 × 轴向载荷极限，按轴径初估
$Fr = 1200   # N，按轴径 φ30 估算的径向载荷
$Fa = 300    # N，轴向力
$X = 1.0; $Y = 1.4
$P_eq = [math]::Round($K_A * ($X*$Fr + $Y*$Fa), 1)
Write-Output "  径向载荷 Fr = $Fr N，轴向 Fa = $Fa N"
Write-Output "  当量动载荷 P = K_A·(X·Fr + Y·Fa) = $K_A·($X·$Fr + $Y·$Fa) = $P_eq N"

# 3) 由寿命反算所需动载荷（球轴承 ε=3）
$millions = $Lh * 60 * $n / 1e6
$eps = 3
$C_need = [math]::Round($P_eq * [math]::Pow($millions, 1/$eps), 1)
Write-Output "  寿命转数 = $Lh h × 60 × $n rpm = $([math]::Round($millions*1e6/1e6,1))×10^6 转"
Write-Output "  球轴承 ε=3 ⇒ C_需 = P × (寿命/10^6)^(1/3) = $P_eq × $([math]::Round($millions,2))^(1/3) = $C_need N = $([math]::Round($C_need/1000,2)) kN"

# 4) 查表选型
Write-Output ""
Write-Output "════ 查表选型（C ≥ $C_need N 且 n_lim ≥ $n）════"
$pick = @()
for ($i = 1; $i -lt $L.Count; $i++) {
    try { $b = Parse $L[$i] } catch { continue }
    if ($b.C -ge $C_need -and $b.nLim -ge $n) { $pick += $b }
}
$pick = $pick | Sort-Object d
if ($pick.Count -eq 0) {
    Write-Output "  ⚠ 表中无满足的型号（表内主要是小规格 M3~M5，功率偏大）"
    # 退而求其次：列出承载最接近的
    $all = @(); for ($i=1;$i -lt $L.Count;$i++){ try { $all += Parse $L[$i] } catch {} }
    $all | Sort-Object { [math]::Abs($_.C - $C_need) } | Select-Object -First 3 |
      ForEach-Object { Write-Output "     最近: $($_.Desig)  d=$(# ★ 闭环验证：用轴承库 + 配合库 + 材料库 做一次真实选型
# 题目：设计一根传动轴，传递 P=2.2kW, n=1450 rpm，要求寿命 L10h=10000h
# 判据自检：算出的 C/C比 是否符合工程常识；选的型号是否真的在表里、n_lim 是否够

$csv = "C:\Users\Zegel\solidpilot-mcp\知识库\bearings\single_row_deep_groove_ball_bearing_parameters.csv"
$L = @(Get-Content $csv | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })

# 列位置（已验证）：1=d 2=D 3=B 4=C 5=C0 6=Pu 7=n_ref 8=n_lim 9=mass 10=Designation 15=da 17=ra
function Parse($line) {
    $r = $line.Split(',')
    [pscustomobject]@{
        bore = [double]$r[1]; shell = [double]$r[2]; wid = [double]$r[3]
        C  = [double]$r[4];  C0 = [double]$r[5];  Pu = [double]$r[6]
        nRef = [double]$r[7]; nLim = [double]$r[8]; mass = [double]$r[9]
        Desig = $r[10].Trim(); da = $r[15].Trim(); ra = $r[17].Trim()
    }
}

Write-Output "════ 工况 ════"
$P = 2.2; $n = 1450; $Lh = 10000
Write-Output "  功率 P = $P kW，转速 n = $n rpm，要求寿命 L10h = $Lh h"
# 1) 载荷系数（design_rules: 中等工况 K_A=1.3~1.5，轻载1.3）
$K_A = 1.3
Write-Output "  工况系数 K_A = $K_A（中等冲击）"

# 2) 当量动载荷 P = K_A × (轴承当量载荷)
#    ★ 简化：设径向为主，取载荷系数 X=1, Y=1.4（球轴承，Fr/Fr > e）
#    为演示取径向载荷 Fr = 0.5 × 轴向载荷极限，按轴径初估
$Fr = 1200   # N，按轴径 φ30 估算的径向载荷
$Fa = 300    # N，轴向力
$X = 1.0; $Y = 1.4
$P_eq = [math]::Round($K_A * ($X*$Fr + $Y*$Fa), 1)
Write-Output "  径向载荷 Fr = $Fr N，轴向 Fa = $Fa N"
Write-Output "  当量动载荷 P = K_A·(X·Fr + Y·Fa) = $K_A·($X·$Fr + $Y·$Fa) = $P_eq N"

# 3) 由寿命反算所需动载荷（球轴承 ε=3）
$millions = $Lh * 60 * $n / 1e6
$eps = 3
$C_need = [math]::Round($P_eq * [math]::Pow($millions, 1/$eps), 1)
Write-Output "  寿命转数 = $Lh h × 60 × $n rpm = $([math]::Round($millions*1e6/1e6,1))×10^6 转"
Write-Output "  球轴承 ε=3 ⇒ C_需 = P × (寿命/10^6)^(1/3) = $P_eq × $([math]::Round($millions,2))^(1/3) = $C_need N = $([math]::Round($C_need/1000,2)) kN"

# 4) 查表选型
Write-Output ""
Write-Output "════ 查表选型（C ≥ $C_need N 且 n_lim ≥ $n）════"
$pick = @()
for ($i = 1; $i -lt $L.Count; $i++) {
    try { $b = Parse $L[$i] } catch { continue }
    if ($b.C -ge $C_need -and $b.nLim -ge $n) { $pick += $b }
}
$pick = $pick | Sort-Object d
if ($pick.Count -eq 0) {
    Write-Output "  ⚠ 表中无满足的型号（表内主要是小规格 M3~M5，功率偏大）"
    # 退而求其次：列出承载最接近的
    $all = @(); for ($i=1;$i -lt $L.Count;$i++){ try { $all += Parse $L[$i] } catch {} }
    $all | Sort-Object { [math]::Abs($_.C - $C_need) } | Select-Object -First 3 |
      ForEach-Object { Write-Output "     最近: $($_.Desig)  d=$($_.d) C=$($_.C)kN  差 $([math]::Round($_.C*1000-$C_need,0))N" }
} else {
    Write-Output "  满足条件的型号 $($pick.Count) 个（按内径排序，前 6 个）:"
    $pick | Select-Object -First 6 | ForEach-Object {
        Write-Output ("     {0,-10} d={1,4} D={2,4} B={3,4}  C={4,6}N  n_lim={5,7}  轴肩da={6,5}  ra={7}" -f `
            $_.Desig, $_.d, $_.D, $_.B, ($_.C*1000), $_.nLim, $_.da, $_.ra)
    }
    $best = $pick | Select-Object -First 1
    Write-Output ""
    Write-Output "════ 校核 ════"
    Write-Output "  选用 $($best.Desig)：C=$($best.C)kN / 需 $C_need N ⇒ 实际富余 $([math]::Round($best.C*1000-$C_need,0))N"
    $lifeChk = [math]::Round(($best.C*1000/$P_eq) * 3 * 1e6 / (60*$n) / 1e6, 2)
    Write-Output "  反算寿命 L10h = (C/P)³·10⁶/(60n) = $lifeChk 万小时（要求 $Lh h）"
    Write-Output "  转速校核：n_lim=$($best.nLim) ≥ $n ⇒ $(if($best.nLim -ge $n){'✅'}else{'❌'})"
}

# 5) 配合：按知识库 fits_iso286，φ30 的 H7/k6
Write-Output ""
Write-Output "════ 配合校核（fits_iso286.yaml，24~30 段）════"
$holeES = 21.0; $holeEI = 0.0     # H7
$axEs = 15.0;  $axEi = 2.0       # k6
$Xmax = $holeES - $axEi
$Xmin = $holeEI - $axEs
Write-Output "  H7 孔 (24~30): ES=+$holeES EI=$holeEI"
Write-Output "  k6 轴 (24~30): es=+$axEs ei=+$axEi"
Write-Output "  ⇒ Xmax = ES孔 − ei轴 = $Xmax μm（最大间隙）"
Write-Output "  ⇒ Xmin = EI孔 − es轴 = $Xmin μm（最大过盈）"
Write-Output "  ⇒ 过渡配合，过盈约 $([math]::Abs($Xmin)) μm = $([math]::Abs($Xmin)/1000) mm"
Write-Output "  ⇒ $(if($Xmin -lt 0){'✅ 轻中载旋转内圈：有过盈但小，便于装拆'}else{'⚠ 无过盈，是间隙配合'})"
.bore) C=$($_.C)kN  差 $([math]::Round($_.C*1000-$C_need,0))N" }
} else {
    Write-Output "  满足条件的型号 $($pick.Count) 个（按内径排序，前 6 个）:"
    $pick | Select-Object -First 6 | ForEach-Object {
        Write-Output ("     {0,-10} d={1,4} D={2,4} B={3,4}  C={4,6}N  n_lim={5,7}  轴肩da={6,5}  ra={7}" -f `
            $_.Desig, # ★ 闭环验证：用轴承库 + 配合库 + 材料库 做一次真实选型
# 题目：设计一根传动轴，传递 P=2.2kW, n=1450 rpm，要求寿命 L10h=10000h
# 判据自检：算出的 C/C比 是否符合工程常识；选的型号是否真的在表里、n_lim 是否够

$csv = "C:\Users\Zegel\solidpilot-mcp\知识库\bearings\single_row_deep_groove_ball_bearing_parameters.csv"
$L = @(Get-Content $csv | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })

# 列位置（已验证）：1=d 2=D 3=B 4=C 5=C0 6=Pu 7=n_ref 8=n_lim 9=mass 10=Designation 15=da 17=ra
function Parse($line) {
    $r = $line.Split(',')
    [pscustomobject]@{
        bore = [double]$r[1]; shell = [double]$r[2]; wid = [double]$r[3]
        C  = [double]$r[4];  C0 = [double]$r[5];  Pu = [double]$r[6]
        nRef = [double]$r[7]; nLim = [double]$r[8]; mass = [double]$r[9]
        Desig = $r[10].Trim(); da = $r[15].Trim(); ra = $r[17].Trim()
    }
}

Write-Output "════ 工况 ════"
$P = 2.2; $n = 1450; $Lh = 10000
Write-Output "  功率 P = $P kW，转速 n = $n rpm，要求寿命 L10h = $Lh h"
# 1) 载荷系数（design_rules: 中等工况 K_A=1.3~1.5，轻载1.3）
$K_A = 1.3
Write-Output "  工况系数 K_A = $K_A（中等冲击）"

# 2) 当量动载荷 P = K_A × (轴承当量载荷)
#    ★ 简化：设径向为主，取载荷系数 X=1, Y=1.4（球轴承，Fr/Fr > e）
#    为演示取径向载荷 Fr = 0.5 × 轴向载荷极限，按轴径初估
$Fr = 1200   # N，按轴径 φ30 估算的径向载荷
$Fa = 300    # N，轴向力
$X = 1.0; $Y = 1.4
$P_eq = [math]::Round($K_A * ($X*$Fr + $Y*$Fa), 1)
Write-Output "  径向载荷 Fr = $Fr N，轴向 Fa = $Fa N"
Write-Output "  当量动载荷 P = K_A·(X·Fr + Y·Fa) = $K_A·($X·$Fr + $Y·$Fa) = $P_eq N"

# 3) 由寿命反算所需动载荷（球轴承 ε=3）
$millions = $Lh * 60 * $n / 1e6
$eps = 3
$C_need = [math]::Round($P_eq * [math]::Pow($millions, 1/$eps), 1)
Write-Output "  寿命转数 = $Lh h × 60 × $n rpm = $([math]::Round($millions*1e6/1e6,1))×10^6 转"
Write-Output "  球轴承 ε=3 ⇒ C_需 = P × (寿命/10^6)^(1/3) = $P_eq × $([math]::Round($millions,2))^(1/3) = $C_need N = $([math]::Round($C_need/1000,2)) kN"

# 4) 查表选型
Write-Output ""
Write-Output "════ 查表选型（C ≥ $C_need N 且 n_lim ≥ $n）════"
$pick = @()
for ($i = 1; $i -lt $L.Count; $i++) {
    try { $b = Parse $L[$i] } catch { continue }
    if ($b.C -ge $C_need -and $b.nLim -ge $n) { $pick += $b }
}
$pick = $pick | Sort-Object d
if ($pick.Count -eq 0) {
    Write-Output "  ⚠ 表中无满足的型号（表内主要是小规格 M3~M5，功率偏大）"
    # 退而求其次：列出承载最接近的
    $all = @(); for ($i=1;$i -lt $L.Count;$i++){ try { $all += Parse $L[$i] } catch {} }
    $all | Sort-Object { [math]::Abs($_.C - $C_need) } | Select-Object -First 3 |
      ForEach-Object { Write-Output "     最近: $($_.Desig)  d=$($_.d) C=$($_.C)kN  差 $([math]::Round($_.C*1000-$C_need,0))N" }
} else {
    Write-Output "  满足条件的型号 $($pick.Count) 个（按内径排序，前 6 个）:"
    $pick | Select-Object -First 6 | ForEach-Object {
        Write-Output ("     {0,-10} d={1,4} D={2,4} B={3,4}  C={4,6}N  n_lim={5,7}  轴肩da={6,5}  ra={7}" -f `
            $_.Desig, $_.d, $_.D, $_.B, ($_.C*1000), $_.nLim, $_.da, $_.ra)
    }
    $best = $pick | Select-Object -First 1
    Write-Output ""
    Write-Output "════ 校核 ════"
    Write-Output "  选用 $($best.Desig)：C=$($best.C)kN / 需 $C_need N ⇒ 实际富余 $([math]::Round($best.C*1000-$C_need,0))N"
    $lifeChk = [math]::Round(($best.C*1000/$P_eq) * 3 * 1e6 / (60*$n) / 1e6, 2)
    Write-Output "  反算寿命 L10h = (C/P)³·10⁶/(60n) = $lifeChk 万小时（要求 $Lh h）"
    Write-Output "  转速校核：n_lim=$($best.nLim) ≥ $n ⇒ $(if($best.nLim -ge $n){'✅'}else{'❌'})"
}

# 5) 配合：按知识库 fits_iso286，φ30 的 H7/k6
Write-Output ""
Write-Output "════ 配合校核（fits_iso286.yaml，24~30 段）════"
$holeES = 21.0; $holeEI = 0.0     # H7
$axEs = 15.0;  $axEi = 2.0       # k6
$Xmax = $holeES - $axEi
$Xmin = $holeEI - $axEs
Write-Output "  H7 孔 (24~30): ES=+$holeES EI=$holeEI"
Write-Output "  k6 轴 (24~30): es=+$axEs ei=+$axEi"
Write-Output "  ⇒ Xmax = ES孔 − ei轴 = $Xmax μm（最大间隙）"
Write-Output "  ⇒ Xmin = EI孔 − es轴 = $Xmin μm（最大过盈）"
Write-Output "  ⇒ 过渡配合，过盈约 $([math]::Abs($Xmin)) μm = $([math]::Abs($Xmin)/1000) mm"
Write-Output "  ⇒ $(if($Xmin -lt 0){'✅ 轻中载旋转内圈：有过盈但小，便于装拆'}else{'⚠ 无过盈，是间隙配合'})"
.bore, # ★ 闭环验证：用轴承库 + 配合库 + 材料库 做一次真实选型
# 题目：设计一根传动轴，传递 P=2.2kW, n=1450 rpm，要求寿命 L10h=10000h
# 判据自检：算出的 C/C比 是否符合工程常识；选的型号是否真的在表里、n_lim 是否够

$csv = "C:\Users\Zegel\solidpilot-mcp\知识库\bearings\single_row_deep_groove_ball_bearing_parameters.csv"
$L = @(Get-Content $csv | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })

# 列位置（已验证）：1=d 2=D 3=B 4=C 5=C0 6=Pu 7=n_ref 8=n_lim 9=mass 10=Designation 15=da 17=ra
function Parse($line) {
    $r = $line.Split(',')
    [pscustomobject]@{
        bore = [double]$r[1]; shell = [double]$r[2]; wid = [double]$r[3]
        C  = [double]$r[4];  C0 = [double]$r[5];  Pu = [double]$r[6]
        nRef = [double]$r[7]; nLim = [double]$r[8]; mass = [double]$r[9]
        Desig = $r[10].Trim(); da = $r[15].Trim(); ra = $r[17].Trim()
    }
}

Write-Output "════ 工况 ════"
$P = 2.2; $n = 1450; $Lh = 10000
Write-Output "  功率 P = $P kW，转速 n = $n rpm，要求寿命 L10h = $Lh h"
# 1) 载荷系数（design_rules: 中等工况 K_A=1.3~1.5，轻载1.3）
$K_A = 1.3
Write-Output "  工况系数 K_A = $K_A（中等冲击）"

# 2) 当量动载荷 P = K_A × (轴承当量载荷)
#    ★ 简化：设径向为主，取载荷系数 X=1, Y=1.4（球轴承，Fr/Fr > e）
#    为演示取径向载荷 Fr = 0.5 × 轴向载荷极限，按轴径初估
$Fr = 1200   # N，按轴径 φ30 估算的径向载荷
$Fa = 300    # N，轴向力
$X = 1.0; $Y = 1.4
$P_eq = [math]::Round($K_A * ($X*$Fr + $Y*$Fa), 1)
Write-Output "  径向载荷 Fr = $Fr N，轴向 Fa = $Fa N"
Write-Output "  当量动载荷 P = K_A·(X·Fr + Y·Fa) = $K_A·($X·$Fr + $Y·$Fa) = $P_eq N"

# 3) 由寿命反算所需动载荷（球轴承 ε=3）
$millions = $Lh * 60 * $n / 1e6
$eps = 3
$C_need = [math]::Round($P_eq * [math]::Pow($millions, 1/$eps), 1)
Write-Output "  寿命转数 = $Lh h × 60 × $n rpm = $([math]::Round($millions*1e6/1e6,1))×10^6 转"
Write-Output "  球轴承 ε=3 ⇒ C_需 = P × (寿命/10^6)^(1/3) = $P_eq × $([math]::Round($millions,2))^(1/3) = $C_need N = $([math]::Round($C_need/1000,2)) kN"

# 4) 查表选型
Write-Output ""
Write-Output "════ 查表选型（C ≥ $C_need N 且 n_lim ≥ $n）════"
$pick = @()
for ($i = 1; $i -lt $L.Count; $i++) {
    try { $b = Parse $L[$i] } catch { continue }
    if ($b.C -ge $C_need -and $b.nLim -ge $n) { $pick += $b }
}
$pick = $pick | Sort-Object d
if ($pick.Count -eq 0) {
    Write-Output "  ⚠ 表中无满足的型号（表内主要是小规格 M3~M5，功率偏大）"
    # 退而求其次：列出承载最接近的
    $all = @(); for ($i=1;$i -lt $L.Count;$i++){ try { $all += Parse $L[$i] } catch {} }
    $all | Sort-Object { [math]::Abs($_.C - $C_need) } | Select-Object -First 3 |
      ForEach-Object { Write-Output "     最近: $($_.Desig)  d=$($_.d) C=$($_.C)kN  差 $([math]::Round($_.C*1000-$C_need,0))N" }
} else {
    Write-Output "  满足条件的型号 $($pick.Count) 个（按内径排序，前 6 个）:"
    $pick | Select-Object -First 6 | ForEach-Object {
        Write-Output ("     {0,-10} d={1,4} D={2,4} B={3,4}  C={4,6}N  n_lim={5,7}  轴肩da={6,5}  ra={7}" -f `
            $_.Desig, $_.d, $_.D, $_.B, ($_.C*1000), $_.nLim, $_.da, $_.ra)
    }
    $best = $pick | Select-Object -First 1
    Write-Output ""
    Write-Output "════ 校核 ════"
    Write-Output "  选用 $($best.Desig)：C=$($best.C)kN / 需 $C_need N ⇒ 实际富余 $([math]::Round($best.C*1000-$C_need,0))N"
    $lifeChk = [math]::Round(($best.C*1000/$P_eq) * 3 * 1e6 / (60*$n) / 1e6, 2)
    Write-Output "  反算寿命 L10h = (C/P)³·10⁶/(60n) = $lifeChk 万小时（要求 $Lh h）"
    Write-Output "  转速校核：n_lim=$($best.nLim) ≥ $n ⇒ $(if($best.nLim -ge $n){'✅'}else{'❌'})"
}

# 5) 配合：按知识库 fits_iso286，φ30 的 H7/k6
Write-Output ""
Write-Output "════ 配合校核（fits_iso286.yaml，24~30 段）════"
$holeES = 21.0; $holeEI = 0.0     # H7
$axEs = 15.0;  $axEi = 2.0       # k6
$Xmax = $holeES - $axEi
$Xmin = $holeEI - $axEs
Write-Output "  H7 孔 (24~30): ES=+$holeES EI=$holeEI"
Write-Output "  k6 轴 (24~30): es=+$axEs ei=+$axEi"
Write-Output "  ⇒ Xmax = ES孔 − ei轴 = $Xmax μm（最大间隙）"
Write-Output "  ⇒ Xmin = EI孔 − es轴 = $Xmin μm（最大过盈）"
Write-Output "  ⇒ 过渡配合，过盈约 $([math]::Abs($Xmin)) μm = $([math]::Abs($Xmin)/1000) mm"
Write-Output "  ⇒ $(if($Xmin -lt 0){'✅ 轻中载旋转内圈：有过盈但小，便于装拆'}else{'⚠ 无过盈，是间隙配合'})"
.bore, $_.B, ($_.C*1000), $_.nLim, $_.da, $_.ra)
    }
    $best = $pick | Select-Object -First 1
    Write-Output ""
    Write-Output "════ 校核 ════"
    Write-Output "  选用 $($best.Desig)：C=$($best.C)kN / 需 $C_need N ⇒ 实际富余 $([math]::Round($best.C*1000-$C_need,0))N"
    $lifeChk = [math]::Round(($best.C*1000/$P_eq) * 3 * 1e6 / (60*$n) / 1e6, 2)
    Write-Output "  反算寿命 L10h = (C/P)³·10⁶/(60n) = $lifeChk 万小时（要求 $Lh h）"
    Write-Output "  转速校核：n_lim=$($best.nLim) ≥ $n ⇒ $(if($best.nLim -ge $n){'✅'}else{'❌'})"
}

# 5) 配合：按知识库 fits_iso286，φ30 的 H7/k6
Write-Output ""
Write-Output "════ 配合校核（fits_iso286.yaml，24~30 段）════"
$holeES = 21.0; $holeEI = 0.0     # H7
$axEs = 15.0;  $axEi = 2.0       # k6
$Xmax = $holeES - $axEi
$Xmin = $holeEI - $axEs
Write-Output "  H7 孔 (24~30): ES=+$holeES EI=$holeEI"
Write-Output "  k6 轴 (24~30): es=+$axEs ei=+$axEi"
Write-Output "  ⇒ Xmax = ES孔 − ei轴 = $Xmax μm（最大间隙）"
Write-Output "  ⇒ Xmin = EI孔 − es轴 = $Xmin μm（最大过盈）"
Write-Output "  ⇒ 过渡配合，过盈约 $([math]::Abs($Xmin)) μm = $([math]::Abs($Xmin)/1000) mm"
Write-Output "  ⇒ $(if($Xmin -lt 0){'✅ 轻中载旋转内圈：有过盈但小，便于装拆'}else{'⚠ 无过盈，是间隙配合'})"
.shell, $_.B, ($_.C*1000), $_.nLim, $_.da, $_.ra)
    }
    $best = $pick | Select-Object -First 1
    Write-Output ""
    Write-Output "════ 校核 ════"
    Write-Output "  选用 $($best.Desig)：C=$($best.C)kN / 需 $C_need N ⇒ 实际富余 $([math]::Round($best.C*1000-$C_need,0))N"
    $lifeChk = [math]::Round(($best.C*1000/$P_eq) * 3 * 1e6 / (60*$n) / 1e6, 2)
    Write-Output "  反算寿命 L10h = (C/P)³·10⁶/(60n) = $lifeChk 万小时（要求 $Lh h）"
    Write-Output "  转速校核：n_lim=$($best.nLim) ≥ $n ⇒ $(if($best.nLim -ge $n){'✅'}else{'❌'})"
}

# 5) 配合：按知识库 fits_iso286，φ30 的 H7/k6
Write-Output ""
Write-Output "════ 配合校核（fits_iso286.yaml，24~30 段）════"
$holeES = 21.0; $holeEI = 0.0     # H7
$axEs = 15.0;  $axEi = 2.0       # k6
$Xmax = $holeES - $axEi
$Xmin = $holeEI - $axEs
Write-Output "  H7 孔 (24~30): ES=+$holeES EI=$holeEI"
Write-Output "  k6 轴 (24~30): es=+$axEs ei=+$axEi"
Write-Output "  ⇒ Xmax = ES孔 − ei轴 = $Xmax μm（最大间隙）"
Write-Output "  ⇒ Xmin = EI孔 − es轴 = $Xmin μm（最大过盈）"
Write-Output "  ⇒ 过渡配合，过盈约 $([math]::Abs($Xmin)) μm = $([math]::Abs($Xmin)/1000) mm"
Write-Output "  ⇒ $(if($Xmin -lt 0){'✅ 轻中载旋转内圈：有过盈但小，便于装拆'}else{'⚠ 无过盈，是间隙配合'})"
.bore) C=$($_.C)kN  差 $([math]::Round($_.C*1000-$C_need,0))N" }
} else {
    Write-Output "  满足条件的型号 $($pick.Count) 个（按内径排序，前 6 个）:"
    $pick | Select-Object -First 6 | ForEach-Object {
        Write-Output ("     {0,-10} d={1,4} D={2,4} B={3,4}  C={4,6}N  n_lim={5,7}  轴肩da={6,5}  ra={7}" -f `
            $_.Desig, # ★ 闭环验证：用轴承库 + 配合库 + 材料库 做一次真实选型
# 题目：设计一根传动轴，传递 P=2.2kW, n=1450 rpm，要求寿命 L10h=10000h
# 判据自检：算出的 C/C比 是否符合工程常识；选的型号是否真的在表里、n_lim 是否够

$csv = "C:\Users\Zegel\solidpilot-mcp\知识库\bearings\single_row_deep_groove_ball_bearing_parameters.csv"
$L = @(Get-Content $csv | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })

# 列位置（已验证）：1=d 2=D 3=B 4=C 5=C0 6=Pu 7=n_ref 8=n_lim 9=mass 10=Designation 15=da 17=ra
function Parse($line) {
    $r = $line.Split(',')
    [pscustomobject]@{
        bore = [double]$r[1]; shell = [double]$r[2]; wid = [double]$r[3]
        C  = [double]$r[4];  C0 = [double]$r[5];  Pu = [double]$r[6]
        nRef = [double]$r[7]; nLim = [double]$r[8]; mass = [double]$r[9]
        Desig = $r[10].Trim(); da = $r[15].Trim(); ra = $r[17].Trim()
    }
}

Write-Output "════ 工况 ════"
$P = 2.2; $n = 1450; $Lh = 10000
Write-Output "  功率 P = $P kW，转速 n = $n rpm，要求寿命 L10h = $Lh h"
# 1) 载荷系数（design_rules: 中等工况 K_A=1.3~1.5，轻载1.3）
$K_A = 1.3
Write-Output "  工况系数 K_A = $K_A（中等冲击）"

# 2) 当量动载荷 P = K_A × (轴承当量载荷)
#    ★ 简化：设径向为主，取载荷系数 X=1, Y=1.4（球轴承，Fr/Fr > e）
#    为演示取径向载荷 Fr = 0.5 × 轴向载荷极限，按轴径初估
$Fr = 1200   # N，按轴径 φ30 估算的径向载荷
$Fa = 300    # N，轴向力
$X = 1.0; $Y = 1.4
$P_eq = [math]::Round($K_A * ($X*$Fr + $Y*$Fa), 1)
Write-Output "  径向载荷 Fr = $Fr N，轴向 Fa = $Fa N"
Write-Output "  当量动载荷 P = K_A·(X·Fr + Y·Fa) = $K_A·($X·$Fr + $Y·$Fa) = $P_eq N"

# 3) 由寿命反算所需动载荷（球轴承 ε=3）
$millions = $Lh * 60 * $n / 1e6
$eps = 3
$C_need = [math]::Round($P_eq * [math]::Pow($millions, 1/$eps), 1)
Write-Output "  寿命转数 = $Lh h × 60 × $n rpm = $([math]::Round($millions*1e6/1e6,1))×10^6 转"
Write-Output "  球轴承 ε=3 ⇒ C_需 = P × (寿命/10^6)^(1/3) = $P_eq × $([math]::Round($millions,2))^(1/3) = $C_need N = $([math]::Round($C_need/1000,2)) kN"

# 4) 查表选型
Write-Output ""
Write-Output "════ 查表选型（C ≥ $C_need N 且 n_lim ≥ $n）════"
$pick = @()
for ($i = 1; $i -lt $L.Count; $i++) {
    try { $b = Parse $L[$i] } catch { continue }
    if ($b.C -ge $C_need -and $b.nLim -ge $n) { $pick += $b }
}
$pick = $pick | Sort-Object d
if ($pick.Count -eq 0) {
    Write-Output "  ⚠ 表中无满足的型号（表内主要是小规格 M3~M5，功率偏大）"
    # 退而求其次：列出承载最接近的
    $all = @(); for ($i=1;$i -lt $L.Count;$i++){ try { $all += Parse $L[$i] } catch {} }
    $all | Sort-Object { [math]::Abs($_.C - $C_need) } | Select-Object -First 3 |
      ForEach-Object { Write-Output "     最近: $($_.Desig)  d=$(# ★ 闭环验证：用轴承库 + 配合库 + 材料库 做一次真实选型
# 题目：设计一根传动轴，传递 P=2.2kW, n=1450 rpm，要求寿命 L10h=10000h
# 判据自检：算出的 C/C比 是否符合工程常识；选的型号是否真的在表里、n_lim 是否够

$csv = "C:\Users\Zegel\solidpilot-mcp\知识库\bearings\single_row_deep_groove_ball_bearing_parameters.csv"
$L = @(Get-Content $csv | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })

# 列位置（已验证）：1=d 2=D 3=B 4=C 5=C0 6=Pu 7=n_ref 8=n_lim 9=mass 10=Designation 15=da 17=ra
function Parse($line) {
    $r = $line.Split(',')
    [pscustomobject]@{
        bore = [double]$r[1]; shell = [double]$r[2]; wid = [double]$r[3]
        C  = [double]$r[4];  C0 = [double]$r[5];  Pu = [double]$r[6]
        nRef = [double]$r[7]; nLim = [double]$r[8]; mass = [double]$r[9]
        Desig = $r[10].Trim(); da = $r[15].Trim(); ra = $r[17].Trim()
    }
}

Write-Output "════ 工况 ════"
$P = 2.2; $n = 1450; $Lh = 10000
Write-Output "  功率 P = $P kW，转速 n = $n rpm，要求寿命 L10h = $Lh h"
# 1) 载荷系数（design_rules: 中等工况 K_A=1.3~1.5，轻载1.3）
$K_A = 1.3
Write-Output "  工况系数 K_A = $K_A（中等冲击）"

# 2) 当量动载荷 P = K_A × (轴承当量载荷)
#    ★ 简化：设径向为主，取载荷系数 X=1, Y=1.4（球轴承，Fr/Fr > e）
#    为演示取径向载荷 Fr = 0.5 × 轴向载荷极限，按轴径初估
$Fr = 1200   # N，按轴径 φ30 估算的径向载荷
$Fa = 300    # N，轴向力
$X = 1.0; $Y = 1.4
$P_eq = [math]::Round($K_A * ($X*$Fr + $Y*$Fa), 1)
Write-Output "  径向载荷 Fr = $Fr N，轴向 Fa = $Fa N"
Write-Output "  当量动载荷 P = K_A·(X·Fr + Y·Fa) = $K_A·($X·$Fr + $Y·$Fa) = $P_eq N"

# 3) 由寿命反算所需动载荷（球轴承 ε=3）
$millions = $Lh * 60 * $n / 1e6
$eps = 3
$C_need = [math]::Round($P_eq * [math]::Pow($millions, 1/$eps), 1)
Write-Output "  寿命转数 = $Lh h × 60 × $n rpm = $([math]::Round($millions*1e6/1e6,1))×10^6 转"
Write-Output "  球轴承 ε=3 ⇒ C_需 = P × (寿命/10^6)^(1/3) = $P_eq × $([math]::Round($millions,2))^(1/3) = $C_need N = $([math]::Round($C_need/1000,2)) kN"

# 4) 查表选型
Write-Output ""
Write-Output "════ 查表选型（C ≥ $C_need N 且 n_lim ≥ $n）════"
$pick = @()
for ($i = 1; $i -lt $L.Count; $i++) {
    try { $b = Parse $L[$i] } catch { continue }
    if ($b.C -ge $C_need -and $b.nLim -ge $n) { $pick += $b }
}
$pick = $pick | Sort-Object d
if ($pick.Count -eq 0) {
    Write-Output "  ⚠ 表中无满足的型号（表内主要是小规格 M3~M5，功率偏大）"
    # 退而求其次：列出承载最接近的
    $all = @(); for ($i=1;$i -lt $L.Count;$i++){ try { $all += Parse $L[$i] } catch {} }
    $all | Sort-Object { [math]::Abs($_.C - $C_need) } | Select-Object -First 3 |
      ForEach-Object { Write-Output "     最近: $($_.Desig)  d=$(# ★ 闭环验证：用轴承库 + 配合库 + 材料库 做一次真实选型
# 题目：设计一根传动轴，传递 P=2.2kW, n=1450 rpm，要求寿命 L10h=10000h
# 判据自检：算出的 C/C比 是否符合工程常识；选的型号是否真的在表里、n_lim 是否够

$csv = "C:\Users\Zegel\solidpilot-mcp\知识库\bearings\single_row_deep_groove_ball_bearing_parameters.csv"
$L = @(Get-Content $csv | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })

# 列位置（已验证）：1=d 2=D 3=B 4=C 5=C0 6=Pu 7=n_ref 8=n_lim 9=mass 10=Designation 15=da 17=ra
function Parse($line) {
    $r = $line.Split(',')
    [pscustomobject]@{
        bore = [double]$r[1]; shell = [double]$r[2]; wid = [double]$r[3]
        C  = [double]$r[4];  C0 = [double]$r[5];  Pu = [double]$r[6]
        nRef = [double]$r[7]; nLim = [double]$r[8]; mass = [double]$r[9]
        Desig = $r[10].Trim(); da = $r[15].Trim(); ra = $r[17].Trim()
    }
}

Write-Output "════ 工况 ════"
$P = 2.2; $n = 1450; $Lh = 10000
Write-Output "  功率 P = $P kW，转速 n = $n rpm，要求寿命 L10h = $Lh h"
# 1) 载荷系数（design_rules: 中等工况 K_A=1.3~1.5，轻载1.3）
$K_A = 1.3
Write-Output "  工况系数 K_A = $K_A（中等冲击）"

# 2) 当量动载荷 P = K_A × (轴承当量载荷)
#    ★ 简化：设径向为主，取载荷系数 X=1, Y=1.4（球轴承，Fr/Fr > e）
#    为演示取径向载荷 Fr = 0.5 × 轴向载荷极限，按轴径初估
$Fr = 1200   # N，按轴径 φ30 估算的径向载荷
$Fa = 300    # N，轴向力
$X = 1.0; $Y = 1.4
$P_eq = [math]::Round($K_A * ($X*$Fr + $Y*$Fa), 1)
Write-Output "  径向载荷 Fr = $Fr N，轴向 Fa = $Fa N"
Write-Output "  当量动载荷 P = K_A·(X·Fr + Y·Fa) = $K_A·($X·$Fr + $Y·$Fa) = $P_eq N"

# 3) 由寿命反算所需动载荷（球轴承 ε=3）
$millions = $Lh * 60 * $n / 1e6
$eps = 3
$C_need = [math]::Round($P_eq * [math]::Pow($millions, 1/$eps), 1)
Write-Output "  寿命转数 = $Lh h × 60 × $n rpm = $([math]::Round($millions*1e6/1e6,1))×10^6 转"
Write-Output "  球轴承 ε=3 ⇒ C_需 = P × (寿命/10^6)^(1/3) = $P_eq × $([math]::Round($millions,2))^(1/3) = $C_need N = $([math]::Round($C_need/1000,2)) kN"

# 4) 查表选型
Write-Output ""
Write-Output "════ 查表选型（C ≥ $C_need N 且 n_lim ≥ $n）════"
$pick = @()
for ($i = 1; $i -lt $L.Count; $i++) {
    try { $b = Parse $L[$i] } catch { continue }
    if ($b.C -ge $C_need -and $b.nLim -ge $n) { $pick += $b }
}
$pick = $pick | Sort-Object d
if ($pick.Count -eq 0) {
    Write-Output "  ⚠ 表中无满足的型号（表内主要是小规格 M3~M5，功率偏大）"
    # 退而求其次：列出承载最接近的
    $all = @(); for ($i=1;$i -lt $L.Count;$i++){ try { $all += Parse $L[$i] } catch {} }
    $all | Sort-Object { [math]::Abs($_.C - $C_need) } | Select-Object -First 3 |
      ForEach-Object { Write-Output "     最近: $($_.Desig)  d=$($_.d) C=$($_.C)kN  差 $([math]::Round($_.C*1000-$C_need,0))N" }
} else {
    Write-Output "  满足条件的型号 $($pick.Count) 个（按内径排序，前 6 个）:"
    $pick | Select-Object -First 6 | ForEach-Object {
        Write-Output ("     {0,-10} d={1,4} D={2,4} B={3,4}  C={4,6}N  n_lim={5,7}  轴肩da={6,5}  ra={7}" -f `
            $_.Desig, $_.d, $_.D, $_.B, ($_.C*1000), $_.nLim, $_.da, $_.ra)
    }
    $best = $pick | Select-Object -First 1
    Write-Output ""
    Write-Output "════ 校核 ════"
    Write-Output "  选用 $($best.Desig)：C=$($best.C)kN / 需 $C_need N ⇒ 实际富余 $([math]::Round($best.C*1000-$C_need,0))N"
    $lifeChk = [math]::Round(($best.C*1000/$P_eq) * 3 * 1e6 / (60*$n) / 1e6, 2)
    Write-Output "  反算寿命 L10h = (C/P)³·10⁶/(60n) = $lifeChk 万小时（要求 $Lh h）"
    Write-Output "  转速校核：n_lim=$($best.nLim) ≥ $n ⇒ $(if($best.nLim -ge $n){'✅'}else{'❌'})"
}

# 5) 配合：按知识库 fits_iso286，φ30 的 H7/k6
Write-Output ""
Write-Output "════ 配合校核（fits_iso286.yaml，24~30 段）════"
$holeES = 21.0; $holeEI = 0.0     # H7
$axEs = 15.0;  $axEi = 2.0       # k6
$Xmax = $holeES - $axEi
$Xmin = $holeEI - $axEs
Write-Output "  H7 孔 (24~30): ES=+$holeES EI=$holeEI"
Write-Output "  k6 轴 (24~30): es=+$axEs ei=+$axEi"
Write-Output "  ⇒ Xmax = ES孔 − ei轴 = $Xmax μm（最大间隙）"
Write-Output "  ⇒ Xmin = EI孔 − es轴 = $Xmin μm（最大过盈）"
Write-Output "  ⇒ 过渡配合，过盈约 $([math]::Abs($Xmin)) μm = $([math]::Abs($Xmin)/1000) mm"
Write-Output "  ⇒ $(if($Xmin -lt 0){'✅ 轻中载旋转内圈：有过盈但小，便于装拆'}else{'⚠ 无过盈，是间隙配合'})"
.bore) C=$($_.C)kN  差 $([math]::Round($_.C*1000-$C_need,0))N" }
} else {
    Write-Output "  满足条件的型号 $($pick.Count) 个（按内径排序，前 6 个）:"
    $pick | Select-Object -First 6 | ForEach-Object {
        Write-Output ("     {0,-10} d={1,4} D={2,4} B={3,4}  C={4,6}N  n_lim={5,7}  轴肩da={6,5}  ra={7}" -f `
            $_.Desig, # ★ 闭环验证：用轴承库 + 配合库 + 材料库 做一次真实选型
# 题目：设计一根传动轴，传递 P=2.2kW, n=1450 rpm，要求寿命 L10h=10000h
# 判据自检：算出的 C/C比 是否符合工程常识；选的型号是否真的在表里、n_lim 是否够

$csv = "C:\Users\Zegel\solidpilot-mcp\知识库\bearings\single_row_deep_groove_ball_bearing_parameters.csv"
$L = @(Get-Content $csv | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })

# 列位置（已验证）：1=d 2=D 3=B 4=C 5=C0 6=Pu 7=n_ref 8=n_lim 9=mass 10=Designation 15=da 17=ra
function Parse($line) {
    $r = $line.Split(',')
    [pscustomobject]@{
        bore = [double]$r[1]; shell = [double]$r[2]; wid = [double]$r[3]
        C  = [double]$r[4];  C0 = [double]$r[5];  Pu = [double]$r[6]
        nRef = [double]$r[7]; nLim = [double]$r[8]; mass = [double]$r[9]
        Desig = $r[10].Trim(); da = $r[15].Trim(); ra = $r[17].Trim()
    }
}

Write-Output "════ 工况 ════"
$P = 2.2; $n = 1450; $Lh = 10000
Write-Output "  功率 P = $P kW，转速 n = $n rpm，要求寿命 L10h = $Lh h"
# 1) 载荷系数（design_rules: 中等工况 K_A=1.3~1.5，轻载1.3）
$K_A = 1.3
Write-Output "  工况系数 K_A = $K_A（中等冲击）"

# 2) 当量动载荷 P = K_A × (轴承当量载荷)
#    ★ 简化：设径向为主，取载荷系数 X=1, Y=1.4（球轴承，Fr/Fr > e）
#    为演示取径向载荷 Fr = 0.5 × 轴向载荷极限，按轴径初估
$Fr = 1200   # N，按轴径 φ30 估算的径向载荷
$Fa = 300    # N，轴向力
$X = 1.0; $Y = 1.4
$P_eq = [math]::Round($K_A * ($X*$Fr + $Y*$Fa), 1)
Write-Output "  径向载荷 Fr = $Fr N，轴向 Fa = $Fa N"
Write-Output "  当量动载荷 P = K_A·(X·Fr + Y·Fa) = $K_A·($X·$Fr + $Y·$Fa) = $P_eq N"

# 3) 由寿命反算所需动载荷（球轴承 ε=3）
$millions = $Lh * 60 * $n / 1e6
$eps = 3
$C_need = [math]::Round($P_eq * [math]::Pow($millions, 1/$eps), 1)
Write-Output "  寿命转数 = $Lh h × 60 × $n rpm = $([math]::Round($millions*1e6/1e6,1))×10^6 转"
Write-Output "  球轴承 ε=3 ⇒ C_需 = P × (寿命/10^6)^(1/3) = $P_eq × $([math]::Round($millions,2))^(1/3) = $C_need N = $([math]::Round($C_need/1000,2)) kN"

# 4) 查表选型
Write-Output ""
Write-Output "════ 查表选型（C ≥ $C_need N 且 n_lim ≥ $n）════"
$pick = @()
for ($i = 1; $i -lt $L.Count; $i++) {
    try { $b = Parse $L[$i] } catch { continue }
    if ($b.C -ge $C_need -and $b.nLim -ge $n) { $pick += $b }
}
$pick = $pick | Sort-Object d
if ($pick.Count -eq 0) {
    Write-Output "  ⚠ 表中无满足的型号（表内主要是小规格 M3~M5，功率偏大）"
    # 退而求其次：列出承载最接近的
    $all = @(); for ($i=1;$i -lt $L.Count;$i++){ try { $all += Parse $L[$i] } catch {} }
    $all | Sort-Object { [math]::Abs($_.C - $C_need) } | Select-Object -First 3 |
      ForEach-Object { Write-Output "     最近: $($_.Desig)  d=$($_.d) C=$($_.C)kN  差 $([math]::Round($_.C*1000-$C_need,0))N" }
} else {
    Write-Output "  满足条件的型号 $($pick.Count) 个（按内径排序，前 6 个）:"
    $pick | Select-Object -First 6 | ForEach-Object {
        Write-Output ("     {0,-10} d={1,4} D={2,4} B={3,4}  C={4,6}N  n_lim={5,7}  轴肩da={6,5}  ra={7}" -f `
            $_.Desig, $_.d, $_.D, $_.B, ($_.C*1000), $_.nLim, $_.da, $_.ra)
    }
    $best = $pick | Select-Object -First 1
    Write-Output ""
    Write-Output "════ 校核 ════"
    Write-Output "  选用 $($best.Desig)：C=$($best.C)kN / 需 $C_need N ⇒ 实际富余 $([math]::Round($best.C*1000-$C_need,0))N"
    $lifeChk = [math]::Round(($best.C*1000/$P_eq) * 3 * 1e6 / (60*$n) / 1e6, 2)
    Write-Output "  反算寿命 L10h = (C/P)³·10⁶/(60n) = $lifeChk 万小时（要求 $Lh h）"
    Write-Output "  转速校核：n_lim=$($best.nLim) ≥ $n ⇒ $(if($best.nLim -ge $n){'✅'}else{'❌'})"
}

# 5) 配合：按知识库 fits_iso286，φ30 的 H7/k6
Write-Output ""
Write-Output "════ 配合校核（fits_iso286.yaml，24~30 段）════"
$holeES = 21.0; $holeEI = 0.0     # H7
$axEs = 15.0;  $axEi = 2.0       # k6
$Xmax = $holeES - $axEi
$Xmin = $holeEI - $axEs
Write-Output "  H7 孔 (24~30): ES=+$holeES EI=$holeEI"
Write-Output "  k6 轴 (24~30): es=+$axEs ei=+$axEi"
Write-Output "  ⇒ Xmax = ES孔 − ei轴 = $Xmax μm（最大间隙）"
Write-Output "  ⇒ Xmin = EI孔 − es轴 = $Xmin μm（最大过盈）"
Write-Output "  ⇒ 过渡配合，过盈约 $([math]::Abs($Xmin)) μm = $([math]::Abs($Xmin)/1000) mm"
Write-Output "  ⇒ $(if($Xmin -lt 0){'✅ 轻中载旋转内圈：有过盈但小，便于装拆'}else{'⚠ 无过盈，是间隙配合'})"
.bore, # ★ 闭环验证：用轴承库 + 配合库 + 材料库 做一次真实选型
# 题目：设计一根传动轴，传递 P=2.2kW, n=1450 rpm，要求寿命 L10h=10000h
# 判据自检：算出的 C/C比 是否符合工程常识；选的型号是否真的在表里、n_lim 是否够

$csv = "C:\Users\Zegel\solidpilot-mcp\知识库\bearings\single_row_deep_groove_ball_bearing_parameters.csv"
$L = @(Get-Content $csv | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })

# 列位置（已验证）：1=d 2=D 3=B 4=C 5=C0 6=Pu 7=n_ref 8=n_lim 9=mass 10=Designation 15=da 17=ra
function Parse($line) {
    $r = $line.Split(',')
    [pscustomobject]@{
        bore = [double]$r[1]; shell = [double]$r[2]; wid = [double]$r[3]
        C  = [double]$r[4];  C0 = [double]$r[5];  Pu = [double]$r[6]
        nRef = [double]$r[7]; nLim = [double]$r[8]; mass = [double]$r[9]
        Desig = $r[10].Trim(); da = $r[15].Trim(); ra = $r[17].Trim()
    }
}

Write-Output "════ 工况 ════"
$P = 2.2; $n = 1450; $Lh = 10000
Write-Output "  功率 P = $P kW，转速 n = $n rpm，要求寿命 L10h = $Lh h"
# 1) 载荷系数（design_rules: 中等工况 K_A=1.3~1.5，轻载1.3）
$K_A = 1.3
Write-Output "  工况系数 K_A = $K_A（中等冲击）"

# 2) 当量动载荷 P = K_A × (轴承当量载荷)
#    ★ 简化：设径向为主，取载荷系数 X=1, Y=1.4（球轴承，Fr/Fr > e）
#    为演示取径向载荷 Fr = 0.5 × 轴向载荷极限，按轴径初估
$Fr = 1200   # N，按轴径 φ30 估算的径向载荷
$Fa = 300    # N，轴向力
$X = 1.0; $Y = 1.4
$P_eq = [math]::Round($K_A * ($X*$Fr + $Y*$Fa), 1)
Write-Output "  径向载荷 Fr = $Fr N，轴向 Fa = $Fa N"
Write-Output "  当量动载荷 P = K_A·(X·Fr + Y·Fa) = $K_A·($X·$Fr + $Y·$Fa) = $P_eq N"

# 3) 由寿命反算所需动载荷（球轴承 ε=3）
$millions = $Lh * 60 * $n / 1e6
$eps = 3
$C_need = [math]::Round($P_eq * [math]::Pow($millions, 1/$eps), 1)
Write-Output "  寿命转数 = $Lh h × 60 × $n rpm = $([math]::Round($millions*1e6/1e6,1))×10^6 转"
Write-Output "  球轴承 ε=3 ⇒ C_需 = P × (寿命/10^6)^(1/3) = $P_eq × $([math]::Round($millions,2))^(1/3) = $C_need N = $([math]::Round($C_need/1000,2)) kN"

# 4) 查表选型
Write-Output ""
Write-Output "════ 查表选型（C ≥ $C_need N 且 n_lim ≥ $n）════"
$pick = @()
for ($i = 1; $i -lt $L.Count; $i++) {
    try { $b = Parse $L[$i] } catch { continue }
    if ($b.C -ge $C_need -and $b.nLim -ge $n) { $pick += $b }
}
$pick = $pick | Sort-Object d
if ($pick.Count -eq 0) {
    Write-Output "  ⚠ 表中无满足的型号（表内主要是小规格 M3~M5，功率偏大）"
    # 退而求其次：列出承载最接近的
    $all = @(); for ($i=1;$i -lt $L.Count;$i++){ try { $all += Parse $L[$i] } catch {} }
    $all | Sort-Object { [math]::Abs($_.C - $C_need) } | Select-Object -First 3 |
      ForEach-Object { Write-Output "     最近: $($_.Desig)  d=$($_.d) C=$($_.C)kN  差 $([math]::Round($_.C*1000-$C_need,0))N" }
} else {
    Write-Output "  满足条件的型号 $($pick.Count) 个（按内径排序，前 6 个）:"
    $pick | Select-Object -First 6 | ForEach-Object {
        Write-Output ("     {0,-10} d={1,4} D={2,4} B={3,4}  C={4,6}N  n_lim={5,7}  轴肩da={6,5}  ra={7}" -f `
            $_.Desig, $_.d, $_.D, $_.B, ($_.C*1000), $_.nLim, $_.da, $_.ra)
    }
    $best = $pick | Select-Object -First 1
    Write-Output ""
    Write-Output "════ 校核 ════"
    Write-Output "  选用 $($best.Desig)：C=$($best.C)kN / 需 $C_need N ⇒ 实际富余 $([math]::Round($best.C*1000-$C_need,0))N"
    $lifeChk = [math]::Round(($best.C*1000/$P_eq) * 3 * 1e6 / (60*$n) / 1e6, 2)
    Write-Output "  反算寿命 L10h = (C/P)³·10⁶/(60n) = $lifeChk 万小时（要求 $Lh h）"
    Write-Output "  转速校核：n_lim=$($best.nLim) ≥ $n ⇒ $(if($best.nLim -ge $n){'✅'}else{'❌'})"
}

# 5) 配合：按知识库 fits_iso286，φ30 的 H7/k6
Write-Output ""
Write-Output "════ 配合校核（fits_iso286.yaml，24~30 段）════"
$holeES = 21.0; $holeEI = 0.0     # H7
$axEs = 15.0;  $axEi = 2.0       # k6
$Xmax = $holeES - $axEi
$Xmin = $holeEI - $axEs
Write-Output "  H7 孔 (24~30): ES=+$holeES EI=$holeEI"
Write-Output "  k6 轴 (24~30): es=+$axEs ei=+$axEi"
Write-Output "  ⇒ Xmax = ES孔 − ei轴 = $Xmax μm（最大间隙）"
Write-Output "  ⇒ Xmin = EI孔 − es轴 = $Xmin μm（最大过盈）"
Write-Output "  ⇒ 过渡配合，过盈约 $([math]::Abs($Xmin)) μm = $([math]::Abs($Xmin)/1000) mm"
Write-Output "  ⇒ $(if($Xmin -lt 0){'✅ 轻中载旋转内圈：有过盈但小，便于装拆'}else{'⚠ 无过盈，是间隙配合'})"
.bore, $_.B, ($_.C*1000), $_.nLim, $_.da, $_.ra)
    }
    $best = $pick | Select-Object -First 1
    Write-Output ""
    Write-Output "════ 校核 ════"
    Write-Output "  选用 $($best.Desig)：C=$($best.C)kN / 需 $C_need N ⇒ 实际富余 $([math]::Round($best.C*1000-$C_need,0))N"
    $lifeChk = [math]::Round(($best.C*1000/$P_eq) * 3 * 1e6 / (60*$n) / 1e6, 2)
    Write-Output "  反算寿命 L10h = (C/P)³·10⁶/(60n) = $lifeChk 万小时（要求 $Lh h）"
    Write-Output "  转速校核：n_lim=$($best.nLim) ≥ $n ⇒ $(if($best.nLim -ge $n){'✅'}else{'❌'})"
}

# 5) 配合：按知识库 fits_iso286，φ30 的 H7/k6
Write-Output ""
Write-Output "════ 配合校核（fits_iso286.yaml，24~30 段）════"
$holeES = 21.0; $holeEI = 0.0     # H7
$axEs = 15.0;  $axEi = 2.0       # k6
$Xmax = $holeES - $axEi
$Xmin = $holeEI - $axEs
Write-Output "  H7 孔 (24~30): ES=+$holeES EI=$holeEI"
Write-Output "  k6 轴 (24~30): es=+$axEs ei=+$axEi"
Write-Output "  ⇒ Xmax = ES孔 − ei轴 = $Xmax μm（最大间隙）"
Write-Output "  ⇒ Xmin = EI孔 − es轴 = $Xmin μm（最大过盈）"
Write-Output "  ⇒ 过渡配合，过盈约 $([math]::Abs($Xmin)) μm = $([math]::Abs($Xmin)/1000) mm"
Write-Output "  ⇒ $(if($Xmin -lt 0){'✅ 轻中载旋转内圈：有过盈但小，便于装拆'}else{'⚠ 无过盈，是间隙配合'})"
.shell) C=$($_.C)kN  差 $([math]::Round($_.C*1000-$C_need,0))N" }
} else {
    Write-Output "  满足条件的型号 $($pick.Count) 个（按内径排序，前 6 个）:"
    $pick | Select-Object -First 6 | ForEach-Object {
        Write-Output ("     {0,-10} d={1,4} D={2,4} B={3,4}  C={4,6}N  n_lim={5,7}  轴肩da={6,5}  ra={7}" -f `
            $_.Desig, # ★ 闭环验证：用轴承库 + 配合库 + 材料库 做一次真实选型
# 题目：设计一根传动轴，传递 P=2.2kW, n=1450 rpm，要求寿命 L10h=10000h
# 判据自检：算出的 C/C比 是否符合工程常识；选的型号是否真的在表里、n_lim 是否够

$csv = "C:\Users\Zegel\solidpilot-mcp\知识库\bearings\single_row_deep_groove_ball_bearing_parameters.csv"
$L = @(Get-Content $csv | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })

# 列位置（已验证）：1=d 2=D 3=B 4=C 5=C0 6=Pu 7=n_ref 8=n_lim 9=mass 10=Designation 15=da 17=ra
function Parse($line) {
    $r = $line.Split(',')
    [pscustomobject]@{
        bore = [double]$r[1]; shell = [double]$r[2]; wid = [double]$r[3]
        C  = [double]$r[4];  C0 = [double]$r[5];  Pu = [double]$r[6]
        nRef = [double]$r[7]; nLim = [double]$r[8]; mass = [double]$r[9]
        Desig = $r[10].Trim(); da = $r[15].Trim(); ra = $r[17].Trim()
    }
}

Write-Output "════ 工况 ════"
$P = 2.2; $n = 1450; $Lh = 10000
Write-Output "  功率 P = $P kW，转速 n = $n rpm，要求寿命 L10h = $Lh h"
# 1) 载荷系数（design_rules: 中等工况 K_A=1.3~1.5，轻载1.3）
$K_A = 1.3
Write-Output "  工况系数 K_A = $K_A（中等冲击）"

# 2) 当量动载荷 P = K_A × (轴承当量载荷)
#    ★ 简化：设径向为主，取载荷系数 X=1, Y=1.4（球轴承，Fr/Fr > e）
#    为演示取径向载荷 Fr = 0.5 × 轴向载荷极限，按轴径初估
$Fr = 1200   # N，按轴径 φ30 估算的径向载荷
$Fa = 300    # N，轴向力
$X = 1.0; $Y = 1.4
$P_eq = [math]::Round($K_A * ($X*$Fr + $Y*$Fa), 1)
Write-Output "  径向载荷 Fr = $Fr N，轴向 Fa = $Fa N"
Write-Output "  当量动载荷 P = K_A·(X·Fr + Y·Fa) = $K_A·($X·$Fr + $Y·$Fa) = $P_eq N"

# 3) 由寿命反算所需动载荷（球轴承 ε=3）
$millions = $Lh * 60 * $n / 1e6
$eps = 3
$C_need = [math]::Round($P_eq * [math]::Pow($millions, 1/$eps), 1)
Write-Output "  寿命转数 = $Lh h × 60 × $n rpm = $([math]::Round($millions*1e6/1e6,1))×10^6 转"
Write-Output "  球轴承 ε=3 ⇒ C_需 = P × (寿命/10^6)^(1/3) = $P_eq × $([math]::Round($millions,2))^(1/3) = $C_need N = $([math]::Round($C_need/1000,2)) kN"

# 4) 查表选型
Write-Output ""
Write-Output "════ 查表选型（C ≥ $C_need N 且 n_lim ≥ $n）════"
$pick = @()
for ($i = 1; $i -lt $L.Count; $i++) {
    try { $b = Parse $L[$i] } catch { continue }
    if ($b.C -ge $C_need -and $b.nLim -ge $n) { $pick += $b }
}
$pick = $pick | Sort-Object d
if ($pick.Count -eq 0) {
    Write-Output "  ⚠ 表中无满足的型号（表内主要是小规格 M3~M5，功率偏大）"
    # 退而求其次：列出承载最接近的
    $all = @(); for ($i=1;$i -lt $L.Count;$i++){ try { $all += Parse $L[$i] } catch {} }
    $all | Sort-Object { [math]::Abs($_.C - $C_need) } | Select-Object -First 3 |
      ForEach-Object { Write-Output "     最近: $($_.Desig)  d=$(# ★ 闭环验证：用轴承库 + 配合库 + 材料库 做一次真实选型
# 题目：设计一根传动轴，传递 P=2.2kW, n=1450 rpm，要求寿命 L10h=10000h
# 判据自检：算出的 C/C比 是否符合工程常识；选的型号是否真的在表里、n_lim 是否够

$csv = "C:\Users\Zegel\solidpilot-mcp\知识库\bearings\single_row_deep_groove_ball_bearing_parameters.csv"
$L = @(Get-Content $csv | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })

# 列位置（已验证）：1=d 2=D 3=B 4=C 5=C0 6=Pu 7=n_ref 8=n_lim 9=mass 10=Designation 15=da 17=ra
function Parse($line) {
    $r = $line.Split(',')
    [pscustomobject]@{
        bore = [double]$r[1]; shell = [double]$r[2]; wid = [double]$r[3]
        C  = [double]$r[4];  C0 = [double]$r[5];  Pu = [double]$r[6]
        nRef = [double]$r[7]; nLim = [double]$r[8]; mass = [double]$r[9]
        Desig = $r[10].Trim(); da = $r[15].Trim(); ra = $r[17].Trim()
    }
}

Write-Output "════ 工况 ════"
$P = 2.2; $n = 1450; $Lh = 10000
Write-Output "  功率 P = $P kW，转速 n = $n rpm，要求寿命 L10h = $Lh h"
# 1) 载荷系数（design_rules: 中等工况 K_A=1.3~1.5，轻载1.3）
$K_A = 1.3
Write-Output "  工况系数 K_A = $K_A（中等冲击）"

# 2) 当量动载荷 P = K_A × (轴承当量载荷)
#    ★ 简化：设径向为主，取载荷系数 X=1, Y=1.4（球轴承，Fr/Fr > e）
#    为演示取径向载荷 Fr = 0.5 × 轴向载荷极限，按轴径初估
$Fr = 1200   # N，按轴径 φ30 估算的径向载荷
$Fa = 300    # N，轴向力
$X = 1.0; $Y = 1.4
$P_eq = [math]::Round($K_A * ($X*$Fr + $Y*$Fa), 1)
Write-Output "  径向载荷 Fr = $Fr N，轴向 Fa = $Fa N"
Write-Output "  当量动载荷 P = K_A·(X·Fr + Y·Fa) = $K_A·($X·$Fr + $Y·$Fa) = $P_eq N"

# 3) 由寿命反算所需动载荷（球轴承 ε=3）
$millions = $Lh * 60 * $n / 1e6
$eps = 3
$C_need = [math]::Round($P_eq * [math]::Pow($millions, 1/$eps), 1)
Write-Output "  寿命转数 = $Lh h × 60 × $n rpm = $([math]::Round($millions*1e6/1e6,1))×10^6 转"
Write-Output "  球轴承 ε=3 ⇒ C_需 = P × (寿命/10^6)^(1/3) = $P_eq × $([math]::Round($millions,2))^(1/3) = $C_need N = $([math]::Round($C_need/1000,2)) kN"

# 4) 查表选型
Write-Output ""
Write-Output "════ 查表选型（C ≥ $C_need N 且 n_lim ≥ $n）════"
$pick = @()
for ($i = 1; $i -lt $L.Count; $i++) {
    try { $b = Parse $L[$i] } catch { continue }
    if ($b.C -ge $C_need -and $b.nLim -ge $n) { $pick += $b }
}
$pick = $pick | Sort-Object d
if ($pick.Count -eq 0) {
    Write-Output "  ⚠ 表中无满足的型号（表内主要是小规格 M3~M5，功率偏大）"
    # 退而求其次：列出承载最接近的
    $all = @(); for ($i=1;$i -lt $L.Count;$i++){ try { $all += Parse $L[$i] } catch {} }
    $all | Sort-Object { [math]::Abs($_.C - $C_need) } | Select-Object -First 3 |
      ForEach-Object { Write-Output "     最近: $($_.Desig)  d=$($_.d) C=$($_.C)kN  差 $([math]::Round($_.C*1000-$C_need,0))N" }
} else {
    Write-Output "  满足条件的型号 $($pick.Count) 个（按内径排序，前 6 个）:"
    $pick | Select-Object -First 6 | ForEach-Object {
        Write-Output ("     {0,-10} d={1,4} D={2,4} B={3,4}  C={4,6}N  n_lim={5,7}  轴肩da={6,5}  ra={7}" -f `
            $_.Desig, $_.d, $_.D, $_.B, ($_.C*1000), $_.nLim, $_.da, $_.ra)
    }
    $best = $pick | Select-Object -First 1
    Write-Output ""
    Write-Output "════ 校核 ════"
    Write-Output "  选用 $($best.Desig)：C=$($best.C)kN / 需 $C_need N ⇒ 实际富余 $([math]::Round($best.C*1000-$C_need,0))N"
    $lifeChk = [math]::Round(($best.C*1000/$P_eq) * 3 * 1e6 / (60*$n) / 1e6, 2)
    Write-Output "  反算寿命 L10h = (C/P)³·10⁶/(60n) = $lifeChk 万小时（要求 $Lh h）"
    Write-Output "  转速校核：n_lim=$($best.nLim) ≥ $n ⇒ $(if($best.nLim -ge $n){'✅'}else{'❌'})"
}

# 5) 配合：按知识库 fits_iso286，φ30 的 H7/k6
Write-Output ""
Write-Output "════ 配合校核（fits_iso286.yaml，24~30 段）════"
$holeES = 21.0; $holeEI = 0.0     # H7
$axEs = 15.0;  $axEi = 2.0       # k6
$Xmax = $holeES - $axEi
$Xmin = $holeEI - $axEs
Write-Output "  H7 孔 (24~30): ES=+$holeES EI=$holeEI"
Write-Output "  k6 轴 (24~30): es=+$axEs ei=+$axEi"
Write-Output "  ⇒ Xmax = ES孔 − ei轴 = $Xmax μm（最大间隙）"
Write-Output "  ⇒ Xmin = EI孔 − es轴 = $Xmin μm（最大过盈）"
Write-Output "  ⇒ 过渡配合，过盈约 $([math]::Abs($Xmin)) μm = $([math]::Abs($Xmin)/1000) mm"
Write-Output "  ⇒ $(if($Xmin -lt 0){'✅ 轻中载旋转内圈：有过盈但小，便于装拆'}else{'⚠ 无过盈，是间隙配合'})"
.bore) C=$($_.C)kN  差 $([math]::Round($_.C*1000-$C_need,0))N" }
} else {
    Write-Output "  满足条件的型号 $($pick.Count) 个（按内径排序，前 6 个）:"
    $pick | Select-Object -First 6 | ForEach-Object {
        Write-Output ("     {0,-10} d={1,4} D={2,4} B={3,4}  C={4,6}N  n_lim={5,7}  轴肩da={6,5}  ra={7}" -f `
            $_.Desig, # ★ 闭环验证：用轴承库 + 配合库 + 材料库 做一次真实选型
# 题目：设计一根传动轴，传递 P=2.2kW, n=1450 rpm，要求寿命 L10h=10000h
# 判据自检：算出的 C/C比 是否符合工程常识；选的型号是否真的在表里、n_lim 是否够

$csv = "C:\Users\Zegel\solidpilot-mcp\知识库\bearings\single_row_deep_groove_ball_bearing_parameters.csv"
$L = @(Get-Content $csv | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })

# 列位置（已验证）：1=d 2=D 3=B 4=C 5=C0 6=Pu 7=n_ref 8=n_lim 9=mass 10=Designation 15=da 17=ra
function Parse($line) {
    $r = $line.Split(',')
    [pscustomobject]@{
        bore = [double]$r[1]; shell = [double]$r[2]; wid = [double]$r[3]
        C  = [double]$r[4];  C0 = [double]$r[5];  Pu = [double]$r[6]
        nRef = [double]$r[7]; nLim = [double]$r[8]; mass = [double]$r[9]
        Desig = $r[10].Trim(); da = $r[15].Trim(); ra = $r[17].Trim()
    }
}

Write-Output "════ 工况 ════"
$P = 2.2; $n = 1450; $Lh = 10000
Write-Output "  功率 P = $P kW，转速 n = $n rpm，要求寿命 L10h = $Lh h"
# 1) 载荷系数（design_rules: 中等工况 K_A=1.3~1.5，轻载1.3）
$K_A = 1.3
Write-Output "  工况系数 K_A = $K_A（中等冲击）"

# 2) 当量动载荷 P = K_A × (轴承当量载荷)
#    ★ 简化：设径向为主，取载荷系数 X=1, Y=1.4（球轴承，Fr/Fr > e）
#    为演示取径向载荷 Fr = 0.5 × 轴向载荷极限，按轴径初估
$Fr = 1200   # N，按轴径 φ30 估算的径向载荷
$Fa = 300    # N，轴向力
$X = 1.0; $Y = 1.4
$P_eq = [math]::Round($K_A * ($X*$Fr + $Y*$Fa), 1)
Write-Output "  径向载荷 Fr = $Fr N，轴向 Fa = $Fa N"
Write-Output "  当量动载荷 P = K_A·(X·Fr + Y·Fa) = $K_A·($X·$Fr + $Y·$Fa) = $P_eq N"

# 3) 由寿命反算所需动载荷（球轴承 ε=3）
$millions = $Lh * 60 * $n / 1e6
$eps = 3
$C_need = [math]::Round($P_eq * [math]::Pow($millions, 1/$eps), 1)
Write-Output "  寿命转数 = $Lh h × 60 × $n rpm = $([math]::Round($millions*1e6/1e6,1))×10^6 转"
Write-Output "  球轴承 ε=3 ⇒ C_需 = P × (寿命/10^6)^(1/3) = $P_eq × $([math]::Round($millions,2))^(1/3) = $C_need N = $([math]::Round($C_need/1000,2)) kN"

# 4) 查表选型
Write-Output ""
Write-Output "════ 查表选型（C ≥ $C_need N 且 n_lim ≥ $n）════"
$pick = @()
for ($i = 1; $i -lt $L.Count; $i++) {
    try { $b = Parse $L[$i] } catch { continue }
    if ($b.C -ge $C_need -and $b.nLim -ge $n) { $pick += $b }
}
$pick = $pick | Sort-Object d
if ($pick.Count -eq 0) {
    Write-Output "  ⚠ 表中无满足的型号（表内主要是小规格 M3~M5，功率偏大）"
    # 退而求其次：列出承载最接近的
    $all = @(); for ($i=1;$i -lt $L.Count;$i++){ try { $all += Parse $L[$i] } catch {} }
    $all | Sort-Object { [math]::Abs($_.C - $C_need) } | Select-Object -First 3 |
      ForEach-Object { Write-Output "     最近: $($_.Desig)  d=$($_.d) C=$($_.C)kN  差 $([math]::Round($_.C*1000-$C_need,0))N" }
} else {
    Write-Output "  满足条件的型号 $($pick.Count) 个（按内径排序，前 6 个）:"
    $pick | Select-Object -First 6 | ForEach-Object {
        Write-Output ("     {0,-10} d={1,4} D={2,4} B={3,4}  C={4,6}N  n_lim={5,7}  轴肩da={6,5}  ra={7}" -f `
            $_.Desig, $_.d, $_.D, $_.B, ($_.C*1000), $_.nLim, $_.da, $_.ra)
    }
    $best = $pick | Select-Object -First 1
    Write-Output ""
    Write-Output "════ 校核 ════"
    Write-Output "  选用 $($best.Desig)：C=$($best.C)kN / 需 $C_need N ⇒ 实际富余 $([math]::Round($best.C*1000-$C_need,0))N"
    $lifeChk = [math]::Round(($best.C*1000/$P_eq) * 3 * 1e6 / (60*$n) / 1e6, 2)
    Write-Output "  反算寿命 L10h = (C/P)³·10⁶/(60n) = $lifeChk 万小时（要求 $Lh h）"
    Write-Output "  转速校核：n_lim=$($best.nLim) ≥ $n ⇒ $(if($best.nLim -ge $n){'✅'}else{'❌'})"
}

# 5) 配合：按知识库 fits_iso286，φ30 的 H7/k6
Write-Output ""
Write-Output "════ 配合校核（fits_iso286.yaml，24~30 段）════"
$holeES = 21.0; $holeEI = 0.0     # H7
$axEs = 15.0;  $axEi = 2.0       # k6
$Xmax = $holeES - $axEi
$Xmin = $holeEI - $axEs
Write-Output "  H7 孔 (24~30): ES=+$holeES EI=$holeEI"
Write-Output "  k6 轴 (24~30): es=+$axEs ei=+$axEi"
Write-Output "  ⇒ Xmax = ES孔 − ei轴 = $Xmax μm（最大间隙）"
Write-Output "  ⇒ Xmin = EI孔 − es轴 = $Xmin μm（最大过盈）"
Write-Output "  ⇒ 过渡配合，过盈约 $([math]::Abs($Xmin)) μm = $([math]::Abs($Xmin)/1000) mm"
Write-Output "  ⇒ $(if($Xmin -lt 0){'✅ 轻中载旋转内圈：有过盈但小，便于装拆'}else{'⚠ 无过盈，是间隙配合'})"
.bore, # ★ 闭环验证：用轴承库 + 配合库 + 材料库 做一次真实选型
# 题目：设计一根传动轴，传递 P=2.2kW, n=1450 rpm，要求寿命 L10h=10000h
# 判据自检：算出的 C/C比 是否符合工程常识；选的型号是否真的在表里、n_lim 是否够

$csv = "C:\Users\Zegel\solidpilot-mcp\知识库\bearings\single_row_deep_groove_ball_bearing_parameters.csv"
$L = @(Get-Content $csv | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })

# 列位置（已验证）：1=d 2=D 3=B 4=C 5=C0 6=Pu 7=n_ref 8=n_lim 9=mass 10=Designation 15=da 17=ra
function Parse($line) {
    $r = $line.Split(',')
    [pscustomobject]@{
        bore = [double]$r[1]; shell = [double]$r[2]; wid = [double]$r[3]
        C  = [double]$r[4];  C0 = [double]$r[5];  Pu = [double]$r[6]
        nRef = [double]$r[7]; nLim = [double]$r[8]; mass = [double]$r[9]
        Desig = $r[10].Trim(); da = $r[15].Trim(); ra = $r[17].Trim()
    }
}

Write-Output "════ 工况 ════"
$P = 2.2; $n = 1450; $Lh = 10000
Write-Output "  功率 P = $P kW，转速 n = $n rpm，要求寿命 L10h = $Lh h"
# 1) 载荷系数（design_rules: 中等工况 K_A=1.3~1.5，轻载1.3）
$K_A = 1.3
Write-Output "  工况系数 K_A = $K_A（中等冲击）"

# 2) 当量动载荷 P = K_A × (轴承当量载荷)
#    ★ 简化：设径向为主，取载荷系数 X=1, Y=1.4（球轴承，Fr/Fr > e）
#    为演示取径向载荷 Fr = 0.5 × 轴向载荷极限，按轴径初估
$Fr = 1200   # N，按轴径 φ30 估算的径向载荷
$Fa = 300    # N，轴向力
$X = 1.0; $Y = 1.4
$P_eq = [math]::Round($K_A * ($X*$Fr + $Y*$Fa), 1)
Write-Output "  径向载荷 Fr = $Fr N，轴向 Fa = $Fa N"
Write-Output "  当量动载荷 P = K_A·(X·Fr + Y·Fa) = $K_A·($X·$Fr + $Y·$Fa) = $P_eq N"

# 3) 由寿命反算所需动载荷（球轴承 ε=3）
$millions = $Lh * 60 * $n / 1e6
$eps = 3
$C_need = [math]::Round($P_eq * [math]::Pow($millions, 1/$eps), 1)
Write-Output "  寿命转数 = $Lh h × 60 × $n rpm = $([math]::Round($millions*1e6/1e6,1))×10^6 转"
Write-Output "  球轴承 ε=3 ⇒ C_需 = P × (寿命/10^6)^(1/3) = $P_eq × $([math]::Round($millions,2))^(1/3) = $C_need N = $([math]::Round($C_need/1000,2)) kN"

# 4) 查表选型
Write-Output ""
Write-Output "════ 查表选型（C ≥ $C_need N 且 n_lim ≥ $n）════"
$pick = @()
for ($i = 1; $i -lt $L.Count; $i++) {
    try { $b = Parse $L[$i] } catch { continue }
    if ($b.C -ge $C_need -and $b.nLim -ge $n) { $pick += $b }
}
$pick = $pick | Sort-Object d
if ($pick.Count -eq 0) {
    Write-Output "  ⚠ 表中无满足的型号（表内主要是小规格 M3~M5，功率偏大）"
    # 退而求其次：列出承载最接近的
    $all = @(); for ($i=1;$i -lt $L.Count;$i++){ try { $all += Parse $L[$i] } catch {} }
    $all | Sort-Object { [math]::Abs($_.C - $C_need) } | Select-Object -First 3 |
      ForEach-Object { Write-Output "     最近: $($_.Desig)  d=$($_.d) C=$($_.C)kN  差 $([math]::Round($_.C*1000-$C_need,0))N" }
} else {
    Write-Output "  满足条件的型号 $($pick.Count) 个（按内径排序，前 6 个）:"
    $pick | Select-Object -First 6 | ForEach-Object {
        Write-Output ("     {0,-10} d={1,4} D={2,4} B={3,4}  C={4,6}N  n_lim={5,7}  轴肩da={6,5}  ra={7}" -f `
            $_.Desig, $_.d, $_.D, $_.B, ($_.C*1000), $_.nLim, $_.da, $_.ra)
    }
    $best = $pick | Select-Object -First 1
    Write-Output ""
    Write-Output "════ 校核 ════"
    Write-Output "  选用 $($best.Desig)：C=$($best.C)kN / 需 $C_need N ⇒ 实际富余 $([math]::Round($best.C*1000-$C_need,0))N"
    $lifeChk = [math]::Round(($best.C*1000/$P_eq) * 3 * 1e6 / (60*$n) / 1e6, 2)
    Write-Output "  反算寿命 L10h = (C/P)³·10⁶/(60n) = $lifeChk 万小时（要求 $Lh h）"
    Write-Output "  转速校核：n_lim=$($best.nLim) ≥ $n ⇒ $(if($best.nLim -ge $n){'✅'}else{'❌'})"
}

# 5) 配合：按知识库 fits_iso286，φ30 的 H7/k6
Write-Output ""
Write-Output "════ 配合校核（fits_iso286.yaml，24~30 段）════"
$holeES = 21.0; $holeEI = 0.0     # H7
$axEs = 15.0;  $axEi = 2.0       # k6
$Xmax = $holeES - $axEi
$Xmin = $holeEI - $axEs
Write-Output "  H7 孔 (24~30): ES=+$holeES EI=$holeEI"
Write-Output "  k6 轴 (24~30): es=+$axEs ei=+$axEi"
Write-Output "  ⇒ Xmax = ES孔 − ei轴 = $Xmax μm（最大间隙）"
Write-Output "  ⇒ Xmin = EI孔 − es轴 = $Xmin μm（最大过盈）"
Write-Output "  ⇒ 过渡配合，过盈约 $([math]::Abs($Xmin)) μm = $([math]::Abs($Xmin)/1000) mm"
Write-Output "  ⇒ $(if($Xmin -lt 0){'✅ 轻中载旋转内圈：有过盈但小，便于装拆'}else{'⚠ 无过盈，是间隙配合'})"
.bore, $_.B, ($_.C*1000), $_.nLim, $_.da, $_.ra)
    }
    $best = $pick | Select-Object -First 1
    Write-Output ""
    Write-Output "════ 校核 ════"
    Write-Output "  选用 $($best.Desig)：C=$($best.C)kN / 需 $C_need N ⇒ 实际富余 $([math]::Round($best.C*1000-$C_need,0))N"
    $lifeChk = [math]::Round(($best.C*1000/$P_eq) * 3 * 1e6 / (60*$n) / 1e6, 2)
    Write-Output "  反算寿命 L10h = (C/P)³·10⁶/(60n) = $lifeChk 万小时（要求 $Lh h）"
    Write-Output "  转速校核：n_lim=$($best.nLim) ≥ $n ⇒ $(if($best.nLim -ge $n){'✅'}else{'❌'})"
}

# 5) 配合：按知识库 fits_iso286，φ30 的 H7/k6
Write-Output ""
Write-Output "════ 配合校核（fits_iso286.yaml，24~30 段）════"
$holeES = 21.0; $holeEI = 0.0     # H7
$axEs = 15.0;  $axEi = 2.0       # k6
$Xmax = $holeES - $axEi
$Xmin = $holeEI - $axEs
Write-Output "  H7 孔 (24~30): ES=+$holeES EI=$holeEI"
Write-Output "  k6 轴 (24~30): es=+$axEs ei=+$axEi"
Write-Output "  ⇒ Xmax = ES孔 − ei轴 = $Xmax μm（最大间隙）"
Write-Output "  ⇒ Xmin = EI孔 − es轴 = $Xmin μm（最大过盈）"
Write-Output "  ⇒ 过渡配合，过盈约 $([math]::Abs($Xmin)) μm = $([math]::Abs($Xmin)/1000) mm"
Write-Output "  ⇒ $(if($Xmin -lt 0){'✅ 轻中载旋转内圈：有过盈但小，便于装拆'}else{'⚠ 无过盈，是间隙配合'})"
.shell, # ★ 闭环验证：用轴承库 + 配合库 + 材料库 做一次真实选型
# 题目：设计一根传动轴，传递 P=2.2kW, n=1450 rpm，要求寿命 L10h=10000h
# 判据自检：算出的 C/C比 是否符合工程常识；选的型号是否真的在表里、n_lim 是否够

$csv = "C:\Users\Zegel\solidpilot-mcp\知识库\bearings\single_row_deep_groove_ball_bearing_parameters.csv"
$L = @(Get-Content $csv | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })

# 列位置（已验证）：1=d 2=D 3=B 4=C 5=C0 6=Pu 7=n_ref 8=n_lim 9=mass 10=Designation 15=da 17=ra
function Parse($line) {
    $r = $line.Split(',')
    [pscustomobject]@{
        bore = [double]$r[1]; shell = [double]$r[2]; wid = [double]$r[3]
        C  = [double]$r[4];  C0 = [double]$r[5];  Pu = [double]$r[6]
        nRef = [double]$r[7]; nLim = [double]$r[8]; mass = [double]$r[9]
        Desig = $r[10].Trim(); da = $r[15].Trim(); ra = $r[17].Trim()
    }
}

Write-Output "════ 工况 ════"
$P = 2.2; $n = 1450; $Lh = 10000
Write-Output "  功率 P = $P kW，转速 n = $n rpm，要求寿命 L10h = $Lh h"
# 1) 载荷系数（design_rules: 中等工况 K_A=1.3~1.5，轻载1.3）
$K_A = 1.3
Write-Output "  工况系数 K_A = $K_A（中等冲击）"

# 2) 当量动载荷 P = K_A × (轴承当量载荷)
#    ★ 简化：设径向为主，取载荷系数 X=1, Y=1.4（球轴承，Fr/Fr > e）
#    为演示取径向载荷 Fr = 0.5 × 轴向载荷极限，按轴径初估
$Fr = 1200   # N，按轴径 φ30 估算的径向载荷
$Fa = 300    # N，轴向力
$X = 1.0; $Y = 1.4
$P_eq = [math]::Round($K_A * ($X*$Fr + $Y*$Fa), 1)
Write-Output "  径向载荷 Fr = $Fr N，轴向 Fa = $Fa N"
Write-Output "  当量动载荷 P = K_A·(X·Fr + Y·Fa) = $K_A·($X·$Fr + $Y·$Fa) = $P_eq N"

# 3) 由寿命反算所需动载荷（球轴承 ε=3）
$millions = $Lh * 60 * $n / 1e6
$eps = 3
$C_need = [math]::Round($P_eq * [math]::Pow($millions, 1/$eps), 1)
Write-Output "  寿命转数 = $Lh h × 60 × $n rpm = $([math]::Round($millions*1e6/1e6,1))×10^6 转"
Write-Output "  球轴承 ε=3 ⇒ C_需 = P × (寿命/10^6)^(1/3) = $P_eq × $([math]::Round($millions,2))^(1/3) = $C_need N = $([math]::Round($C_need/1000,2)) kN"

# 4) 查表选型
Write-Output ""
Write-Output "════ 查表选型（C ≥ $C_need N 且 n_lim ≥ $n）════"
$pick = @()
for ($i = 1; $i -lt $L.Count; $i++) {
    try { $b = Parse $L[$i] } catch { continue }
    if ($b.C -ge $C_need -and $b.nLim -ge $n) { $pick += $b }
}
$pick = $pick | Sort-Object d
if ($pick.Count -eq 0) {
    Write-Output "  ⚠ 表中无满足的型号（表内主要是小规格 M3~M5，功率偏大）"
    # 退而求其次：列出承载最接近的
    $all = @(); for ($i=1;$i -lt $L.Count;$i++){ try { $all += Parse $L[$i] } catch {} }
    $all | Sort-Object { [math]::Abs($_.C - $C_need) } | Select-Object -First 3 |
      ForEach-Object { Write-Output "     最近: $($_.Desig)  d=$(# ★ 闭环验证：用轴承库 + 配合库 + 材料库 做一次真实选型
# 题目：设计一根传动轴，传递 P=2.2kW, n=1450 rpm，要求寿命 L10h=10000h
# 判据自检：算出的 C/C比 是否符合工程常识；选的型号是否真的在表里、n_lim 是否够

$csv = "C:\Users\Zegel\solidpilot-mcp\知识库\bearings\single_row_deep_groove_ball_bearing_parameters.csv"
$L = @(Get-Content $csv | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })

# 列位置（已验证）：1=d 2=D 3=B 4=C 5=C0 6=Pu 7=n_ref 8=n_lim 9=mass 10=Designation 15=da 17=ra
function Parse($line) {
    $r = $line.Split(',')
    [pscustomobject]@{
        bore = [double]$r[1]; shell = [double]$r[2]; wid = [double]$r[3]
        C  = [double]$r[4];  C0 = [double]$r[5];  Pu = [double]$r[6]
        nRef = [double]$r[7]; nLim = [double]$r[8]; mass = [double]$r[9]
        Desig = $r[10].Trim(); da = $r[15].Trim(); ra = $r[17].Trim()
    }
}

Write-Output "════ 工况 ════"
$P = 2.2; $n = 1450; $Lh = 10000
Write-Output "  功率 P = $P kW，转速 n = $n rpm，要求寿命 L10h = $Lh h"
# 1) 载荷系数（design_rules: 中等工况 K_A=1.3~1.5，轻载1.3）
$K_A = 1.3
Write-Output "  工况系数 K_A = $K_A（中等冲击）"

# 2) 当量动载荷 P = K_A × (轴承当量载荷)
#    ★ 简化：设径向为主，取载荷系数 X=1, Y=1.4（球轴承，Fr/Fr > e）
#    为演示取径向载荷 Fr = 0.5 × 轴向载荷极限，按轴径初估
$Fr = 1200   # N，按轴径 φ30 估算的径向载荷
$Fa = 300    # N，轴向力
$X = 1.0; $Y = 1.4
$P_eq = [math]::Round($K_A * ($X*$Fr + $Y*$Fa), 1)
Write-Output "  径向载荷 Fr = $Fr N，轴向 Fa = $Fa N"
Write-Output "  当量动载荷 P = K_A·(X·Fr + Y·Fa) = $K_A·($X·$Fr + $Y·$Fa) = $P_eq N"

# 3) 由寿命反算所需动载荷（球轴承 ε=3）
$millions = $Lh * 60 * $n / 1e6
$eps = 3
$C_need = [math]::Round($P_eq * [math]::Pow($millions, 1/$eps), 1)
Write-Output "  寿命转数 = $Lh h × 60 × $n rpm = $([math]::Round($millions*1e6/1e6,1))×10^6 转"
Write-Output "  球轴承 ε=3 ⇒ C_需 = P × (寿命/10^6)^(1/3) = $P_eq × $([math]::Round($millions,2))^(1/3) = $C_need N = $([math]::Round($C_need/1000,2)) kN"

# 4) 查表选型
Write-Output ""
Write-Output "════ 查表选型（C ≥ $C_need N 且 n_lim ≥ $n）════"
$pick = @()
for ($i = 1; $i -lt $L.Count; $i++) {
    try { $b = Parse $L[$i] } catch { continue }
    if ($b.C -ge $C_need -and $b.nLim -ge $n) { $pick += $b }
}
$pick = $pick | Sort-Object d
if ($pick.Count -eq 0) {
    Write-Output "  ⚠ 表中无满足的型号（表内主要是小规格 M3~M5，功率偏大）"
    # 退而求其次：列出承载最接近的
    $all = @(); for ($i=1;$i -lt $L.Count;$i++){ try { $all += Parse $L[$i] } catch {} }
    $all | Sort-Object { [math]::Abs($_.C - $C_need) } | Select-Object -First 3 |
      ForEach-Object { Write-Output "     最近: $($_.Desig)  d=$($_.d) C=$($_.C)kN  差 $([math]::Round($_.C*1000-$C_need,0))N" }
} else {
    Write-Output "  满足条件的型号 $($pick.Count) 个（按内径排序，前 6 个）:"
    $pick | Select-Object -First 6 | ForEach-Object {
        Write-Output ("     {0,-10} d={1,4} D={2,4} B={3,4}  C={4,6}N  n_lim={5,7}  轴肩da={6,5}  ra={7}" -f `
            $_.Desig, $_.d, $_.D, $_.B, ($_.C*1000), $_.nLim, $_.da, $_.ra)
    }
    $best = $pick | Select-Object -First 1
    Write-Output ""
    Write-Output "════ 校核 ════"
    Write-Output "  选用 $($best.Desig)：C=$($best.C)kN / 需 $C_need N ⇒ 实际富余 $([math]::Round($best.C*1000-$C_need,0))N"
    $lifeChk = [math]::Round(($best.C*1000/$P_eq) * 3 * 1e6 / (60*$n) / 1e6, 2)
    Write-Output "  反算寿命 L10h = (C/P)³·10⁶/(60n) = $lifeChk 万小时（要求 $Lh h）"
    Write-Output "  转速校核：n_lim=$($best.nLim) ≥ $n ⇒ $(if($best.nLim -ge $n){'✅'}else{'❌'})"
}

# 5) 配合：按知识库 fits_iso286，φ30 的 H7/k6
Write-Output ""
Write-Output "════ 配合校核（fits_iso286.yaml，24~30 段）════"
$holeES = 21.0; $holeEI = 0.0     # H7
$axEs = 15.0;  $axEi = 2.0       # k6
$Xmax = $holeES - $axEi
$Xmin = $holeEI - $axEs
Write-Output "  H7 孔 (24~30): ES=+$holeES EI=$holeEI"
Write-Output "  k6 轴 (24~30): es=+$axEs ei=+$axEi"
Write-Output "  ⇒ Xmax = ES孔 − ei轴 = $Xmax μm（最大间隙）"
Write-Output "  ⇒ Xmin = EI孔 − es轴 = $Xmin μm（最大过盈）"
Write-Output "  ⇒ 过渡配合，过盈约 $([math]::Abs($Xmin)) μm = $([math]::Abs($Xmin)/1000) mm"
Write-Output "  ⇒ $(if($Xmin -lt 0){'✅ 轻中载旋转内圈：有过盈但小，便于装拆'}else{'⚠ 无过盈，是间隙配合'})"
.bore) C=$($_.C)kN  差 $([math]::Round($_.C*1000-$C_need,0))N" }
} else {
    Write-Output "  满足条件的型号 $($pick.Count) 个（按内径排序，前 6 个）:"
    $pick | Select-Object -First 6 | ForEach-Object {
        Write-Output ("     {0,-10} d={1,4} D={2,4} B={3,4}  C={4,6}N  n_lim={5,7}  轴肩da={6,5}  ra={7}" -f `
            $_.Desig, # ★ 闭环验证：用轴承库 + 配合库 + 材料库 做一次真实选型
# 题目：设计一根传动轴，传递 P=2.2kW, n=1450 rpm，要求寿命 L10h=10000h
# 判据自检：算出的 C/C比 是否符合工程常识；选的型号是否真的在表里、n_lim 是否够

$csv = "C:\Users\Zegel\solidpilot-mcp\知识库\bearings\single_row_deep_groove_ball_bearing_parameters.csv"
$L = @(Get-Content $csv | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })

# 列位置（已验证）：1=d 2=D 3=B 4=C 5=C0 6=Pu 7=n_ref 8=n_lim 9=mass 10=Designation 15=da 17=ra
function Parse($line) {
    $r = $line.Split(',')
    [pscustomobject]@{
        bore = [double]$r[1]; shell = [double]$r[2]; wid = [double]$r[3]
        C  = [double]$r[4];  C0 = [double]$r[5];  Pu = [double]$r[6]
        nRef = [double]$r[7]; nLim = [double]$r[8]; mass = [double]$r[9]
        Desig = $r[10].Trim(); da = $r[15].Trim(); ra = $r[17].Trim()
    }
}

Write-Output "════ 工况 ════"
$P = 2.2; $n = 1450; $Lh = 10000
Write-Output "  功率 P = $P kW，转速 n = $n rpm，要求寿命 L10h = $Lh h"
# 1) 载荷系数（design_rules: 中等工况 K_A=1.3~1.5，轻载1.3）
$K_A = 1.3
Write-Output "  工况系数 K_A = $K_A（中等冲击）"

# 2) 当量动载荷 P = K_A × (轴承当量载荷)
#    ★ 简化：设径向为主，取载荷系数 X=1, Y=1.4（球轴承，Fr/Fr > e）
#    为演示取径向载荷 Fr = 0.5 × 轴向载荷极限，按轴径初估
$Fr = 1200   # N，按轴径 φ30 估算的径向载荷
$Fa = 300    # N，轴向力
$X = 1.0; $Y = 1.4
$P_eq = [math]::Round($K_A * ($X*$Fr + $Y*$Fa), 1)
Write-Output "  径向载荷 Fr = $Fr N，轴向 Fa = $Fa N"
Write-Output "  当量动载荷 P = K_A·(X·Fr + Y·Fa) = $K_A·($X·$Fr + $Y·$Fa) = $P_eq N"

# 3) 由寿命反算所需动载荷（球轴承 ε=3）
$millions = $Lh * 60 * $n / 1e6
$eps = 3
$C_need = [math]::Round($P_eq * [math]::Pow($millions, 1/$eps), 1)
Write-Output "  寿命转数 = $Lh h × 60 × $n rpm = $([math]::Round($millions*1e6/1e6,1))×10^6 转"
Write-Output "  球轴承 ε=3 ⇒ C_需 = P × (寿命/10^6)^(1/3) = $P_eq × $([math]::Round($millions,2))^(1/3) = $C_need N = $([math]::Round($C_need/1000,2)) kN"

# 4) 查表选型
Write-Output ""
Write-Output "════ 查表选型（C ≥ $C_need N 且 n_lim ≥ $n）════"
$pick = @()
for ($i = 1; $i -lt $L.Count; $i++) {
    try { $b = Parse $L[$i] } catch { continue }
    if ($b.C -ge $C_need -and $b.nLim -ge $n) { $pick += $b }
}
$pick = $pick | Sort-Object d
if ($pick.Count -eq 0) {
    Write-Output "  ⚠ 表中无满足的型号（表内主要是小规格 M3~M5，功率偏大）"
    # 退而求其次：列出承载最接近的
    $all = @(); for ($i=1;$i -lt $L.Count;$i++){ try { $all += Parse $L[$i] } catch {} }
    $all | Sort-Object { [math]::Abs($_.C - $C_need) } | Select-Object -First 3 |
      ForEach-Object { Write-Output "     最近: $($_.Desig)  d=$($_.d) C=$($_.C)kN  差 $([math]::Round($_.C*1000-$C_need,0))N" }
} else {
    Write-Output "  满足条件的型号 $($pick.Count) 个（按内径排序，前 6 个）:"
    $pick | Select-Object -First 6 | ForEach-Object {
        Write-Output ("     {0,-10} d={1,4} D={2,4} B={3,4}  C={4,6}N  n_lim={5,7}  轴肩da={6,5}  ra={7}" -f `
            $_.Desig, $_.d, $_.D, $_.B, ($_.C*1000), $_.nLim, $_.da, $_.ra)
    }
    $best = $pick | Select-Object -First 1
    Write-Output ""
    Write-Output "════ 校核 ════"
    Write-Output "  选用 $($best.Desig)：C=$($best.C)kN / 需 $C_need N ⇒ 实际富余 $([math]::Round($best.C*1000-$C_need,0))N"
    $lifeChk = [math]::Round(($best.C*1000/$P_eq) * 3 * 1e6 / (60*$n) / 1e6, 2)
    Write-Output "  反算寿命 L10h = (C/P)³·10⁶/(60n) = $lifeChk 万小时（要求 $Lh h）"
    Write-Output "  转速校核：n_lim=$($best.nLim) ≥ $n ⇒ $(if($best.nLim -ge $n){'✅'}else{'❌'})"
}

# 5) 配合：按知识库 fits_iso286，φ30 的 H7/k6
Write-Output ""
Write-Output "════ 配合校核（fits_iso286.yaml，24~30 段）════"
$holeES = 21.0; $holeEI = 0.0     # H7
$axEs = 15.0;  $axEi = 2.0       # k6
$Xmax = $holeES - $axEi
$Xmin = $holeEI - $axEs
Write-Output "  H7 孔 (24~30): ES=+$holeES EI=$holeEI"
Write-Output "  k6 轴 (24~30): es=+$axEs ei=+$axEi"
Write-Output "  ⇒ Xmax = ES孔 − ei轴 = $Xmax μm（最大间隙）"
Write-Output "  ⇒ Xmin = EI孔 − es轴 = $Xmin μm（最大过盈）"
Write-Output "  ⇒ 过渡配合，过盈约 $([math]::Abs($Xmin)) μm = $([math]::Abs($Xmin)/1000) mm"
Write-Output "  ⇒ $(if($Xmin -lt 0){'✅ 轻中载旋转内圈：有过盈但小，便于装拆'}else{'⚠ 无过盈，是间隙配合'})"
.bore, # ★ 闭环验证：用轴承库 + 配合库 + 材料库 做一次真实选型
# 题目：设计一根传动轴，传递 P=2.2kW, n=1450 rpm，要求寿命 L10h=10000h
# 判据自检：算出的 C/C比 是否符合工程常识；选的型号是否真的在表里、n_lim 是否够

$csv = "C:\Users\Zegel\solidpilot-mcp\知识库\bearings\single_row_deep_groove_ball_bearing_parameters.csv"
$L = @(Get-Content $csv | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })

# 列位置（已验证）：1=d 2=D 3=B 4=C 5=C0 6=Pu 7=n_ref 8=n_lim 9=mass 10=Designation 15=da 17=ra
function Parse($line) {
    $r = $line.Split(',')
    [pscustomobject]@{
        bore = [double]$r[1]; shell = [double]$r[2]; wid = [double]$r[3]
        C  = [double]$r[4];  C0 = [double]$r[5];  Pu = [double]$r[6]
        nRef = [double]$r[7]; nLim = [double]$r[8]; mass = [double]$r[9]
        Desig = $r[10].Trim(); da = $r[15].Trim(); ra = $r[17].Trim()
    }
}

Write-Output "════ 工况 ════"
$P = 2.2; $n = 1450; $Lh = 10000
Write-Output "  功率 P = $P kW，转速 n = $n rpm，要求寿命 L10h = $Lh h"
# 1) 载荷系数（design_rules: 中等工况 K_A=1.3~1.5，轻载1.3）
$K_A = 1.3
Write-Output "  工况系数 K_A = $K_A（中等冲击）"

# 2) 当量动载荷 P = K_A × (轴承当量载荷)
#    ★ 简化：设径向为主，取载荷系数 X=1, Y=1.4（球轴承，Fr/Fr > e）
#    为演示取径向载荷 Fr = 0.5 × 轴向载荷极限，按轴径初估
$Fr = 1200   # N，按轴径 φ30 估算的径向载荷
$Fa = 300    # N，轴向力
$X = 1.0; $Y = 1.4
$P_eq = [math]::Round($K_A * ($X*$Fr + $Y*$Fa), 1)
Write-Output "  径向载荷 Fr = $Fr N，轴向 Fa = $Fa N"
Write-Output "  当量动载荷 P = K_A·(X·Fr + Y·Fa) = $K_A·($X·$Fr + $Y·$Fa) = $P_eq N"

# 3) 由寿命反算所需动载荷（球轴承 ε=3）
$millions = $Lh * 60 * $n / 1e6
$eps = 3
$C_need = [math]::Round($P_eq * [math]::Pow($millions, 1/$eps), 1)
Write-Output "  寿命转数 = $Lh h × 60 × $n rpm = $([math]::Round($millions*1e6/1e6,1))×10^6 转"
Write-Output "  球轴承 ε=3 ⇒ C_需 = P × (寿命/10^6)^(1/3) = $P_eq × $([math]::Round($millions,2))^(1/3) = $C_need N = $([math]::Round($C_need/1000,2)) kN"

# 4) 查表选型
Write-Output ""
Write-Output "════ 查表选型（C ≥ $C_need N 且 n_lim ≥ $n）════"
$pick = @()
for ($i = 1; $i -lt $L.Count; $i++) {
    try { $b = Parse $L[$i] } catch { continue }
    if ($b.C -ge $C_need -and $b.nLim -ge $n) { $pick += $b }
}
$pick = $pick | Sort-Object d
if ($pick.Count -eq 0) {
    Write-Output "  ⚠ 表中无满足的型号（表内主要是小规格 M3~M5，功率偏大）"
    # 退而求其次：列出承载最接近的
    $all = @(); for ($i=1;$i -lt $L.Count;$i++){ try { $all += Parse $L[$i] } catch {} }
    $all | Sort-Object { [math]::Abs($_.C - $C_need) } | Select-Object -First 3 |
      ForEach-Object { Write-Output "     最近: $($_.Desig)  d=$($_.d) C=$($_.C)kN  差 $([math]::Round($_.C*1000-$C_need,0))N" }
} else {
    Write-Output "  满足条件的型号 $($pick.Count) 个（按内径排序，前 6 个）:"
    $pick | Select-Object -First 6 | ForEach-Object {
        Write-Output ("     {0,-10} d={1,4} D={2,4} B={3,4}  C={4,6}N  n_lim={5,7}  轴肩da={6,5}  ra={7}" -f `
            $_.Desig, $_.d, $_.D, $_.B, ($_.C*1000), $_.nLim, $_.da, $_.ra)
    }
    $best = $pick | Select-Object -First 1
    Write-Output ""
    Write-Output "════ 校核 ════"
    Write-Output "  选用 $($best.Desig)：C=$($best.C)kN / 需 $C_need N ⇒ 实际富余 $([math]::Round($best.C*1000-$C_need,0))N"
    $lifeChk = [math]::Round(($best.C*1000/$P_eq) * 3 * 1e6 / (60*$n) / 1e6, 2)
    Write-Output "  反算寿命 L10h = (C/P)³·10⁶/(60n) = $lifeChk 万小时（要求 $Lh h）"
    Write-Output "  转速校核：n_lim=$($best.nLim) ≥ $n ⇒ $(if($best.nLim -ge $n){'✅'}else{'❌'})"
}

# 5) 配合：按知识库 fits_iso286，φ30 的 H7/k6
Write-Output ""
Write-Output "════ 配合校核（fits_iso286.yaml，24~30 段）════"
$holeES = 21.0; $holeEI = 0.0     # H7
$axEs = 15.0;  $axEi = 2.0       # k6
$Xmax = $holeES - $axEi
$Xmin = $holeEI - $axEs
Write-Output "  H7 孔 (24~30): ES=+$holeES EI=$holeEI"
Write-Output "  k6 轴 (24~30): es=+$axEs ei=+$axEi"
Write-Output "  ⇒ Xmax = ES孔 − ei轴 = $Xmax μm（最大间隙）"
Write-Output "  ⇒ Xmin = EI孔 − es轴 = $Xmin μm（最大过盈）"
Write-Output "  ⇒ 过渡配合，过盈约 $([math]::Abs($Xmin)) μm = $([math]::Abs($Xmin)/1000) mm"
Write-Output "  ⇒ $(if($Xmin -lt 0){'✅ 轻中载旋转内圈：有过盈但小，便于装拆'}else{'⚠ 无过盈，是间隙配合'})"
.bore, $_.B, ($_.C*1000), $_.nLim, $_.da, $_.ra)
    }
    $best = $pick | Select-Object -First 1
    Write-Output ""
    Write-Output "════ 校核 ════"
    Write-Output "  选用 $($best.Desig)：C=$($best.C)kN / 需 $C_need N ⇒ 实际富余 $([math]::Round($best.C*1000-$C_need,0))N"
    $lifeChk = [math]::Round(($best.C*1000/$P_eq) * 3 * 1e6 / (60*$n) / 1e6, 2)
    Write-Output "  反算寿命 L10h = (C/P)³·10⁶/(60n) = $lifeChk 万小时（要求 $Lh h）"
    Write-Output "  转速校核：n_lim=$($best.nLim) ≥ $n ⇒ $(if($best.nLim -ge $n){'✅'}else{'❌'})"
}

# 5) 配合：按知识库 fits_iso286，φ30 的 H7/k6
Write-Output ""
Write-Output "════ 配合校核（fits_iso286.yaml，24~30 段）════"
$holeES = 21.0; $holeEI = 0.0     # H7
$axEs = 15.0;  $axEi = 2.0       # k6
$Xmax = $holeES - $axEi
$Xmin = $holeEI - $axEs
Write-Output "  H7 孔 (24~30): ES=+$holeES EI=$holeEI"
Write-Output "  k6 轴 (24~30): es=+$axEs ei=+$axEi"
Write-Output "  ⇒ Xmax = ES孔 − ei轴 = $Xmax μm（最大间隙）"
Write-Output "  ⇒ Xmin = EI孔 − es轴 = $Xmin μm（最大过盈）"
Write-Output "  ⇒ 过渡配合，过盈约 $([math]::Abs($Xmin)) μm = $([math]::Abs($Xmin)/1000) mm"
Write-Output "  ⇒ $(if($Xmin -lt 0){'✅ 轻中载旋转内圈：有过盈但小，便于装拆'}else{'⚠ 无过盈，是间隙配合'})"
.shell, $_.B, ($_.C*1000), $_.nLim, $_.da, $_.ra)
    }
    $best = $pick | Select-Object -First 1
    Write-Output ""
    Write-Output "════ 校核 ════"
    Write-Output "  选用 $($best.Desig)：C=$($best.C)kN / 需 $C_need N ⇒ 实际富余 $([math]::Round($best.C*1000-$C_need,0))N"
    $lifeChk = [math]::Round(($best.C*1000/$P_eq) * 3 * 1e6 / (60*$n) / 1e6, 2)
    Write-Output "  反算寿命 L10h = (C/P)³·10⁶/(60n) = $lifeChk 万小时（要求 $Lh h）"
    Write-Output "  转速校核：n_lim=$($best.nLim) ≥ $n ⇒ $(if($best.nLim -ge $n){'✅'}else{'❌'})"
}

# 5) 配合：按知识库 fits_iso286，φ30 的 H7/k6
Write-Output ""
Write-Output "════ 配合校核（fits_iso286.yaml，24~30 段）════"
$holeES = 21.0; $holeEI = 0.0     # H7
$axEs = 15.0;  $axEi = 2.0       # k6
$Xmax = $holeES - $axEi
$Xmin = $holeEI - $axEs
Write-Output "  H7 孔 (24~30): ES=+$holeES EI=$holeEI"
Write-Output "  k6 轴 (24~30): es=+$axEs ei=+$axEi"
Write-Output "  ⇒ Xmax = ES孔 − ei轴 = $Xmax μm（最大间隙）"
Write-Output "  ⇒ Xmin = EI孔 − es轴 = $Xmin μm（最大过盈）"
Write-Output "  ⇒ 过渡配合，过盈约 $([math]::Abs($Xmin)) μm = $([math]::Abs($Xmin)/1000) mm"
Write-Output "  ⇒ $(if($Xmin -lt 0){'✅ 轻中载旋转内圈：有过盈但小，便于装拆'}else{'⚠ 无过盈，是间隙配合'})"
.bore, # ★ 闭环验证：用轴承库 + 配合库 + 材料库 做一次真实选型
# 题目：设计一根传动轴，传递 P=2.2kW, n=1450 rpm，要求寿命 L10h=10000h
# 判据自检：算出的 C/C比 是否符合工程常识；选的型号是否真的在表里、n_lim 是否够

$csv = "C:\Users\Zegel\solidpilot-mcp\知识库\bearings\single_row_deep_groove_ball_bearing_parameters.csv"
$L = @(Get-Content $csv | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })

# 列位置（已验证）：1=d 2=D 3=B 4=C 5=C0 6=Pu 7=n_ref 8=n_lim 9=mass 10=Designation 15=da 17=ra
function Parse($line) {
    $r = $line.Split(',')
    [pscustomobject]@{
        bore = [double]$r[1]; shell = [double]$r[2]; wid = [double]$r[3]
        C  = [double]$r[4];  C0 = [double]$r[5];  Pu = [double]$r[6]
        nRef = [double]$r[7]; nLim = [double]$r[8]; mass = [double]$r[9]
        Desig = $r[10].Trim(); da = $r[15].Trim(); ra = $r[17].Trim()
    }
}

Write-Output "════ 工况 ════"
$P = 2.2; $n = 1450; $Lh = 10000
Write-Output "  功率 P = $P kW，转速 n = $n rpm，要求寿命 L10h = $Lh h"
# 1) 载荷系数（design_rules: 中等工况 K_A=1.3~1.5，轻载1.3）
$K_A = 1.3
Write-Output "  工况系数 K_A = $K_A（中等冲击）"

# 2) 当量动载荷 P = K_A × (轴承当量载荷)
#    ★ 简化：设径向为主，取载荷系数 X=1, Y=1.4（球轴承，Fr/Fr > e）
#    为演示取径向载荷 Fr = 0.5 × 轴向载荷极限，按轴径初估
$Fr = 1200   # N，按轴径 φ30 估算的径向载荷
$Fa = 300    # N，轴向力
$X = 1.0; $Y = 1.4
$P_eq = [math]::Round($K_A * ($X*$Fr + $Y*$Fa), 1)
Write-Output "  径向载荷 Fr = $Fr N，轴向 Fa = $Fa N"
Write-Output "  当量动载荷 P = K_A·(X·Fr + Y·Fa) = $K_A·($X·$Fr + $Y·$Fa) = $P_eq N"

# 3) 由寿命反算所需动载荷（球轴承 ε=3）
$millions = $Lh * 60 * $n / 1e6
$eps = 3
$C_need = [math]::Round($P_eq * [math]::Pow($millions, 1/$eps), 1)
Write-Output "  寿命转数 = $Lh h × 60 × $n rpm = $([math]::Round($millions*1e6/1e6,1))×10^6 转"
Write-Output "  球轴承 ε=3 ⇒ C_需 = P × (寿命/10^6)^(1/3) = $P_eq × $([math]::Round($millions,2))^(1/3) = $C_need N = $([math]::Round($C_need/1000,2)) kN"

# 4) 查表选型
Write-Output ""
Write-Output "════ 查表选型（C ≥ $C_need N 且 n_lim ≥ $n）════"
$pick = @()
for ($i = 1; $i -lt $L.Count; $i++) {
    try { $b = Parse $L[$i] } catch { continue }
    if ($b.C -ge $C_need -and $b.nLim -ge $n) { $pick += $b }
}
$pick = $pick | Sort-Object d
if ($pick.Count -eq 0) {
    Write-Output "  ⚠ 表中无满足的型号（表内主要是小规格 M3~M5，功率偏大）"
    # 退而求其次：列出承载最接近的
    $all = @(); for ($i=1;$i -lt $L.Count;$i++){ try { $all += Parse $L[$i] } catch {} }
    $all | Sort-Object { [math]::Abs($_.C - $C_need) } | Select-Object -First 3 |
      ForEach-Object { Write-Output "     最近: $($_.Desig)  d=$(# ★ 闭环验证：用轴承库 + 配合库 + 材料库 做一次真实选型
# 题目：设计一根传动轴，传递 P=2.2kW, n=1450 rpm，要求寿命 L10h=10000h
# 判据自检：算出的 C/C比 是否符合工程常识；选的型号是否真的在表里、n_lim 是否够

$csv = "C:\Users\Zegel\solidpilot-mcp\知识库\bearings\single_row_deep_groove_ball_bearing_parameters.csv"
$L = @(Get-Content $csv | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })

# 列位置（已验证）：1=d 2=D 3=B 4=C 5=C0 6=Pu 7=n_ref 8=n_lim 9=mass 10=Designation 15=da 17=ra
function Parse($line) {
    $r = $line.Split(',')
    [pscustomobject]@{
        bore = [double]$r[1]; shell = [double]$r[2]; wid = [double]$r[3]
        C  = [double]$r[4];  C0 = [double]$r[5];  Pu = [double]$r[6]
        nRef = [double]$r[7]; nLim = [double]$r[8]; mass = [double]$r[9]
        Desig = $r[10].Trim(); da = $r[15].Trim(); ra = $r[17].Trim()
    }
}

Write-Output "════ 工况 ════"
$P = 2.2; $n = 1450; $Lh = 10000
Write-Output "  功率 P = $P kW，转速 n = $n rpm，要求寿命 L10h = $Lh h"
# 1) 载荷系数（design_rules: 中等工况 K_A=1.3~1.5，轻载1.3）
$K_A = 1.3
Write-Output "  工况系数 K_A = $K_A（中等冲击）"

# 2) 当量动载荷 P = K_A × (轴承当量载荷)
#    ★ 简化：设径向为主，取载荷系数 X=1, Y=1.4（球轴承，Fr/Fr > e）
#    为演示取径向载荷 Fr = 0.5 × 轴向载荷极限，按轴径初估
$Fr = 1200   # N，按轴径 φ30 估算的径向载荷
$Fa = 300    # N，轴向力
$X = 1.0; $Y = 1.4
$P_eq = [math]::Round($K_A * ($X*$Fr + $Y*$Fa), 1)
Write-Output "  径向载荷 Fr = $Fr N，轴向 Fa = $Fa N"
Write-Output "  当量动载荷 P = K_A·(X·Fr + Y·Fa) = $K_A·($X·$Fr + $Y·$Fa) = $P_eq N"

# 3) 由寿命反算所需动载荷（球轴承 ε=3）
$millions = $Lh * 60 * $n / 1e6
$eps = 3
$C_need = [math]::Round($P_eq * [math]::Pow($millions, 1/$eps), 1)
Write-Output "  寿命转数 = $Lh h × 60 × $n rpm = $([math]::Round($millions*1e6/1e6,1))×10^6 转"
Write-Output "  球轴承 ε=3 ⇒ C_需 = P × (寿命/10^6)^(1/3) = $P_eq × $([math]::Round($millions,2))^(1/3) = $C_need N = $([math]::Round($C_need/1000,2)) kN"

# 4) 查表选型
Write-Output ""
Write-Output "════ 查表选型（C ≥ $C_need N 且 n_lim ≥ $n）════"
$pick = @()
for ($i = 1; $i -lt $L.Count; $i++) {
    try { $b = Parse $L[$i] } catch { continue }
    if ($b.C -ge $C_need -and $b.nLim -ge $n) { $pick += $b }
}
$pick = $pick | Sort-Object d
if ($pick.Count -eq 0) {
    Write-Output "  ⚠ 表中无满足的型号（表内主要是小规格 M3~M5，功率偏大）"
    # 退而求其次：列出承载最接近的
    $all = @(); for ($i=1;$i -lt $L.Count;$i++){ try { $all += Parse $L[$i] } catch {} }
    $all | Sort-Object { [math]::Abs($_.C - $C_need) } | Select-Object -First 3 |
      ForEach-Object { Write-Output "     最近: $($_.Desig)  d=$(# ★ 闭环验证：用轴承库 + 配合库 + 材料库 做一次真实选型
# 题目：设计一根传动轴，传递 P=2.2kW, n=1450 rpm，要求寿命 L10h=10000h
# 判据自检：算出的 C/C比 是否符合工程常识；选的型号是否真的在表里、n_lim 是否够

$csv = "C:\Users\Zegel\solidpilot-mcp\知识库\bearings\single_row_deep_groove_ball_bearing_parameters.csv"
$L = @(Get-Content $csv | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })

# 列位置（已验证）：1=d 2=D 3=B 4=C 5=C0 6=Pu 7=n_ref 8=n_lim 9=mass 10=Designation 15=da 17=ra
function Parse($line) {
    $r = $line.Split(',')
    [pscustomobject]@{
        bore = [double]$r[1]; shell = [double]$r[2]; wid = [double]$r[3]
        C  = [double]$r[4];  C0 = [double]$r[5];  Pu = [double]$r[6]
        nRef = [double]$r[7]; nLim = [double]$r[8]; mass = [double]$r[9]
        Desig = $r[10].Trim(); da = $r[15].Trim(); ra = $r[17].Trim()
    }
}

Write-Output "════ 工况 ════"
$P = 2.2; $n = 1450; $Lh = 10000
Write-Output "  功率 P = $P kW，转速 n = $n rpm，要求寿命 L10h = $Lh h"
# 1) 载荷系数（design_rules: 中等工况 K_A=1.3~1.5，轻载1.3）
$K_A = 1.3
Write-Output "  工况系数 K_A = $K_A（中等冲击）"

# 2) 当量动载荷 P = K_A × (轴承当量载荷)
#    ★ 简化：设径向为主，取载荷系数 X=1, Y=1.4（球轴承，Fr/Fr > e）
#    为演示取径向载荷 Fr = 0.5 × 轴向载荷极限，按轴径初估
$Fr = 1200   # N，按轴径 φ30 估算的径向载荷
$Fa = 300    # N，轴向力
$X = 1.0; $Y = 1.4
$P_eq = [math]::Round($K_A * ($X*$Fr + $Y*$Fa), 1)
Write-Output "  径向载荷 Fr = $Fr N，轴向 Fa = $Fa N"
Write-Output "  当量动载荷 P = K_A·(X·Fr + Y·Fa) = $K_A·($X·$Fr + $Y·$Fa) = $P_eq N"

# 3) 由寿命反算所需动载荷（球轴承 ε=3）
$millions = $Lh * 60 * $n / 1e6
$eps = 3
$C_need = [math]::Round($P_eq * [math]::Pow($millions, 1/$eps), 1)
Write-Output "  寿命转数 = $Lh h × 60 × $n rpm = $([math]::Round($millions*1e6/1e6,1))×10^6 转"
Write-Output "  球轴承 ε=3 ⇒ C_需 = P × (寿命/10^6)^(1/3) = $P_eq × $([math]::Round($millions,2))^(1/3) = $C_need N = $([math]::Round($C_need/1000,2)) kN"

# 4) 查表选型
Write-Output ""
Write-Output "════ 查表选型（C ≥ $C_need N 且 n_lim ≥ $n）════"
$pick = @()
for ($i = 1; $i -lt $L.Count; $i++) {
    try { $b = Parse $L[$i] } catch { continue }
    if ($b.C -ge $C_need -and $b.nLim -ge $n) { $pick += $b }
}
$pick = $pick | Sort-Object d
if ($pick.Count -eq 0) {
    Write-Output "  ⚠ 表中无满足的型号（表内主要是小规格 M3~M5，功率偏大）"
    # 退而求其次：列出承载最接近的
    $all = @(); for ($i=1;$i -lt $L.Count;$i++){ try { $all += Parse $L[$i] } catch {} }
    $all | Sort-Object { [math]::Abs($_.C - $C_need) } | Select-Object -First 3 |
      ForEach-Object { Write-Output "     最近: $($_.Desig)  d=$($_.d) C=$($_.C)kN  差 $([math]::Round($_.C*1000-$C_need,0))N" }
} else {
    Write-Output "  满足条件的型号 $($pick.Count) 个（按内径排序，前 6 个）:"
    $pick | Select-Object -First 6 | ForEach-Object {
        Write-Output ("     {0,-10} d={1,4} D={2,4} B={3,4}  C={4,6}N  n_lim={5,7}  轴肩da={6,5}  ra={7}" -f `
            $_.Desig, $_.d, $_.D, $_.B, ($_.C*1000), $_.nLim, $_.da, $_.ra)
    }
    $best = $pick | Select-Object -First 1
    Write-Output ""
    Write-Output "════ 校核 ════"
    Write-Output "  选用 $($best.Desig)：C=$($best.C)kN / 需 $C_need N ⇒ 实际富余 $([math]::Round($best.C*1000-$C_need,0))N"
    $lifeChk = [math]::Round(($best.C*1000/$P_eq) * 3 * 1e6 / (60*$n) / 1e6, 2)
    Write-Output "  反算寿命 L10h = (C/P)³·10⁶/(60n) = $lifeChk 万小时（要求 $Lh h）"
    Write-Output "  转速校核：n_lim=$($best.nLim) ≥ $n ⇒ $(if($best.nLim -ge $n){'✅'}else{'❌'})"
}

# 5) 配合：按知识库 fits_iso286，φ30 的 H7/k6
Write-Output ""
Write-Output "════ 配合校核（fits_iso286.yaml，24~30 段）════"
$holeES = 21.0; $holeEI = 0.0     # H7
$axEs = 15.0;  $axEi = 2.0       # k6
$Xmax = $holeES - $axEi
$Xmin = $holeEI - $axEs
Write-Output "  H7 孔 (24~30): ES=+$holeES EI=$holeEI"
Write-Output "  k6 轴 (24~30): es=+$axEs ei=+$axEi"
Write-Output "  ⇒ Xmax = ES孔 − ei轴 = $Xmax μm（最大间隙）"
Write-Output "  ⇒ Xmin = EI孔 − es轴 = $Xmin μm（最大过盈）"
Write-Output "  ⇒ 过渡配合，过盈约 $([math]::Abs($Xmin)) μm = $([math]::Abs($Xmin)/1000) mm"
Write-Output "  ⇒ $(if($Xmin -lt 0){'✅ 轻中载旋转内圈：有过盈但小，便于装拆'}else{'⚠ 无过盈，是间隙配合'})"
.bore) C=$($_.C)kN  差 $([math]::Round($_.C*1000-$C_need,0))N" }
} else {
    Write-Output "  满足条件的型号 $($pick.Count) 个（按内径排序，前 6 个）:"
    $pick | Select-Object -First 6 | ForEach-Object {
        Write-Output ("     {0,-10} d={1,4} D={2,4} B={3,4}  C={4,6}N  n_lim={5,7}  轴肩da={6,5}  ra={7}" -f `
            $_.Desig, # ★ 闭环验证：用轴承库 + 配合库 + 材料库 做一次真实选型
# 题目：设计一根传动轴，传递 P=2.2kW, n=1450 rpm，要求寿命 L10h=10000h
# 判据自检：算出的 C/C比 是否符合工程常识；选的型号是否真的在表里、n_lim 是否够

$csv = "C:\Users\Zegel\solidpilot-mcp\知识库\bearings\single_row_deep_groove_ball_bearing_parameters.csv"
$L = @(Get-Content $csv | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })

# 列位置（已验证）：1=d 2=D 3=B 4=C 5=C0 6=Pu 7=n_ref 8=n_lim 9=mass 10=Designation 15=da 17=ra
function Parse($line) {
    $r = $line.Split(',')
    [pscustomobject]@{
        bore = [double]$r[1]; shell = [double]$r[2]; wid = [double]$r[3]
        C  = [double]$r[4];  C0 = [double]$r[5];  Pu = [double]$r[6]
        nRef = [double]$r[7]; nLim = [double]$r[8]; mass = [double]$r[9]
        Desig = $r[10].Trim(); da = $r[15].Trim(); ra = $r[17].Trim()
    }
}

Write-Output "════ 工况 ════"
$P = 2.2; $n = 1450; $Lh = 10000
Write-Output "  功率 P = $P kW，转速 n = $n rpm，要求寿命 L10h = $Lh h"
# 1) 载荷系数（design_rules: 中等工况 K_A=1.3~1.5，轻载1.3）
$K_A = 1.3
Write-Output "  工况系数 K_A = $K_A（中等冲击）"

# 2) 当量动载荷 P = K_A × (轴承当量载荷)
#    ★ 简化：设径向为主，取载荷系数 X=1, Y=1.4（球轴承，Fr/Fr > e）
#    为演示取径向载荷 Fr = 0.5 × 轴向载荷极限，按轴径初估
$Fr = 1200   # N，按轴径 φ30 估算的径向载荷
$Fa = 300    # N，轴向力
$X = 1.0; $Y = 1.4
$P_eq = [math]::Round($K_A * ($X*$Fr + $Y*$Fa), 1)
Write-Output "  径向载荷 Fr = $Fr N，轴向 Fa = $Fa N"
Write-Output "  当量动载荷 P = K_A·(X·Fr + Y·Fa) = $K_A·($X·$Fr + $Y·$Fa) = $P_eq N"

# 3) 由寿命反算所需动载荷（球轴承 ε=3）
$millions = $Lh * 60 * $n / 1e6
$eps = 3
$C_need = [math]::Round($P_eq * [math]::Pow($millions, 1/$eps), 1)
Write-Output "  寿命转数 = $Lh h × 60 × $n rpm = $([math]::Round($millions*1e6/1e6,1))×10^6 转"
Write-Output "  球轴承 ε=3 ⇒ C_需 = P × (寿命/10^6)^(1/3) = $P_eq × $([math]::Round($millions,2))^(1/3) = $C_need N = $([math]::Round($C_need/1000,2)) kN"

# 4) 查表选型
Write-Output ""
Write-Output "════ 查表选型（C ≥ $C_need N 且 n_lim ≥ $n）════"
$pick = @()
for ($i = 1; $i -lt $L.Count; $i++) {
    try { $b = Parse $L[$i] } catch { continue }
    if ($b.C -ge $C_need -and $b.nLim -ge $n) { $pick += $b }
}
$pick = $pick | Sort-Object d
if ($pick.Count -eq 0) {
    Write-Output "  ⚠ 表中无满足的型号（表内主要是小规格 M3~M5，功率偏大）"
    # 退而求其次：列出承载最接近的
    $all = @(); for ($i=1;$i -lt $L.Count;$i++){ try { $all += Parse $L[$i] } catch {} }
    $all | Sort-Object { [math]::Abs($_.C - $C_need) } | Select-Object -First 3 |
      ForEach-Object { Write-Output "     最近: $($_.Desig)  d=$($_.d) C=$($_.C)kN  差 $([math]::Round($_.C*1000-$C_need,0))N" }
} else {
    Write-Output "  满足条件的型号 $($pick.Count) 个（按内径排序，前 6 个）:"
    $pick | Select-Object -First 6 | ForEach-Object {
        Write-Output ("     {0,-10} d={1,4} D={2,4} B={3,4}  C={4,6}N  n_lim={5,7}  轴肩da={6,5}  ra={7}" -f `
            $_.Desig, $_.d, $_.D, $_.B, ($_.C*1000), $_.nLim, $_.da, $_.ra)
    }
    $best = $pick | Select-Object -First 1
    Write-Output ""
    Write-Output "════ 校核 ════"
    Write-Output "  选用 $($best.Desig)：C=$($best.C)kN / 需 $C_need N ⇒ 实际富余 $([math]::Round($best.C*1000-$C_need,0))N"
    $lifeChk = [math]::Round(($best.C*1000/$P_eq) * 3 * 1e6 / (60*$n) / 1e6, 2)
    Write-Output "  反算寿命 L10h = (C/P)³·10⁶/(60n) = $lifeChk 万小时（要求 $Lh h）"
    Write-Output "  转速校核：n_lim=$($best.nLim) ≥ $n ⇒ $(if($best.nLim -ge $n){'✅'}else{'❌'})"
}

# 5) 配合：按知识库 fits_iso286，φ30 的 H7/k6
Write-Output ""
Write-Output "════ 配合校核（fits_iso286.yaml，24~30 段）════"
$holeES = 21.0; $holeEI = 0.0     # H7
$axEs = 15.0;  $axEi = 2.0       # k6
$Xmax = $holeES - $axEi
$Xmin = $holeEI - $axEs
Write-Output "  H7 孔 (24~30): ES=+$holeES EI=$holeEI"
Write-Output "  k6 轴 (24~30): es=+$axEs ei=+$axEi"
Write-Output "  ⇒ Xmax = ES孔 − ei轴 = $Xmax μm（最大间隙）"
Write-Output "  ⇒ Xmin = EI孔 − es轴 = $Xmin μm（最大过盈）"
Write-Output "  ⇒ 过渡配合，过盈约 $([math]::Abs($Xmin)) μm = $([math]::Abs($Xmin)/1000) mm"
Write-Output "  ⇒ $(if($Xmin -lt 0){'✅ 轻中载旋转内圈：有过盈但小，便于装拆'}else{'⚠ 无过盈，是间隙配合'})"
.bore, # ★ 闭环验证：用轴承库 + 配合库 + 材料库 做一次真实选型
# 题目：设计一根传动轴，传递 P=2.2kW, n=1450 rpm，要求寿命 L10h=10000h
# 判据自检：算出的 C/C比 是否符合工程常识；选的型号是否真的在表里、n_lim 是否够

$csv = "C:\Users\Zegel\solidpilot-mcp\知识库\bearings\single_row_deep_groove_ball_bearing_parameters.csv"
$L = @(Get-Content $csv | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })

# 列位置（已验证）：1=d 2=D 3=B 4=C 5=C0 6=Pu 7=n_ref 8=n_lim 9=mass 10=Designation 15=da 17=ra
function Parse($line) {
    $r = $line.Split(',')
    [pscustomobject]@{
        bore = [double]$r[1]; shell = [double]$r[2]; wid = [double]$r[3]
        C  = [double]$r[4];  C0 = [double]$r[5];  Pu = [double]$r[6]
        nRef = [double]$r[7]; nLim = [double]$r[8]; mass = [double]$r[9]
        Desig = $r[10].Trim(); da = $r[15].Trim(); ra = $r[17].Trim()
    }
}

Write-Output "════ 工况 ════"
$P = 2.2; $n = 1450; $Lh = 10000
Write-Output "  功率 P = $P kW，转速 n = $n rpm，要求寿命 L10h = $Lh h"
# 1) 载荷系数（design_rules: 中等工况 K_A=1.3~1.5，轻载1.3）
$K_A = 1.3
Write-Output "  工况系数 K_A = $K_A（中等冲击）"

# 2) 当量动载荷 P = K_A × (轴承当量载荷)
#    ★ 简化：设径向为主，取载荷系数 X=1, Y=1.4（球轴承，Fr/Fr > e）
#    为演示取径向载荷 Fr = 0.5 × 轴向载荷极限，按轴径初估
$Fr = 1200   # N，按轴径 φ30 估算的径向载荷
$Fa = 300    # N，轴向力
$X = 1.0; $Y = 1.4
$P_eq = [math]::Round($K_A * ($X*$Fr + $Y*$Fa), 1)
Write-Output "  径向载荷 Fr = $Fr N，轴向 Fa = $Fa N"
Write-Output "  当量动载荷 P = K_A·(X·Fr + Y·Fa) = $K_A·($X·$Fr + $Y·$Fa) = $P_eq N"

# 3) 由寿命反算所需动载荷（球轴承 ε=3）
$millions = $Lh * 60 * $n / 1e6
$eps = 3
$C_need = [math]::Round($P_eq * [math]::Pow($millions, 1/$eps), 1)
Write-Output "  寿命转数 = $Lh h × 60 × $n rpm = $([math]::Round($millions*1e6/1e6,1))×10^6 转"
Write-Output "  球轴承 ε=3 ⇒ C_需 = P × (寿命/10^6)^(1/3) = $P_eq × $([math]::Round($millions,2))^(1/3) = $C_need N = $([math]::Round($C_need/1000,2)) kN"

# 4) 查表选型
Write-Output ""
Write-Output "════ 查表选型（C ≥ $C_need N 且 n_lim ≥ $n）════"
$pick = @()
for ($i = 1; $i -lt $L.Count; $i++) {
    try { $b = Parse $L[$i] } catch { continue }
    if ($b.C -ge $C_need -and $b.nLim -ge $n) { $pick += $b }
}
$pick = $pick | Sort-Object d
if ($pick.Count -eq 0) {
    Write-Output "  ⚠ 表中无满足的型号（表内主要是小规格 M3~M5，功率偏大）"
    # 退而求其次：列出承载最接近的
    $all = @(); for ($i=1;$i -lt $L.Count;$i++){ try { $all += Parse $L[$i] } catch {} }
    $all | Sort-Object { [math]::Abs($_.C - $C_need) } | Select-Object -First 3 |
      ForEach-Object { Write-Output "     最近: $($_.Desig)  d=$($_.d) C=$($_.C)kN  差 $([math]::Round($_.C*1000-$C_need,0))N" }
} else {
    Write-Output "  满足条件的型号 $($pick.Count) 个（按内径排序，前 6 个）:"
    $pick | Select-Object -First 6 | ForEach-Object {
        Write-Output ("     {0,-10} d={1,4} D={2,4} B={3,4}  C={4,6}N  n_lim={5,7}  轴肩da={6,5}  ra={7}" -f `
            $_.Desig, $_.d, $_.D, $_.B, ($_.C*1000), $_.nLim, $_.da, $_.ra)
    }
    $best = $pick | Select-Object -First 1
    Write-Output ""
    Write-Output "════ 校核 ════"
    Write-Output "  选用 $($best.Desig)：C=$($best.C)kN / 需 $C_need N ⇒ 实际富余 $([math]::Round($best.C*1000-$C_need,0))N"
    $lifeChk = [math]::Round(($best.C*1000/$P_eq) * 3 * 1e6 / (60*$n) / 1e6, 2)
    Write-Output "  反算寿命 L10h = (C/P)³·10⁶/(60n) = $lifeChk 万小时（要求 $Lh h）"
    Write-Output "  转速校核：n_lim=$($best.nLim) ≥ $n ⇒ $(if($best.nLim -ge $n){'✅'}else{'❌'})"
}

# 5) 配合：按知识库 fits_iso286，φ30 的 H7/k6
Write-Output ""
Write-Output "════ 配合校核（fits_iso286.yaml，24~30 段）════"
$holeES = 21.0; $holeEI = 0.0     # H7
$axEs = 15.0;  $axEi = 2.0       # k6
$Xmax = $holeES - $axEi
$Xmin = $holeEI - $axEs
Write-Output "  H7 孔 (24~30): ES=+$holeES EI=$holeEI"
Write-Output "  k6 轴 (24~30): es=+$axEs ei=+$axEi"
Write-Output "  ⇒ Xmax = ES孔 − ei轴 = $Xmax μm（最大间隙）"
Write-Output "  ⇒ Xmin = EI孔 − es轴 = $Xmin μm（最大过盈）"
Write-Output "  ⇒ 过渡配合，过盈约 $([math]::Abs($Xmin)) μm = $([math]::Abs($Xmin)/1000) mm"
Write-Output "  ⇒ $(if($Xmin -lt 0){'✅ 轻中载旋转内圈：有过盈但小，便于装拆'}else{'⚠ 无过盈，是间隙配合'})"
.bore, $_.B, ($_.C*1000), $_.nLim, $_.da, $_.ra)
    }
    $best = $pick | Select-Object -First 1
    Write-Output ""
    Write-Output "════ 校核 ════"
    Write-Output "  选用 $($best.Desig)：C=$($best.C)kN / 需 $C_need N ⇒ 实际富余 $([math]::Round($best.C*1000-$C_need,0))N"
    $lifeChk = [math]::Round(($best.C*1000/$P_eq) * 3 * 1e6 / (60*$n) / 1e6, 2)
    Write-Output "  反算寿命 L10h = (C/P)³·10⁶/(60n) = $lifeChk 万小时（要求 $Lh h）"
    Write-Output "  转速校核：n_lim=$($best.nLim) ≥ $n ⇒ $(if($best.nLim -ge $n){'✅'}else{'❌'})"
}

# 5) 配合：按知识库 fits_iso286，φ30 的 H7/k6
Write-Output ""
Write-Output "════ 配合校核（fits_iso286.yaml，24~30 段）════"
$holeES = 21.0; $holeEI = 0.0     # H7
$axEs = 15.0;  $axEi = 2.0       # k6
$Xmax = $holeES - $axEi
$Xmin = $holeEI - $axEs
Write-Output "  H7 孔 (24~30): ES=+$holeES EI=$holeEI"
Write-Output "  k6 轴 (24~30): es=+$axEs ei=+$axEi"
Write-Output "  ⇒ Xmax = ES孔 − ei轴 = $Xmax μm（最大间隙）"
Write-Output "  ⇒ Xmin = EI孔 − es轴 = $Xmin μm（最大过盈）"
Write-Output "  ⇒ 过渡配合，过盈约 $([math]::Abs($Xmin)) μm = $([math]::Abs($Xmin)/1000) mm"
Write-Output "  ⇒ $(if($Xmin -lt 0){'✅ 轻中载旋转内圈：有过盈但小，便于装拆'}else{'⚠ 无过盈，是间隙配合'})"
.shell) C=$($_.C)kN  差 $([math]::Round($_.C*1000-$C_need,0))N" }
} else {
    Write-Output "  满足条件的型号 $($pick.Count) 个（按内径排序，前 6 个）:"
    $pick | Select-Object -First 6 | ForEach-Object {
        Write-Output ("     {0,-10} d={1,4} D={2,4} B={3,4}  C={4,6}N  n_lim={5,7}  轴肩da={6,5}  ra={7}" -f `
            $_.Desig, # ★ 闭环验证：用轴承库 + 配合库 + 材料库 做一次真实选型
# 题目：设计一根传动轴，传递 P=2.2kW, n=1450 rpm，要求寿命 L10h=10000h
# 判据自检：算出的 C/C比 是否符合工程常识；选的型号是否真的在表里、n_lim 是否够

$csv = "C:\Users\Zegel\solidpilot-mcp\知识库\bearings\single_row_deep_groove_ball_bearing_parameters.csv"
$L = @(Get-Content $csv | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })

# 列位置（已验证）：1=d 2=D 3=B 4=C 5=C0 6=Pu 7=n_ref 8=n_lim 9=mass 10=Designation 15=da 17=ra
function Parse($line) {
    $r = $line.Split(',')
    [pscustomobject]@{
        bore = [double]$r[1]; shell = [double]$r[2]; wid = [double]$r[3]
        C  = [double]$r[4];  C0 = [double]$r[5];  Pu = [double]$r[6]
        nRef = [double]$r[7]; nLim = [double]$r[8]; mass = [double]$r[9]
        Desig = $r[10].Trim(); da = $r[15].Trim(); ra = $r[17].Trim()
    }
}

Write-Output "════ 工况 ════"
$P = 2.2; $n = 1450; $Lh = 10000
Write-Output "  功率 P = $P kW，转速 n = $n rpm，要求寿命 L10h = $Lh h"
# 1) 载荷系数（design_rules: 中等工况 K_A=1.3~1.5，轻载1.3）
$K_A = 1.3
Write-Output "  工况系数 K_A = $K_A（中等冲击）"

# 2) 当量动载荷 P = K_A × (轴承当量载荷)
#    ★ 简化：设径向为主，取载荷系数 X=1, Y=1.4（球轴承，Fr/Fr > e）
#    为演示取径向载荷 Fr = 0.5 × 轴向载荷极限，按轴径初估
$Fr = 1200   # N，按轴径 φ30 估算的径向载荷
$Fa = 300    # N，轴向力
$X = 1.0; $Y = 1.4
$P_eq = [math]::Round($K_A * ($X*$Fr + $Y*$Fa), 1)
Write-Output "  径向载荷 Fr = $Fr N，轴向 Fa = $Fa N"
Write-Output "  当量动载荷 P = K_A·(X·Fr + Y·Fa) = $K_A·($X·$Fr + $Y·$Fa) = $P_eq N"

# 3) 由寿命反算所需动载荷（球轴承 ε=3）
$millions = $Lh * 60 * $n / 1e6
$eps = 3
$C_need = [math]::Round($P_eq * [math]::Pow($millions, 1/$eps), 1)
Write-Output "  寿命转数 = $Lh h × 60 × $n rpm = $([math]::Round($millions*1e6/1e6,1))×10^6 转"
Write-Output "  球轴承 ε=3 ⇒ C_需 = P × (寿命/10^6)^(1/3) = $P_eq × $([math]::Round($millions,2))^(1/3) = $C_need N = $([math]::Round($C_need/1000,2)) kN"

# 4) 查表选型
Write-Output ""
Write-Output "════ 查表选型（C ≥ $C_need N 且 n_lim ≥ $n）════"
$pick = @()
for ($i = 1; $i -lt $L.Count; $i++) {
    try { $b = Parse $L[$i] } catch { continue }
    if ($b.C -ge $C_need -and $b.nLim -ge $n) { $pick += $b }
}
$pick = $pick | Sort-Object d
if ($pick.Count -eq 0) {
    Write-Output "  ⚠ 表中无满足的型号（表内主要是小规格 M3~M5，功率偏大）"
    # 退而求其次：列出承载最接近的
    $all = @(); for ($i=1;$i -lt $L.Count;$i++){ try { $all += Parse $L[$i] } catch {} }
    $all | Sort-Object { [math]::Abs($_.C - $C_need) } | Select-Object -First 3 |
      ForEach-Object { Write-Output "     最近: $($_.Desig)  d=$(# ★ 闭环验证：用轴承库 + 配合库 + 材料库 做一次真实选型
# 题目：设计一根传动轴，传递 P=2.2kW, n=1450 rpm，要求寿命 L10h=10000h
# 判据自检：算出的 C/C比 是否符合工程常识；选的型号是否真的在表里、n_lim 是否够

$csv = "C:\Users\Zegel\solidpilot-mcp\知识库\bearings\single_row_deep_groove_ball_bearing_parameters.csv"
$L = @(Get-Content $csv | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })

# 列位置（已验证）：1=d 2=D 3=B 4=C 5=C0 6=Pu 7=n_ref 8=n_lim 9=mass 10=Designation 15=da 17=ra
function Parse($line) {
    $r = $line.Split(',')
    [pscustomobject]@{
        bore = [double]$r[1]; shell = [double]$r[2]; wid = [double]$r[3]
        C  = [double]$r[4];  C0 = [double]$r[5];  Pu = [double]$r[6]
        nRef = [double]$r[7]; nLim = [double]$r[8]; mass = [double]$r[9]
        Desig = $r[10].Trim(); da = $r[15].Trim(); ra = $r[17].Trim()
    }
}

Write-Output "════ 工况 ════"
$P = 2.2; $n = 1450; $Lh = 10000
Write-Output "  功率 P = $P kW，转速 n = $n rpm，要求寿命 L10h = $Lh h"
# 1) 载荷系数（design_rules: 中等工况 K_A=1.3~1.5，轻载1.3）
$K_A = 1.3
Write-Output "  工况系数 K_A = $K_A（中等冲击）"

# 2) 当量动载荷 P = K_A × (轴承当量载荷)
#    ★ 简化：设径向为主，取载荷系数 X=1, Y=1.4（球轴承，Fr/Fr > e）
#    为演示取径向载荷 Fr = 0.5 × 轴向载荷极限，按轴径初估
$Fr = 1200   # N，按轴径 φ30 估算的径向载荷
$Fa = 300    # N，轴向力
$X = 1.0; $Y = 1.4
$P_eq = [math]::Round($K_A * ($X*$Fr + $Y*$Fa), 1)
Write-Output "  径向载荷 Fr = $Fr N，轴向 Fa = $Fa N"
Write-Output "  当量动载荷 P = K_A·(X·Fr + Y·Fa) = $K_A·($X·$Fr + $Y·$Fa) = $P_eq N"

# 3) 由寿命反算所需动载荷（球轴承 ε=3）
$millions = $Lh * 60 * $n / 1e6
$eps = 3
$C_need = [math]::Round($P_eq * [math]::Pow($millions, 1/$eps), 1)
Write-Output "  寿命转数 = $Lh h × 60 × $n rpm = $([math]::Round($millions*1e6/1e6,1))×10^6 转"
Write-Output "  球轴承 ε=3 ⇒ C_需 = P × (寿命/10^6)^(1/3) = $P_eq × $([math]::Round($millions,2))^(1/3) = $C_need N = $([math]::Round($C_need/1000,2)) kN"

# 4) 查表选型
Write-Output ""
Write-Output "════ 查表选型（C ≥ $C_need N 且 n_lim ≥ $n）════"
$pick = @()
for ($i = 1; $i -lt $L.Count; $i++) {
    try { $b = Parse $L[$i] } catch { continue }
    if ($b.C -ge $C_need -and $b.nLim -ge $n) { $pick += $b }
}
$pick = $pick | Sort-Object d
if ($pick.Count -eq 0) {
    Write-Output "  ⚠ 表中无满足的型号（表内主要是小规格 M3~M5，功率偏大）"
    # 退而求其次：列出承载最接近的
    $all = @(); for ($i=1;$i -lt $L.Count;$i++){ try { $all += Parse $L[$i] } catch {} }
    $all | Sort-Object { [math]::Abs($_.C - $C_need) } | Select-Object -First 3 |
      ForEach-Object { Write-Output "     最近: $($_.Desig)  d=$($_.d) C=$($_.C)kN  差 $([math]::Round($_.C*1000-$C_need,0))N" }
} else {
    Write-Output "  满足条件的型号 $($pick.Count) 个（按内径排序，前 6 个）:"
    $pick | Select-Object -First 6 | ForEach-Object {
        Write-Output ("     {0,-10} d={1,4} D={2,4} B={3,4}  C={4,6}N  n_lim={5,7}  轴肩da={6,5}  ra={7}" -f `
            $_.Desig, $_.d, $_.D, $_.B, ($_.C*1000), $_.nLim, $_.da, $_.ra)
    }
    $best = $pick | Select-Object -First 1
    Write-Output ""
    Write-Output "════ 校核 ════"
    Write-Output "  选用 $($best.Desig)：C=$($best.C)kN / 需 $C_need N ⇒ 实际富余 $([math]::Round($best.C*1000-$C_need,0))N"
    $lifeChk = [math]::Round(($best.C*1000/$P_eq) * 3 * 1e6 / (60*$n) / 1e6, 2)
    Write-Output "  反算寿命 L10h = (C/P)³·10⁶/(60n) = $lifeChk 万小时（要求 $Lh h）"
    Write-Output "  转速校核：n_lim=$($best.nLim) ≥ $n ⇒ $(if($best.nLim -ge $n){'✅'}else{'❌'})"
}

# 5) 配合：按知识库 fits_iso286，φ30 的 H7/k6
Write-Output ""
Write-Output "════ 配合校核（fits_iso286.yaml，24~30 段）════"
$holeES = 21.0; $holeEI = 0.0     # H7
$axEs = 15.0;  $axEi = 2.0       # k6
$Xmax = $holeES - $axEi
$Xmin = $holeEI - $axEs
Write-Output "  H7 孔 (24~30): ES=+$holeES EI=$holeEI"
Write-Output "  k6 轴 (24~30): es=+$axEs ei=+$axEi"
Write-Output "  ⇒ Xmax = ES孔 − ei轴 = $Xmax μm（最大间隙）"
Write-Output "  ⇒ Xmin = EI孔 − es轴 = $Xmin μm（最大过盈）"
Write-Output "  ⇒ 过渡配合，过盈约 $([math]::Abs($Xmin)) μm = $([math]::Abs($Xmin)/1000) mm"
Write-Output "  ⇒ $(if($Xmin -lt 0){'✅ 轻中载旋转内圈：有过盈但小，便于装拆'}else{'⚠ 无过盈，是间隙配合'})"
.bore) C=$($_.C)kN  差 $([math]::Round($_.C*1000-$C_need,0))N" }
} else {
    Write-Output "  满足条件的型号 $($pick.Count) 个（按内径排序，前 6 个）:"
    $pick | Select-Object -First 6 | ForEach-Object {
        Write-Output ("     {0,-10} d={1,4} D={2,4} B={3,4}  C={4,6}N  n_lim={5,7}  轴肩da={6,5}  ra={7}" -f `
            $_.Desig, # ★ 闭环验证：用轴承库 + 配合库 + 材料库 做一次真实选型
# 题目：设计一根传动轴，传递 P=2.2kW, n=1450 rpm，要求寿命 L10h=10000h
# 判据自检：算出的 C/C比 是否符合工程常识；选的型号是否真的在表里、n_lim 是否够

$csv = "C:\Users\Zegel\solidpilot-mcp\知识库\bearings\single_row_deep_groove_ball_bearing_parameters.csv"
$L = @(Get-Content $csv | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })

# 列位置（已验证）：1=d 2=D 3=B 4=C 5=C0 6=Pu 7=n_ref 8=n_lim 9=mass 10=Designation 15=da 17=ra
function Parse($line) {
    $r = $line.Split(',')
    [pscustomobject]@{
        bore = [double]$r[1]; shell = [double]$r[2]; wid = [double]$r[3]
        C  = [double]$r[4];  C0 = [double]$r[5];  Pu = [double]$r[6]
        nRef = [double]$r[7]; nLim = [double]$r[8]; mass = [double]$r[9]
        Desig = $r[10].Trim(); da = $r[15].Trim(); ra = $r[17].Trim()
    }
}

Write-Output "════ 工况 ════"
$P = 2.2; $n = 1450; $Lh = 10000
Write-Output "  功率 P = $P kW，转速 n = $n rpm，要求寿命 L10h = $Lh h"
# 1) 载荷系数（design_rules: 中等工况 K_A=1.3~1.5，轻载1.3）
$K_A = 1.3
Write-Output "  工况系数 K_A = $K_A（中等冲击）"

# 2) 当量动载荷 P = K_A × (轴承当量载荷)
#    ★ 简化：设径向为主，取载荷系数 X=1, Y=1.4（球轴承，Fr/Fr > e）
#    为演示取径向载荷 Fr = 0.5 × 轴向载荷极限，按轴径初估
$Fr = 1200   # N，按轴径 φ30 估算的径向载荷
$Fa = 300    # N，轴向力
$X = 1.0; $Y = 1.4
$P_eq = [math]::Round($K_A * ($X*$Fr + $Y*$Fa), 1)
Write-Output "  径向载荷 Fr = $Fr N，轴向 Fa = $Fa N"
Write-Output "  当量动载荷 P = K_A·(X·Fr + Y·Fa) = $K_A·($X·$Fr + $Y·$Fa) = $P_eq N"

# 3) 由寿命反算所需动载荷（球轴承 ε=3）
$millions = $Lh * 60 * $n / 1e6
$eps = 3
$C_need = [math]::Round($P_eq * [math]::Pow($millions, 1/$eps), 1)
Write-Output "  寿命转数 = $Lh h × 60 × $n rpm = $([math]::Round($millions*1e6/1e6,1))×10^6 转"
Write-Output "  球轴承 ε=3 ⇒ C_需 = P × (寿命/10^6)^(1/3) = $P_eq × $([math]::Round($millions,2))^(1/3) = $C_need N = $([math]::Round($C_need/1000,2)) kN"

# 4) 查表选型
Write-Output ""
Write-Output "════ 查表选型（C ≥ $C_need N 且 n_lim ≥ $n）════"
$pick = @()
for ($i = 1; $i -lt $L.Count; $i++) {
    try { $b = Parse $L[$i] } catch { continue }
    if ($b.C -ge $C_need -and $b.nLim -ge $n) { $pick += $b }
}
$pick = $pick | Sort-Object d
if ($pick.Count -eq 0) {
    Write-Output "  ⚠ 表中无满足的型号（表内主要是小规格 M3~M5，功率偏大）"
    # 退而求其次：列出承载最接近的
    $all = @(); for ($i=1;$i -lt $L.Count;$i++){ try { $all += Parse $L[$i] } catch {} }
    $all | Sort-Object { [math]::Abs($_.C - $C_need) } | Select-Object -First 3 |
      ForEach-Object { Write-Output "     最近: $($_.Desig)  d=$($_.d) C=$($_.C)kN  差 $([math]::Round($_.C*1000-$C_need,0))N" }
} else {
    Write-Output "  满足条件的型号 $($pick.Count) 个（按内径排序，前 6 个）:"
    $pick | Select-Object -First 6 | ForEach-Object {
        Write-Output ("     {0,-10} d={1,4} D={2,4} B={3,4}  C={4,6}N  n_lim={5,7}  轴肩da={6,5}  ra={7}" -f `
            $_.Desig, $_.d, $_.D, $_.B, ($_.C*1000), $_.nLim, $_.da, $_.ra)
    }
    $best = $pick | Select-Object -First 1
    Write-Output ""
    Write-Output "════ 校核 ════"
    Write-Output "  选用 $($best.Desig)：C=$($best.C)kN / 需 $C_need N ⇒ 实际富余 $([math]::Round($best.C*1000-$C_need,0))N"
    $lifeChk = [math]::Round(($best.C*1000/$P_eq) * 3 * 1e6 / (60*$n) / 1e6, 2)
    Write-Output "  反算寿命 L10h = (C/P)³·10⁶/(60n) = $lifeChk 万小时（要求 $Lh h）"
    Write-Output "  转速校核：n_lim=$($best.nLim) ≥ $n ⇒ $(if($best.nLim -ge $n){'✅'}else{'❌'})"
}

# 5) 配合：按知识库 fits_iso286，φ30 的 H7/k6
Write-Output ""
Write-Output "════ 配合校核（fits_iso286.yaml，24~30 段）════"
$holeES = 21.0; $holeEI = 0.0     # H7
$axEs = 15.0;  $axEi = 2.0       # k6
$Xmax = $holeES - $axEi
$Xmin = $holeEI - $axEs
Write-Output "  H7 孔 (24~30): ES=+$holeES EI=$holeEI"
Write-Output "  k6 轴 (24~30): es=+$axEs ei=+$axEi"
Write-Output "  ⇒ Xmax = ES孔 − ei轴 = $Xmax μm（最大间隙）"
Write-Output "  ⇒ Xmin = EI孔 − es轴 = $Xmin μm（最大过盈）"
Write-Output "  ⇒ 过渡配合，过盈约 $([math]::Abs($Xmin)) μm = $([math]::Abs($Xmin)/1000) mm"
Write-Output "  ⇒ $(if($Xmin -lt 0){'✅ 轻中载旋转内圈：有过盈但小，便于装拆'}else{'⚠ 无过盈，是间隙配合'})"
.bore, # ★ 闭环验证：用轴承库 + 配合库 + 材料库 做一次真实选型
# 题目：设计一根传动轴，传递 P=2.2kW, n=1450 rpm，要求寿命 L10h=10000h
# 判据自检：算出的 C/C比 是否符合工程常识；选的型号是否真的在表里、n_lim 是否够

$csv = "C:\Users\Zegel\solidpilot-mcp\知识库\bearings\single_row_deep_groove_ball_bearing_parameters.csv"
$L = @(Get-Content $csv | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })

# 列位置（已验证）：1=d 2=D 3=B 4=C 5=C0 6=Pu 7=n_ref 8=n_lim 9=mass 10=Designation 15=da 17=ra
function Parse($line) {
    $r = $line.Split(',')
    [pscustomobject]@{
        bore = [double]$r[1]; shell = [double]$r[2]; wid = [double]$r[3]
        C  = [double]$r[4];  C0 = [double]$r[5];  Pu = [double]$r[6]
        nRef = [double]$r[7]; nLim = [double]$r[8]; mass = [double]$r[9]
        Desig = $r[10].Trim(); da = $r[15].Trim(); ra = $r[17].Trim()
    }
}

Write-Output "════ 工况 ════"
$P = 2.2; $n = 1450; $Lh = 10000
Write-Output "  功率 P = $P kW，转速 n = $n rpm，要求寿命 L10h = $Lh h"
# 1) 载荷系数（design_rules: 中等工况 K_A=1.3~1.5，轻载1.3）
$K_A = 1.3
Write-Output "  工况系数 K_A = $K_A（中等冲击）"

# 2) 当量动载荷 P = K_A × (轴承当量载荷)
#    ★ 简化：设径向为主，取载荷系数 X=1, Y=1.4（球轴承，Fr/Fr > e）
#    为演示取径向载荷 Fr = 0.5 × 轴向载荷极限，按轴径初估
$Fr = 1200   # N，按轴径 φ30 估算的径向载荷
$Fa = 300    # N，轴向力
$X = 1.0; $Y = 1.4
$P_eq = [math]::Round($K_A * ($X*$Fr + $Y*$Fa), 1)
Write-Output "  径向载荷 Fr = $Fr N，轴向 Fa = $Fa N"
Write-Output "  当量动载荷 P = K_A·(X·Fr + Y·Fa) = $K_A·($X·$Fr + $Y·$Fa) = $P_eq N"

# 3) 由寿命反算所需动载荷（球轴承 ε=3）
$millions = $Lh * 60 * $n / 1e6
$eps = 3
$C_need = [math]::Round($P_eq * [math]::Pow($millions, 1/$eps), 1)
Write-Output "  寿命转数 = $Lh h × 60 × $n rpm = $([math]::Round($millions*1e6/1e6,1))×10^6 转"
Write-Output "  球轴承 ε=3 ⇒ C_需 = P × (寿命/10^6)^(1/3) = $P_eq × $([math]::Round($millions,2))^(1/3) = $C_need N = $([math]::Round($C_need/1000,2)) kN"

# 4) 查表选型
Write-Output ""
Write-Output "════ 查表选型（C ≥ $C_need N 且 n_lim ≥ $n）════"
$pick = @()
for ($i = 1; $i -lt $L.Count; $i++) {
    try { $b = Parse $L[$i] } catch { continue }
    if ($b.C -ge $C_need -and $b.nLim -ge $n) { $pick += $b }
}
$pick = $pick | Sort-Object d
if ($pick.Count -eq 0) {
    Write-Output "  ⚠ 表中无满足的型号（表内主要是小规格 M3~M5，功率偏大）"
    # 退而求其次：列出承载最接近的
    $all = @(); for ($i=1;$i -lt $L.Count;$i++){ try { $all += Parse $L[$i] } catch {} }
    $all | Sort-Object { [math]::Abs($_.C - $C_need) } | Select-Object -First 3 |
      ForEach-Object { Write-Output "     最近: $($_.Desig)  d=$($_.d) C=$($_.C)kN  差 $([math]::Round($_.C*1000-$C_need,0))N" }
} else {
    Write-Output "  满足条件的型号 $($pick.Count) 个（按内径排序，前 6 个）:"
    $pick | Select-Object -First 6 | ForEach-Object {
        Write-Output ("     {0,-10} d={1,4} D={2,4} B={3,4}  C={4,6}N  n_lim={5,7}  轴肩da={6,5}  ra={7}" -f `
            $_.Desig, $_.d, $_.D, $_.B, ($_.C*1000), $_.nLim, $_.da, $_.ra)
    }
    $best = $pick | Select-Object -First 1
    Write-Output ""
    Write-Output "════ 校核 ════"
    Write-Output "  选用 $($best.Desig)：C=$($best.C)kN / 需 $C_need N ⇒ 实际富余 $([math]::Round($best.C*1000-$C_need,0))N"
    $lifeChk = [math]::Round(($best.C*1000/$P_eq) * 3 * 1e6 / (60*$n) / 1e6, 2)
    Write-Output "  反算寿命 L10h = (C/P)³·10⁶/(60n) = $lifeChk 万小时（要求 $Lh h）"
    Write-Output "  转速校核：n_lim=$($best.nLim) ≥ $n ⇒ $(if($best.nLim -ge $n){'✅'}else{'❌'})"
}

# 5) 配合：按知识库 fits_iso286，φ30 的 H7/k6
Write-Output ""
Write-Output "════ 配合校核（fits_iso286.yaml，24~30 段）════"
$holeES = 21.0; $holeEI = 0.0     # H7
$axEs = 15.0;  $axEi = 2.0       # k6
$Xmax = $holeES - $axEi
$Xmin = $holeEI - $axEs
Write-Output "  H7 孔 (24~30): ES=+$holeES EI=$holeEI"
Write-Output "  k6 轴 (24~30): es=+$axEs ei=+$axEi"
Write-Output "  ⇒ Xmax = ES孔 − ei轴 = $Xmax μm（最大间隙）"
Write-Output "  ⇒ Xmin = EI孔 − es轴 = $Xmin μm（最大过盈）"
Write-Output "  ⇒ 过渡配合，过盈约 $([math]::Abs($Xmin)) μm = $([math]::Abs($Xmin)/1000) mm"
Write-Output "  ⇒ $(if($Xmin -lt 0){'✅ 轻中载旋转内圈：有过盈但小，便于装拆'}else{'⚠ 无过盈，是间隙配合'})"
.bore, $_.B, ($_.C*1000), $_.nLim, $_.da, $_.ra)
    }
    $best = $pick | Select-Object -First 1
    Write-Output ""
    Write-Output "════ 校核 ════"
    Write-Output "  选用 $($best.Desig)：C=$($best.C)kN / 需 $C_need N ⇒ 实际富余 $([math]::Round($best.C*1000-$C_need,0))N"
    $lifeChk = [math]::Round(($best.C*1000/$P_eq) * 3 * 1e6 / (60*$n) / 1e6, 2)
    Write-Output "  反算寿命 L10h = (C/P)³·10⁶/(60n) = $lifeChk 万小时（要求 $Lh h）"
    Write-Output "  转速校核：n_lim=$($best.nLim) ≥ $n ⇒ $(if($best.nLim -ge $n){'✅'}else{'❌'})"
}

# 5) 配合：按知识库 fits_iso286，φ30 的 H7/k6
Write-Output ""
Write-Output "════ 配合校核（fits_iso286.yaml，24~30 段）════"
$holeES = 21.0; $holeEI = 0.0     # H7
$axEs = 15.0;  $axEi = 2.0       # k6
$Xmax = $holeES - $axEi
$Xmin = $holeEI - $axEs
Write-Output "  H7 孔 (24~30): ES=+$holeES EI=$holeEI"
Write-Output "  k6 轴 (24~30): es=+$axEs ei=+$axEi"
Write-Output "  ⇒ Xmax = ES孔 − ei轴 = $Xmax μm（最大间隙）"
Write-Output "  ⇒ Xmin = EI孔 − es轴 = $Xmin μm（最大过盈）"
Write-Output "  ⇒ 过渡配合，过盈约 $([math]::Abs($Xmin)) μm = $([math]::Abs($Xmin)/1000) mm"
Write-Output "  ⇒ $(if($Xmin -lt 0){'✅ 轻中载旋转内圈：有过盈但小，便于装拆'}else{'⚠ 无过盈，是间隙配合'})"
.shell, # ★ 闭环验证：用轴承库 + 配合库 + 材料库 做一次真实选型
# 题目：设计一根传动轴，传递 P=2.2kW, n=1450 rpm，要求寿命 L10h=10000h
# 判据自检：算出的 C/C比 是否符合工程常识；选的型号是否真的在表里、n_lim 是否够

$csv = "C:\Users\Zegel\solidpilot-mcp\知识库\bearings\single_row_deep_groove_ball_bearing_parameters.csv"
$L = @(Get-Content $csv | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })

# 列位置（已验证）：1=d 2=D 3=B 4=C 5=C0 6=Pu 7=n_ref 8=n_lim 9=mass 10=Designation 15=da 17=ra
function Parse($line) {
    $r = $line.Split(',')
    [pscustomobject]@{
        bore = [double]$r[1]; shell = [double]$r[2]; wid = [double]$r[3]
        C  = [double]$r[4];  C0 = [double]$r[5];  Pu = [double]$r[6]
        nRef = [double]$r[7]; nLim = [double]$r[8]; mass = [double]$r[9]
        Desig = $r[10].Trim(); da = $r[15].Trim(); ra = $r[17].Trim()
    }
}

Write-Output "════ 工况 ════"
$P = 2.2; $n = 1450; $Lh = 10000
Write-Output "  功率 P = $P kW，转速 n = $n rpm，要求寿命 L10h = $Lh h"
# 1) 载荷系数（design_rules: 中等工况 K_A=1.3~1.5，轻载1.3）
$K_A = 1.3
Write-Output "  工况系数 K_A = $K_A（中等冲击）"

# 2) 当量动载荷 P = K_A × (轴承当量载荷)
#    ★ 简化：设径向为主，取载荷系数 X=1, Y=1.4（球轴承，Fr/Fr > e）
#    为演示取径向载荷 Fr = 0.5 × 轴向载荷极限，按轴径初估
$Fr = 1200   # N，按轴径 φ30 估算的径向载荷
$Fa = 300    # N，轴向力
$X = 1.0; $Y = 1.4
$P_eq = [math]::Round($K_A * ($X*$Fr + $Y*$Fa), 1)
Write-Output "  径向载荷 Fr = $Fr N，轴向 Fa = $Fa N"
Write-Output "  当量动载荷 P = K_A·(X·Fr + Y·Fa) = $K_A·($X·$Fr + $Y·$Fa) = $P_eq N"

# 3) 由寿命反算所需动载荷（球轴承 ε=3）
$millions = $Lh * 60 * $n / 1e6
$eps = 3
$C_need = [math]::Round($P_eq * [math]::Pow($millions, 1/$eps), 1)
Write-Output "  寿命转数 = $Lh h × 60 × $n rpm = $([math]::Round($millions*1e6/1e6,1))×10^6 转"
Write-Output "  球轴承 ε=3 ⇒ C_需 = P × (寿命/10^6)^(1/3) = $P_eq × $([math]::Round($millions,2))^(1/3) = $C_need N = $([math]::Round($C_need/1000,2)) kN"

# 4) 查表选型
Write-Output ""
Write-Output "════ 查表选型（C ≥ $C_need N 且 n_lim ≥ $n）════"
$pick = @()
for ($i = 1; $i -lt $L.Count; $i++) {
    try { $b = Parse $L[$i] } catch { continue }
    if ($b.C -ge $C_need -and $b.nLim -ge $n) { $pick += $b }
}
$pick = $pick | Sort-Object d
if ($pick.Count -eq 0) {
    Write-Output "  ⚠ 表中无满足的型号（表内主要是小规格 M3~M5，功率偏大）"
    # 退而求其次：列出承载最接近的
    $all = @(); for ($i=1;$i -lt $L.Count;$i++){ try { $all += Parse $L[$i] } catch {} }
    $all | Sort-Object { [math]::Abs($_.C - $C_need) } | Select-Object -First 3 |
      ForEach-Object { Write-Output "     最近: $($_.Desig)  d=$(# ★ 闭环验证：用轴承库 + 配合库 + 材料库 做一次真实选型
# 题目：设计一根传动轴，传递 P=2.2kW, n=1450 rpm，要求寿命 L10h=10000h
# 判据自检：算出的 C/C比 是否符合工程常识；选的型号是否真的在表里、n_lim 是否够

$csv = "C:\Users\Zegel\solidpilot-mcp\知识库\bearings\single_row_deep_groove_ball_bearing_parameters.csv"
$L = @(Get-Content $csv | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })

# 列位置（已验证）：1=d 2=D 3=B 4=C 5=C0 6=Pu 7=n_ref 8=n_lim 9=mass 10=Designation 15=da 17=ra
function Parse($line) {
    $r = $line.Split(',')
    [pscustomobject]@{
        bore = [double]$r[1]; shell = [double]$r[2]; wid = [double]$r[3]
        C  = [double]$r[4];  C0 = [double]$r[5];  Pu = [double]$r[6]
        nRef = [double]$r[7]; nLim = [double]$r[8]; mass = [double]$r[9]
        Desig = $r[10].Trim(); da = $r[15].Trim(); ra = $r[17].Trim()
    }
}

Write-Output "════ 工况 ════"
$P = 2.2; $n = 1450; $Lh = 10000
Write-Output "  功率 P = $P kW，转速 n = $n rpm，要求寿命 L10h = $Lh h"
# 1) 载荷系数（design_rules: 中等工况 K_A=1.3~1.5，轻载1.3）
$K_A = 1.3
Write-Output "  工况系数 K_A = $K_A（中等冲击）"

# 2) 当量动载荷 P = K_A × (轴承当量载荷)
#    ★ 简化：设径向为主，取载荷系数 X=1, Y=1.4（球轴承，Fr/Fr > e）
#    为演示取径向载荷 Fr = 0.5 × 轴向载荷极限，按轴径初估
$Fr = 1200   # N，按轴径 φ30 估算的径向载荷
$Fa = 300    # N，轴向力
$X = 1.0; $Y = 1.4
$P_eq = [math]::Round($K_A * ($X*$Fr + $Y*$Fa), 1)
Write-Output "  径向载荷 Fr = $Fr N，轴向 Fa = $Fa N"
Write-Output "  当量动载荷 P = K_A·(X·Fr + Y·Fa) = $K_A·($X·$Fr + $Y·$Fa) = $P_eq N"

# 3) 由寿命反算所需动载荷（球轴承 ε=3）
$millions = $Lh * 60 * $n / 1e6
$eps = 3
$C_need = [math]::Round($P_eq * [math]::Pow($millions, 1/$eps), 1)
Write-Output "  寿命转数 = $Lh h × 60 × $n rpm = $([math]::Round($millions*1e6/1e6,1))×10^6 转"
Write-Output "  球轴承 ε=3 ⇒ C_需 = P × (寿命/10^6)^(1/3) = $P_eq × $([math]::Round($millions,2))^(1/3) = $C_need N = $([math]::Round($C_need/1000,2)) kN"

# 4) 查表选型
Write-Output ""
Write-Output "════ 查表选型（C ≥ $C_need N 且 n_lim ≥ $n）════"
$pick = @()
for ($i = 1; $i -lt $L.Count; $i++) {
    try { $b = Parse $L[$i] } catch { continue }
    if ($b.C -ge $C_need -and $b.nLim -ge $n) { $pick += $b }
}
$pick = $pick | Sort-Object d
if ($pick.Count -eq 0) {
    Write-Output "  ⚠ 表中无满足的型号（表内主要是小规格 M3~M5，功率偏大）"
    # 退而求其次：列出承载最接近的
    $all = @(); for ($i=1;$i -lt $L.Count;$i++){ try { $all += Parse $L[$i] } catch {} }
    $all | Sort-Object { [math]::Abs($_.C - $C_need) } | Select-Object -First 3 |
      ForEach-Object { Write-Output "     最近: $($_.Desig)  d=$($_.d) C=$($_.C)kN  差 $([math]::Round($_.C*1000-$C_need,0))N" }
} else {
    Write-Output "  满足条件的型号 $($pick.Count) 个（按内径排序，前 6 个）:"
    $pick | Select-Object -First 6 | ForEach-Object {
        Write-Output ("     {0,-10} d={1,4} D={2,4} B={3,4}  C={4,6}N  n_lim={5,7}  轴肩da={6,5}  ra={7}" -f `
            $_.Desig, $_.d, $_.D, $_.B, ($_.C*1000), $_.nLim, $_.da, $_.ra)
    }
    $best = $pick | Select-Object -First 1
    Write-Output ""
    Write-Output "════ 校核 ════"
    Write-Output "  选用 $($best.Desig)：C=$($best.C)kN / 需 $C_need N ⇒ 实际富余 $([math]::Round($best.C*1000-$C_need,0))N"
    $lifeChk = [math]::Round(($best.C*1000/$P_eq) * 3 * 1e6 / (60*$n) / 1e6, 2)
    Write-Output "  反算寿命 L10h = (C/P)³·10⁶/(60n) = $lifeChk 万小时（要求 $Lh h）"
    Write-Output "  转速校核：n_lim=$($best.nLim) ≥ $n ⇒ $(if($best.nLim -ge $n){'✅'}else{'❌'})"
}

# 5) 配合：按知识库 fits_iso286，φ30 的 H7/k6
Write-Output ""
Write-Output "════ 配合校核（fits_iso286.yaml，24~30 段）════"
$holeES = 21.0; $holeEI = 0.0     # H7
$axEs = 15.0;  $axEi = 2.0       # k6
$Xmax = $holeES - $axEi
$Xmin = $holeEI - $axEs
Write-Output "  H7 孔 (24~30): ES=+$holeES EI=$holeEI"
Write-Output "  k6 轴 (24~30): es=+$axEs ei=+$axEi"
Write-Output "  ⇒ Xmax = ES孔 − ei轴 = $Xmax μm（最大间隙）"
Write-Output "  ⇒ Xmin = EI孔 − es轴 = $Xmin μm（最大过盈）"
Write-Output "  ⇒ 过渡配合，过盈约 $([math]::Abs($Xmin)) μm = $([math]::Abs($Xmin)/1000) mm"
Write-Output "  ⇒ $(if($Xmin -lt 0){'✅ 轻中载旋转内圈：有过盈但小，便于装拆'}else{'⚠ 无过盈，是间隙配合'})"
.bore) C=$($_.C)kN  差 $([math]::Round($_.C*1000-$C_need,0))N" }
} else {
    Write-Output "  满足条件的型号 $($pick.Count) 个（按内径排序，前 6 个）:"
    $pick | Select-Object -First 6 | ForEach-Object {
        Write-Output ("     {0,-10} d={1,4} D={2,4} B={3,4}  C={4,6}N  n_lim={5,7}  轴肩da={6,5}  ra={7}" -f `
            $_.Desig, # ★ 闭环验证：用轴承库 + 配合库 + 材料库 做一次真实选型
# 题目：设计一根传动轴，传递 P=2.2kW, n=1450 rpm，要求寿命 L10h=10000h
# 判据自检：算出的 C/C比 是否符合工程常识；选的型号是否真的在表里、n_lim 是否够

$csv = "C:\Users\Zegel\solidpilot-mcp\知识库\bearings\single_row_deep_groove_ball_bearing_parameters.csv"
$L = @(Get-Content $csv | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })

# 列位置（已验证）：1=d 2=D 3=B 4=C 5=C0 6=Pu 7=n_ref 8=n_lim 9=mass 10=Designation 15=da 17=ra
function Parse($line) {
    $r = $line.Split(',')
    [pscustomobject]@{
        bore = [double]$r[1]; shell = [double]$r[2]; wid = [double]$r[3]
        C  = [double]$r[4];  C0 = [double]$r[5];  Pu = [double]$r[6]
        nRef = [double]$r[7]; nLim = [double]$r[8]; mass = [double]$r[9]
        Desig = $r[10].Trim(); da = $r[15].Trim(); ra = $r[17].Trim()
    }
}

Write-Output "════ 工况 ════"
$P = 2.2; $n = 1450; $Lh = 10000
Write-Output "  功率 P = $P kW，转速 n = $n rpm，要求寿命 L10h = $Lh h"
# 1) 载荷系数（design_rules: 中等工况 K_A=1.3~1.5，轻载1.3）
$K_A = 1.3
Write-Output "  工况系数 K_A = $K_A（中等冲击）"

# 2) 当量动载荷 P = K_A × (轴承当量载荷)
#    ★ 简化：设径向为主，取载荷系数 X=1, Y=1.4（球轴承，Fr/Fr > e）
#    为演示取径向载荷 Fr = 0.5 × 轴向载荷极限，按轴径初估
$Fr = 1200   # N，按轴径 φ30 估算的径向载荷
$Fa = 300    # N，轴向力
$X = 1.0; $Y = 1.4
$P_eq = [math]::Round($K_A * ($X*$Fr + $Y*$Fa), 1)
Write-Output "  径向载荷 Fr = $Fr N，轴向 Fa = $Fa N"
Write-Output "  当量动载荷 P = K_A·(X·Fr + Y·Fa) = $K_A·($X·$Fr + $Y·$Fa) = $P_eq N"

# 3) 由寿命反算所需动载荷（球轴承 ε=3）
$millions = $Lh * 60 * $n / 1e6
$eps = 3
$C_need = [math]::Round($P_eq * [math]::Pow($millions, 1/$eps), 1)
Write-Output "  寿命转数 = $Lh h × 60 × $n rpm = $([math]::Round($millions*1e6/1e6,1))×10^6 转"
Write-Output "  球轴承 ε=3 ⇒ C_需 = P × (寿命/10^6)^(1/3) = $P_eq × $([math]::Round($millions,2))^(1/3) = $C_need N = $([math]::Round($C_need/1000,2)) kN"

# 4) 查表选型
Write-Output ""
Write-Output "════ 查表选型（C ≥ $C_need N 且 n_lim ≥ $n）════"
$pick = @()
for ($i = 1; $i -lt $L.Count; $i++) {
    try { $b = Parse $L[$i] } catch { continue }
    if ($b.C -ge $C_need -and $b.nLim -ge $n) { $pick += $b }
}
$pick = $pick | Sort-Object d
if ($pick.Count -eq 0) {
    Write-Output "  ⚠ 表中无满足的型号（表内主要是小规格 M3~M5，功率偏大）"
    # 退而求其次：列出承载最接近的
    $all = @(); for ($i=1;$i -lt $L.Count;$i++){ try { $all += Parse $L[$i] } catch {} }
    $all | Sort-Object { [math]::Abs($_.C - $C_need) } | Select-Object -First 3 |
      ForEach-Object { Write-Output "     最近: $($_.Desig)  d=$($_.d) C=$($_.C)kN  差 $([math]::Round($_.C*1000-$C_need,0))N" }
} else {
    Write-Output "  满足条件的型号 $($pick.Count) 个（按内径排序，前 6 个）:"
    $pick | Select-Object -First 6 | ForEach-Object {
        Write-Output ("     {0,-10} d={1,4} D={2,4} B={3,4}  C={4,6}N  n_lim={5,7}  轴肩da={6,5}  ra={7}" -f `
            $_.Desig, $_.d, $_.D, $_.B, ($_.C*1000), $_.nLim, $_.da, $_.ra)
    }
    $best = $pick | Select-Object -First 1
    Write-Output ""
    Write-Output "════ 校核 ════"
    Write-Output "  选用 $($best.Desig)：C=$($best.C)kN / 需 $C_need N ⇒ 实际富余 $([math]::Round($best.C*1000-$C_need,0))N"
    $lifeChk = [math]::Round(($best.C*1000/$P_eq) * 3 * 1e6 / (60*$n) / 1e6, 2)
    Write-Output "  反算寿命 L10h = (C/P)³·10⁶/(60n) = $lifeChk 万小时（要求 $Lh h）"
    Write-Output "  转速校核：n_lim=$($best.nLim) ≥ $n ⇒ $(if($best.nLim -ge $n){'✅'}else{'❌'})"
}

# 5) 配合：按知识库 fits_iso286，φ30 的 H7/k6
Write-Output ""
Write-Output "════ 配合校核（fits_iso286.yaml，24~30 段）════"
$holeES = 21.0; $holeEI = 0.0     # H7
$axEs = 15.0;  $axEi = 2.0       # k6
$Xmax = $holeES - $axEi
$Xmin = $holeEI - $axEs
Write-Output "  H7 孔 (24~30): ES=+$holeES EI=$holeEI"
Write-Output "  k6 轴 (24~30): es=+$axEs ei=+$axEi"
Write-Output "  ⇒ Xmax = ES孔 − ei轴 = $Xmax μm（最大间隙）"
Write-Output "  ⇒ Xmin = EI孔 − es轴 = $Xmin μm（最大过盈）"
Write-Output "  ⇒ 过渡配合，过盈约 $([math]::Abs($Xmin)) μm = $([math]::Abs($Xmin)/1000) mm"
Write-Output "  ⇒ $(if($Xmin -lt 0){'✅ 轻中载旋转内圈：有过盈但小，便于装拆'}else{'⚠ 无过盈，是间隙配合'})"
.bore, # ★ 闭环验证：用轴承库 + 配合库 + 材料库 做一次真实选型
# 题目：设计一根传动轴，传递 P=2.2kW, n=1450 rpm，要求寿命 L10h=10000h
# 判据自检：算出的 C/C比 是否符合工程常识；选的型号是否真的在表里、n_lim 是否够

$csv = "C:\Users\Zegel\solidpilot-mcp\知识库\bearings\single_row_deep_groove_ball_bearing_parameters.csv"
$L = @(Get-Content $csv | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })

# 列位置（已验证）：1=d 2=D 3=B 4=C 5=C0 6=Pu 7=n_ref 8=n_lim 9=mass 10=Designation 15=da 17=ra
function Parse($line) {
    $r = $line.Split(',')
    [pscustomobject]@{
        bore = [double]$r[1]; shell = [double]$r[2]; wid = [double]$r[3]
        C  = [double]$r[4];  C0 = [double]$r[5];  Pu = [double]$r[6]
        nRef = [double]$r[7]; nLim = [double]$r[8]; mass = [double]$r[9]
        Desig = $r[10].Trim(); da = $r[15].Trim(); ra = $r[17].Trim()
    }
}

Write-Output "════ 工况 ════"
$P = 2.2; $n = 1450; $Lh = 10000
Write-Output "  功率 P = $P kW，转速 n = $n rpm，要求寿命 L10h = $Lh h"
# 1) 载荷系数（design_rules: 中等工况 K_A=1.3~1.5，轻载1.3）
$K_A = 1.3
Write-Output "  工况系数 K_A = $K_A（中等冲击）"

# 2) 当量动载荷 P = K_A × (轴承当量载荷)
#    ★ 简化：设径向为主，取载荷系数 X=1, Y=1.4（球轴承，Fr/Fr > e）
#    为演示取径向载荷 Fr = 0.5 × 轴向载荷极限，按轴径初估
$Fr = 1200   # N，按轴径 φ30 估算的径向载荷
$Fa = 300    # N，轴向力
$X = 1.0; $Y = 1.4
$P_eq = [math]::Round($K_A * ($X*$Fr + $Y*$Fa), 1)
Write-Output "  径向载荷 Fr = $Fr N，轴向 Fa = $Fa N"
Write-Output "  当量动载荷 P = K_A·(X·Fr + Y·Fa) = $K_A·($X·$Fr + $Y·$Fa) = $P_eq N"

# 3) 由寿命反算所需动载荷（球轴承 ε=3）
$millions = $Lh * 60 * $n / 1e6
$eps = 3
$C_need = [math]::Round($P_eq * [math]::Pow($millions, 1/$eps), 1)
Write-Output "  寿命转数 = $Lh h × 60 × $n rpm = $([math]::Round($millions*1e6/1e6,1))×10^6 转"
Write-Output "  球轴承 ε=3 ⇒ C_需 = P × (寿命/10^6)^(1/3) = $P_eq × $([math]::Round($millions,2))^(1/3) = $C_need N = $([math]::Round($C_need/1000,2)) kN"

# 4) 查表选型
Write-Output ""
Write-Output "════ 查表选型（C ≥ $C_need N 且 n_lim ≥ $n）════"
$pick = @()
for ($i = 1; $i -lt $L.Count; $i++) {
    try { $b = Parse $L[$i] } catch { continue }
    if ($b.C -ge $C_need -and $b.nLim -ge $n) { $pick += $b }
}
$pick = $pick | Sort-Object d
if ($pick.Count -eq 0) {
    Write-Output "  ⚠ 表中无满足的型号（表内主要是小规格 M3~M5，功率偏大）"
    # 退而求其次：列出承载最接近的
    $all = @(); for ($i=1;$i -lt $L.Count;$i++){ try { $all += Parse $L[$i] } catch {} }
    $all | Sort-Object { [math]::Abs($_.C - $C_need) } | Select-Object -First 3 |
      ForEach-Object { Write-Output "     最近: $($_.Desig)  d=$($_.d) C=$($_.C)kN  差 $([math]::Round($_.C*1000-$C_need,0))N" }
} else {
    Write-Output "  满足条件的型号 $($pick.Count) 个（按内径排序，前 6 个）:"
    $pick | Select-Object -First 6 | ForEach-Object {
        Write-Output ("     {0,-10} d={1,4} D={2,4} B={3,4}  C={4,6}N  n_lim={5,7}  轴肩da={6,5}  ra={7}" -f `
            $_.Desig, $_.d, $_.D, $_.B, ($_.C*1000), $_.nLim, $_.da, $_.ra)
    }
    $best = $pick | Select-Object -First 1
    Write-Output ""
    Write-Output "════ 校核 ════"
    Write-Output "  选用 $($best.Desig)：C=$($best.C)kN / 需 $C_need N ⇒ 实际富余 $([math]::Round($best.C*1000-$C_need,0))N"
    $lifeChk = [math]::Round(($best.C*1000/$P_eq) * 3 * 1e6 / (60*$n) / 1e6, 2)
    Write-Output "  反算寿命 L10h = (C/P)³·10⁶/(60n) = $lifeChk 万小时（要求 $Lh h）"
    Write-Output "  转速校核：n_lim=$($best.nLim) ≥ $n ⇒ $(if($best.nLim -ge $n){'✅'}else{'❌'})"
}

# 5) 配合：按知识库 fits_iso286，φ30 的 H7/k6
Write-Output ""
Write-Output "════ 配合校核（fits_iso286.yaml，24~30 段）════"
$holeES = 21.0; $holeEI = 0.0     # H7
$axEs = 15.0;  $axEi = 2.0       # k6
$Xmax = $holeES - $axEi
$Xmin = $holeEI - $axEs
Write-Output "  H7 孔 (24~30): ES=+$holeES EI=$holeEI"
Write-Output "  k6 轴 (24~30): es=+$axEs ei=+$axEi"
Write-Output "  ⇒ Xmax = ES孔 − ei轴 = $Xmax μm（最大间隙）"
Write-Output "  ⇒ Xmin = EI孔 − es轴 = $Xmin μm（最大过盈）"
Write-Output "  ⇒ 过渡配合，过盈约 $([math]::Abs($Xmin)) μm = $([math]::Abs($Xmin)/1000) mm"
Write-Output "  ⇒ $(if($Xmin -lt 0){'✅ 轻中载旋转内圈：有过盈但小，便于装拆'}else{'⚠ 无过盈，是间隙配合'})"
.bore, $_.B, ($_.C*1000), $_.nLim, $_.da, $_.ra)
    }
    $best = $pick | Select-Object -First 1
    Write-Output ""
    Write-Output "════ 校核 ════"
    Write-Output "  选用 $($best.Desig)：C=$($best.C)kN / 需 $C_need N ⇒ 实际富余 $([math]::Round($best.C*1000-$C_need,0))N"
    $lifeChk = [math]::Round(($best.C*1000/$P_eq) * 3 * 1e6 / (60*$n) / 1e6, 2)
    Write-Output "  反算寿命 L10h = (C/P)³·10⁶/(60n) = $lifeChk 万小时（要求 $Lh h）"
    Write-Output "  转速校核：n_lim=$($best.nLim) ≥ $n ⇒ $(if($best.nLim -ge $n){'✅'}else{'❌'})"
}

# 5) 配合：按知识库 fits_iso286，φ30 的 H7/k6
Write-Output ""
Write-Output "════ 配合校核（fits_iso286.yaml，24~30 段）════"
$holeES = 21.0; $holeEI = 0.0     # H7
$axEs = 15.0;  $axEi = 2.0       # k6
$Xmax = $holeES - $axEi
$Xmin = $holeEI - $axEs
Write-Output "  H7 孔 (24~30): ES=+$holeES EI=$holeEI"
Write-Output "  k6 轴 (24~30): es=+$axEs ei=+$axEi"
Write-Output "  ⇒ Xmax = ES孔 − ei轴 = $Xmax μm（最大间隙）"
Write-Output "  ⇒ Xmin = EI孔 − es轴 = $Xmin μm（最大过盈）"
Write-Output "  ⇒ 过渡配合，过盈约 $([math]::Abs($Xmin)) μm = $([math]::Abs($Xmin)/1000) mm"
Write-Output "  ⇒ $(if($Xmin -lt 0){'✅ 轻中载旋转内圈：有过盈但小，便于装拆'}else{'⚠ 无过盈，是间隙配合'})"
.shell, $_.B, ($_.C*1000), $_.nLim, $_.da, $_.ra)
    }
    $best = $pick | Select-Object -First 1
    Write-Output ""
    Write-Output "════ 校核 ════"
    Write-Output "  选用 $($best.Desig)：C=$($best.C)kN / 需 $C_need N ⇒ 实际富余 $([math]::Round($best.C*1000-$C_need,0))N"
    $lifeChk = [math]::Round(($best.C*1000/$P_eq) * 3 * 1e6 / (60*$n) / 1e6, 2)
    Write-Output "  反算寿命 L10h = (C/P)³·10⁶/(60n) = $lifeChk 万小时（要求 $Lh h）"
    Write-Output "  转速校核：n_lim=$($best.nLim) ≥ $n ⇒ $(if($best.nLim -ge $n){'✅'}else{'❌'})"
}

# 5) 配合：按知识库 fits_iso286，φ30 的 H7/k6
Write-Output ""
Write-Output "════ 配合校核（fits_iso286.yaml，24~30 段）════"
$holeES = 21.0; $holeEI = 0.0     # H7
$axEs = 15.0;  $axEi = 2.0       # k6
$Xmax = $holeES - $axEi
$Xmin = $holeEI - $axEs
Write-Output "  H7 孔 (24~30): ES=+$holeES EI=$holeEI"
Write-Output "  k6 轴 (24~30): es=+$axEs ei=+$axEi"
Write-Output "  ⇒ Xmax = ES孔 − ei轴 = $Xmax μm（最大间隙）"
Write-Output "  ⇒ Xmin = EI孔 − es轴 = $Xmin μm（最大过盈）"
Write-Output "  ⇒ 过渡配合，过盈约 $([math]::Abs($Xmin)) μm = $([math]::Abs($Xmin)/1000) mm"
Write-Output "  ⇒ $(if($Xmin -lt 0){'✅ 轻中载旋转内圈：有过盈但小，便于装拆'}else{'⚠ 无过盈，是间隙配合'})"
.bore, $_.B, ($_.C*1000), $_.nLim, $_.da, $_.ra)
    }
    $best = $pick | Select-Object -First 1
    Write-Output ""
    Write-Output "════ 校核 ════"
    Write-Output "  选用 $($best.Desig)：C=$($best.C)kN / 需 $C_need N ⇒ 实际富余 $([math]::Round($best.C*1000-$C_need,0))N"
    $lifeChk = [math]::Round(($best.C*1000/$P_eq) * 3 * 1e6 / (60*$n) / 1e6, 2)
    Write-Output "  反算寿命 L10h = (C/P)³·10⁶/(60n) = $lifeChk 万小时（要求 $Lh h）"
    Write-Output "  转速校核：n_lim=$($best.nLim) ≥ $n ⇒ $(if($best.nLim -ge $n){'✅'}else{'❌'})"
}

# 5) 配合：按知识库 fits_iso286，φ30 的 H7/k6
Write-Output ""
Write-Output "════ 配合校核（fits_iso286.yaml，24~30 段）════"
$holeES = 21.0; $holeEI = 0.0     # H7
$axEs = 15.0;  $axEi = 2.0       # k6
$Xmax = $holeES - $axEi
$Xmin = $holeEI - $axEs
Write-Output "  H7 孔 (24~30): ES=+$holeES EI=$holeEI"
Write-Output "  k6 轴 (24~30): es=+$axEs ei=+$axEi"
Write-Output "  ⇒ Xmax = ES孔 − ei轴 = $Xmax μm（最大间隙）"
Write-Output "  ⇒ Xmin = EI孔 − es轴 = $Xmin μm（最大过盈）"
Write-Output "  ⇒ 过渡配合，过盈约 $([math]::Abs($Xmin)) μm = $([math]::Abs($Xmin)/1000) mm"
Write-Output "  ⇒ $(if($Xmin -lt 0){'✅ 轻中载旋转内圈：有过盈但小，便于装拆'}else{'⚠ 无过盈，是间隙配合'})"
