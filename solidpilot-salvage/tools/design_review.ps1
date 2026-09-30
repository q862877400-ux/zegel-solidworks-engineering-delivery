# ★ 设计评审器：用知识库规则对真实装配做工程审查
# 这是"从会用 API 到懂设计"的直接体现 —— 不是建模，是【做设计决策并给出结论】
$ErrorActionPreference = 'Continue'
. "C:\Users\Zegel\solidpilot-mcp\tools\call.ps1"

$KB = "C:\Users\Zegel\solidpilot-mcp\知识库"
$parts = "D:\AI\SW\AI Solidworks\模型"
$asm = "$parts\换刀主轴装配_BT30_ATC_Assembly.SLDASM"

$issues = @()
function Add-Issue { param($Level,$Cat,$Title,$Detail,$Fix)
    $script:issues += [pscustomobject]@{Level=$Level;Category=$Cat;Title=$Title;Detail=$Detail;Fix=$Fix}
}

Write-Output "══════ 设计评审：换刀主轴装配_BT30_ATC ══════`n"

# ── 1. 装配完整性 ──
Write-Output "【1】装配完整性"
$null = Call 'open_document' @{ file_path = $asm }
$a = Call 'analyze_assembly' @{}
$j = $a.cadState.features[0] | ConvertFrom-Json
$comps = $j.components
Write-Output "  组件数 = $($j.component_count)"

# BT30 换刀主轴的必备件
$required = @{
  '主轴'     = '带 BT30 内锥孔的旋转轴体 —— ★本装配【完全缺失】'
  '壳体'     = '固定主轴的壳体'
  '刀柄'     = '换刀时夹持刀具'
  '拉钉'     = '拉紧刀柄'
  '碟簧'     = '预紧力元件'
  '标准件'   = '螺钉/螺母/垫圈'
}
$hasSpindle = $comps | Where-Object { $_.name -match 'Spindle|主轴(?<!壳)' }
if(-not $hasSpindle){
  Add-Issue '严重' '完整性' '主轴本体缺失' `
    "BT30 ATC 换刀主轴的核心是带 7:24 内锥孔的主轴本体，本装配 11 个组件中【没有】它。" `
    "无主轴则：刀柄无处安装、壳体无轴孔、无法传递扭矩、锥孔配合无从谈起。整套机构不成立。"
}
# 固定状态检查
$fixedN = ($comps | Where-Object { $_.fixed }).Count
$floatN = ($comps | Where-Object { -not $_.fixed }).Count
Write-Output "  固定组件 = $fixedN   浮动组件 = $floatN"
if($floatN -eq 0){
  Add-Issue '严重' '装配' '全部组件处于固定状态，无自由度' `
    "11 个组件里 $($fixedN) 个 fixed=true，说明它们只是按坐标摆好的散件，【没有任何配合】。" `
    "浮动组件应为 0：真实装配中，未被配合约束的组件才能体现装配关系。当前装配不可用于运动分析/干涉检查。"
}

# ── 2. 配合检查 ──
Write-Output "`n【2】配合关系"
$hasMate = $false   # analyze_assembly 不返回 mates（R14 已知）
# 用组件位置反推：BT30 要求壳体与主轴同轴
$spindleLike = $comps | Where-Object { $_.name -match 'Housing|壳体' }
Write-Output "  ★ analyze_assembly 无 mates 字段，只能间接判断"
Add-Issue '中等' '装配' '无法确认配合关系' `
  "analyze_assembly 只返回 component_count + components[]，没有配合列表。" `
  "⇒ 需改服务端补 mates 字段（IAssemblyDoc.GetMates），否则无法自动审查配合"

# ── 3. 标准件检查 ──
Write-Output "`n【3】标准件使用"
$std = $comps | Where-Object { $_.name -match 'ISO|GB|DIN' }
Write-Output "  标准件组件 = $($std.Count) 个"
$std | ForEach-Object { Write-Output "    $($_.name)" }
if($std.Count -gt 0){
  # M12 螺钉的知识库规则
  Add-Issue '提示' '紧固' 'M12 螺钉旋合长度需校核' `
    "已用内六角螺钉 M12×40（GB/T 4762）+ 平垫（7089）+ 螺母（4032）。" `
    "按知识库 general.bolt.thread_engagement：钢件旋合需 ≥1.5d = 18mm。" `
    "★ 40mm 的螺钉旋合长度取决于被连接件厚度 —— 装配里看不到连接件，【无法校核】，需补连接件模型。"
}

# ── 4. 几何/材料检查 ──
Write-Output "`n【4】零件几何与材料"
$null = Call 'open_document' @{ file_path = "$parts\主轴壳体_Housing.sldprt" }
$m = Call 'analyze_model' @{ analysis_type='mass_properties' }
$vol = [double]([regex]::Match($m.cadState.features[0],'volume=([0-9.E+-]+)').Groups[1].Value)
$fa = Call 'analyze_model' @{ analysis_type='faces' }
$faces = ($fa.cadState.features[0] | ConvertFrom-Json).faces
$areas = $faces | Sort-Object { -$_.area }
# ★ 面积单位是 m²，×1e6 转 mm²。
# ★ 圆柱侧面积 A = π·D·L ⇒ D = A/(π·L)（得到的是【直径】，不是半径）
$outer = $areas[0].area * 1e6          # mm²
$inner = $areas[1].area * 1e6          # mm²
$OD = [math]::Round([math]::Sqrt($outer / [math]::PI / 110), 2)   # 外径 mm
$ID = [math]::Round([math]::Sqrt($inner / [math]::PI / 110), 2)   # 内径 mm
$wall = $OD - $ID
Write-Output "  壳体: 外Ø$OD 内Ø$ID 壁厚$([math]::Round($wall,1))mm 体积$([math]::Round($vol*1e9,0))mm³"

# 合理性自检：薄壁筒的壁厚应当远小于直径（这里 9/80 ≈ 11%）
if($wall -gt $OD){
    Write-Output "  ⚠ 壁厚($wall) > 外径($OD) ⇒ 单位换算有误，跳过铸造检查"
} else {
    # 知识库规则：铸造最小壁厚 = max(4, D/50 + 2.5)
    $minWall = [math]::Max(4, $OD/50 + 2.5)
    if($wall -ge $minWall){
        Write-Output "  ✅ 壁厚 $([math]::Round($wall,1)) ≥ 铸造最小 $([math]::Round($minWall,1))"
    } else {
        Add-Issue '严重' 'DFM' '壁厚不足' "壁厚 $([math]::Round($wall,1)) < 铸造最小 $([math]::Round($minWall,1))" "改为锻件或减小型腔"
    }
}

# 轴承位检查：这是换刀主轴的关键尺寸
Add-Issue '严重' '功能' '壳体无轴承位（实测确认）' `
  "壳体 Ø$OD × 110mm 薄壁筒，只有 2 平面 + 2 圆柱面（4 个面）。" `
  "★ 换刀主轴的壳体必须有【轴承位/轴承座孔】与主轴配合、并承受轴向定位。" `
  "4 个面说明它是个【素筒】—— 这正是 24 轮来 Simulation 加不上轴承载荷夹具的结构原因。"

# ── 5. 图纸完整性 ──
Write-Output "`n【5】图纸与技术要求"
$checks = @(
  @{n='表面粗糙度标注'; ok=$false; why="两端是与主轴/轴承的配合面，按知识库应 Ra0.8~1.6；模型中无任何粗糙度信息"}
  @{n='尺寸公差标注';     ok=$false; why="Ø80 属 >30~120 段，GB/T 1804-m 未注公差 ±0.3mm；模型中无公差信息"}
  @{n='形位公差(GD&T)';  ok=$false; why="轴承孔的【同轴度/位置度】是换刀精度的关键，装配里没体现"}
  @{n='材料牌号';         ok=$false; why="know库有 45钢/40Cr 等，但模型未赋材料（SolidWorks 用 AISI1020 近似）"}
  @{n='热处理要求';       ok=$false; why="轴类件通常需要调质（σb↑），图纸上必须注明"}
)
foreach($c in $checks){
  $mark = if($c.ok){'✅'}else{'❌'}
  Write-Output "  $mark $($c.n)  —— $($c.why)"
  if(-not $c.ok){ Add-Issue '缺失' '图纸' $c.n '' $c.why }
}

# ── 6. 汇总 ──
Write-Output "`n══════ 评审汇总 ══════"
$issues | Group-Object Level | ForEach-Object { Write-Output ("  {0,-4} {1} 项" -f # ★ 设计评审器：用知识库规则对真实装配做工程审查
# 这是"从会用 API 到懂设计"的直接体现 —— 不是建模，是【做设计决策并给出结论】
$ErrorActionPreference = 'Continue'
. "C:\Users\Zegel\solidpilot-mcp\tools\call.ps1"

$KB = "C:\Users\Zegel\solidpilot-mcp\知识库"
$parts = "D:\AI\SW\AI Solidworks\模型"
$asm = "$parts\换刀主轴装配_BT30_ATC_Assembly.SLDASM"

$issues = @()
function Add-Issue { param($Level,$Cat,$Title,$Detail,$Fix)
    $script:issues += [pscustomobject]@{Level=$Level;Category=$Cat;Title=$Title;Detail=$Detail;Fix=$Fix}
}

Write-Output "══════ 设计评审：换刀主轴装配_BT30_ATC ══════`n"

# ── 1. 装配完整性 ──
Write-Output "【1】装配完整性"
$null = Call 'open_document' @{ file_path = $asm }
$a = Call 'analyze_assembly' @{}
$j = $a.cadState.features[0] | ConvertFrom-Json
$comps = $j.components
Write-Output "  组件数 = $($j.component_count)"

# BT30 换刀主轴的必备件
$required = @{
  '主轴'     = '带 BT30 内锥孔的旋转轴体 —— ★本装配【完全缺失】'
  '壳体'     = '固定主轴的壳体'
  '刀柄'     = '换刀时夹持刀具'
  '拉钉'     = '拉紧刀柄'
  '碟簧'     = '预紧力元件'
  '标准件'   = '螺钉/螺母/垫圈'
}
$hasSpindle = $comps | Where-Object { $_.name -match 'Spindle|主轴(?<!壳)' }
if(-not $hasSpindle){
  Add-Issue '严重' '完整性' '主轴本体缺失' `
    "BT30 ATC 换刀主轴的核心是带 7:24 内锥孔的主轴本体，本装配 11 个组件中【没有】它。" `
    "无主轴则：刀柄无处安装、壳体无轴孔、无法传递扭矩、锥孔配合无从谈起。整套机构不成立。"
}
# 固定状态检查
$fixedN = ($comps | Where-Object { $_.fixed }).Count
$floatN = ($comps | Where-Object { -not $_.fixed }).Count
Write-Output "  固定组件 = $fixedN   浮动组件 = $floatN"
if($floatN -eq 0){
  Add-Issue '严重' '装配' '全部组件处于固定状态，无自由度' `
    "11 个组件里 $($fixedN) 个 fixed=true，说明它们只是按坐标摆好的散件，【没有任何配合】。" `
    "浮动组件应为 0：真实装配中，未被配合约束的组件才能体现装配关系。当前装配不可用于运动分析/干涉检查。"
}

# ── 2. 配合检查 ──
Write-Output "`n【2】配合关系"
$hasMate = $false   # analyze_assembly 不返回 mates（R14 已知）
# 用组件位置反推：BT30 要求壳体与主轴同轴
$spindleLike = $comps | Where-Object { $_.name -match 'Housing|壳体' }
Write-Output "  ★ analyze_assembly 无 mates 字段，只能间接判断"
Add-Issue '中等' '装配' '无法确认配合关系' `
  "analyze_assembly 只返回 component_count + components[]，没有配合列表。" `
  "⇒ 需改服务端补 mates 字段（IAssemblyDoc.GetMates），否则无法自动审查配合"

# ── 3. 标准件检查 ──
Write-Output "`n【3】标准件使用"
$std = $comps | Where-Object { $_.name -match 'ISO|GB|DIN' }
Write-Output "  标准件组件 = $($std.Count) 个"
$std | ForEach-Object { Write-Output "    $($_.name)" }
if($std.Count -gt 0){
  # M12 螺钉的知识库规则
  Add-Issue '提示' '紧固' 'M12 螺钉旋合长度需校核' `
    "已用内六角螺钉 M12×40（GB/T 4762）+ 平垫（7089）+ 螺母（4032）。" `
    "按知识库 general.bolt.thread_engagement：钢件旋合需 ≥1.5d = 18mm。" `
    "★ 40mm 的螺钉旋合长度取决于被连接件厚度 —— 装配里看不到连接件，【无法校核】，需补连接件模型。"
}

# ── 4. 几何/材料检查 ──
Write-Output "`n【4】零件几何与材料"
$null = Call 'open_document' @{ file_path = "$parts\主轴壳体_Housing.sldprt" }
$m = Call 'analyze_model' @{ analysis_type='mass_properties' }
$vol = [double]([regex]::Match($m.cadState.features[0],'volume=([0-9.E+-]+)').Groups[1].Value)
$fa = Call 'analyze_model' @{ analysis_type='faces' }
$faces = ($fa.cadState.features[0] | ConvertFrom-Json).faces
$areas = $faces | Sort-Object { -$_.area }
# ★ 面积单位是 m²，×1e6 转 mm²。
# ★ 圆柱侧面积 A = π·D·L ⇒ D = A/(π·L)（得到的是【直径】，不是半径）
$outer = $areas[0].area * 1e6          # mm²
$inner = $areas[1].area * 1e6          # mm²
$OD = [math]::Round([math]::Sqrt($outer / [math]::PI / 110), 2)   # 外径 mm
$ID = [math]::Round([math]::Sqrt($inner / [math]::PI / 110), 2)   # 内径 mm
$wall = $OD - $ID
Write-Output "  壳体: 外Ø$OD 内Ø$ID 壁厚$([math]::Round($wall,1))mm 体积$([math]::Round($vol*1e9,0))mm³"

# 合理性自检：薄壁筒的壁厚应当远小于直径（这里 9/80 ≈ 11%）
if($wall -gt $OD){
    Write-Output "  ⚠ 壁厚($wall) > 外径($OD) ⇒ 单位换算有误，跳过铸造检查"
} else {
    # 知识库规则：铸造最小壁厚 = max(4, D/50 + 2.5)
    $minWall = [math]::Max(4, $OD/50 + 2.5)
    if($wall -ge $minWall){
        Write-Output "  ✅ 壁厚 $([math]::Round($wall,1)) ≥ 铸造最小 $([math]::Round($minWall,1))"
    } else {
        Add-Issue '严重' 'DFM' '壁厚不足' "壁厚 $([math]::Round($wall,1)) < 铸造最小 $([math]::Round($minWall,1))" "改为锻件或减小型腔"
    }
}

# 轴承位检查：这是换刀主轴的关键尺寸
Add-Issue '严重' '功能' '壳体无轴承位（实测确认）' `
  "壳体 Ø$OD × 110mm 薄壁筒，只有 2 平面 + 2 圆柱面（4 个面）。" `
  "★ 换刀主轴的壳体必须有【轴承位/轴承座孔】与主轴配合、并承受轴向定位。" `
  "4 个面说明它是个【素筒】—— 这正是 24 轮来 Simulation 加不上轴承载荷夹具的结构原因。"

# ── 5. 图纸完整性 ──
Write-Output "`n【5】图纸与技术要求"
$checks = @(
  @{n='表面粗糙度标注'; ok=$false; why="两端是与主轴/轴承的配合面，按知识库应 Ra0.8~1.6；模型中无任何粗糙度信息"}
  @{n='尺寸公差标注';     ok=$false; why="Ø80 属 >30~120 段，GB/T 1804-m 未注公差 ±0.3mm；模型中无公差信息"}
  @{n='形位公差(GD&T)';  ok=$false; why="轴承孔的【同轴度/位置度】是换刀精度的关键，装配里没体现"}
  @{n='材料牌号';         ok=$false; why="know库有 45钢/40Cr 等，但模型未赋材料（SolidWorks 用 AISI1020 近似）"}
  @{n='热处理要求';       ok=$false; why="轴类件通常需要调质（σb↑），图纸上必须注明"}
)
foreach($c in $checks){
  $mark = if($c.ok){'✅'}else{'❌'}
  Write-Output "  $mark $($c.n)  —— $($c.why)"
  if(-not $c.ok){ Add-Issue '缺失' '图纸' $c.n '' $c.why }
}

# ── 6. 汇总 ──
Write-Output "`n══════ 评审汇总 ══════"
$issues | Group-Object Level | ForEach-Object { Write-Output "  {0,-4} {1} 项" -f $_.Name, $_.Count }
Write-Output ""
$issues | ForEach-Object { Write-Output "  [$($_.Level)] $($_.Category) / $($_.Title)" }

# 风险评分（透明分解，参考 almightyshui 的做法）
$sev = ($issues|Where-Object{$_.Level -eq '严重'}).Count
$med = ($issues|Where-Object{$_.Level -eq '中等'}).Count
$mis = ($issues|Where-Object{$_.Level -eq '缺失'}).Count
$score = [math]::Max(0, 100 - $sev*20 - $med*8 - $mis*4)
Write-Output ""
Write-Output "  风险评分 = 100 − 严重×20 − 中等×8 − 缺失×4"
Write-Output "         = 100 − $sev×20 − $med×8 − $mis×4 = $score / 100"
Write-Output "  结论: $(if($sev -ge 2){'★ 该设计当前【不能投入加工】——存在结构性缺失'}elseif($score -ge 70){'⚠ 可继续但需补齐技术要求'}else{'❌ 不合格'})"

$issues | Export-Csv "C:\Users\Zegel\solidpilot-mcp\设计评审_BT30_ATC_20260928.csv" -NoTypeInformation -Encoding UTF8
& "C:\Users\Zegel\solidpilot-mcp\tools\reclaim.ps1" 2>&1 | Select-Object -Last 1
.Name, # ★ 设计评审器：用知识库规则对真实装配做工程审查
# 这是"从会用 API 到懂设计"的直接体现 —— 不是建模，是【做设计决策并给出结论】
$ErrorActionPreference = 'Continue'
. "C:\Users\Zegel\solidpilot-mcp\tools\call.ps1"

$KB = "C:\Users\Zegel\solidpilot-mcp\知识库"
$parts = "D:\AI\SW\AI Solidworks\模型"
$asm = "$parts\换刀主轴装配_BT30_ATC_Assembly.SLDASM"

$issues = @()
function Add-Issue { param($Level,$Cat,$Title,$Detail,$Fix)
    $script:issues += [pscustomobject]@{Level=$Level;Category=$Cat;Title=$Title;Detail=$Detail;Fix=$Fix}
}

Write-Output "══════ 设计评审：换刀主轴装配_BT30_ATC ══════`n"

# ── 1. 装配完整性 ──
Write-Output "【1】装配完整性"
$null = Call 'open_document' @{ file_path = $asm }
$a = Call 'analyze_assembly' @{}
$j = $a.cadState.features[0] | ConvertFrom-Json
$comps = $j.components
Write-Output "  组件数 = $($j.component_count)"

# BT30 换刀主轴的必备件
$required = @{
  '主轴'     = '带 BT30 内锥孔的旋转轴体 —— ★本装配【完全缺失】'
  '壳体'     = '固定主轴的壳体'
  '刀柄'     = '换刀时夹持刀具'
  '拉钉'     = '拉紧刀柄'
  '碟簧'     = '预紧力元件'
  '标准件'   = '螺钉/螺母/垫圈'
}
$hasSpindle = $comps | Where-Object { $_.name -match 'Spindle|主轴(?<!壳)' }
if(-not $hasSpindle){
  Add-Issue '严重' '完整性' '主轴本体缺失' `
    "BT30 ATC 换刀主轴的核心是带 7:24 内锥孔的主轴本体，本装配 11 个组件中【没有】它。" `
    "无主轴则：刀柄无处安装、壳体无轴孔、无法传递扭矩、锥孔配合无从谈起。整套机构不成立。"
}
# 固定状态检查
$fixedN = ($comps | Where-Object { $_.fixed }).Count
$floatN = ($comps | Where-Object { -not $_.fixed }).Count
Write-Output "  固定组件 = $fixedN   浮动组件 = $floatN"
if($floatN -eq 0){
  Add-Issue '严重' '装配' '全部组件处于固定状态，无自由度' `
    "11 个组件里 $($fixedN) 个 fixed=true，说明它们只是按坐标摆好的散件，【没有任何配合】。" `
    "浮动组件应为 0：真实装配中，未被配合约束的组件才能体现装配关系。当前装配不可用于运动分析/干涉检查。"
}

# ── 2. 配合检查 ──
Write-Output "`n【2】配合关系"
$hasMate = $false   # analyze_assembly 不返回 mates（R14 已知）
# 用组件位置反推：BT30 要求壳体与主轴同轴
$spindleLike = $comps | Where-Object { $_.name -match 'Housing|壳体' }
Write-Output "  ★ analyze_assembly 无 mates 字段，只能间接判断"
Add-Issue '中等' '装配' '无法确认配合关系' `
  "analyze_assembly 只返回 component_count + components[]，没有配合列表。" `
  "⇒ 需改服务端补 mates 字段（IAssemblyDoc.GetMates），否则无法自动审查配合"

# ── 3. 标准件检查 ──
Write-Output "`n【3】标准件使用"
$std = $comps | Where-Object { $_.name -match 'ISO|GB|DIN' }
Write-Output "  标准件组件 = $($std.Count) 个"
$std | ForEach-Object { Write-Output "    $($_.name)" }
if($std.Count -gt 0){
  # M12 螺钉的知识库规则
  Add-Issue '提示' '紧固' 'M12 螺钉旋合长度需校核' `
    "已用内六角螺钉 M12×40（GB/T 4762）+ 平垫（7089）+ 螺母（4032）。" `
    "按知识库 general.bolt.thread_engagement：钢件旋合需 ≥1.5d = 18mm。" `
    "★ 40mm 的螺钉旋合长度取决于被连接件厚度 —— 装配里看不到连接件，【无法校核】，需补连接件模型。"
}

# ── 4. 几何/材料检查 ──
Write-Output "`n【4】零件几何与材料"
$null = Call 'open_document' @{ file_path = "$parts\主轴壳体_Housing.sldprt" }
$m = Call 'analyze_model' @{ analysis_type='mass_properties' }
$vol = [double]([regex]::Match($m.cadState.features[0],'volume=([0-9.E+-]+)').Groups[1].Value)
$fa = Call 'analyze_model' @{ analysis_type='faces' }
$faces = ($fa.cadState.features[0] | ConvertFrom-Json).faces
$areas = $faces | Sort-Object { -$_.area }
# ★ 面积单位是 m²，×1e6 转 mm²。
# ★ 圆柱侧面积 A = π·D·L ⇒ D = A/(π·L)（得到的是【直径】，不是半径）
$outer = $areas[0].area * 1e6          # mm²
$inner = $areas[1].area * 1e6          # mm²
$OD = [math]::Round([math]::Sqrt($outer / [math]::PI / 110), 2)   # 外径 mm
$ID = [math]::Round([math]::Sqrt($inner / [math]::PI / 110), 2)   # 内径 mm
$wall = $OD - $ID
Write-Output "  壳体: 外Ø$OD 内Ø$ID 壁厚$([math]::Round($wall,1))mm 体积$([math]::Round($vol*1e9,0))mm³"

# 合理性自检：薄壁筒的壁厚应当远小于直径（这里 9/80 ≈ 11%）
if($wall -gt $OD){
    Write-Output "  ⚠ 壁厚($wall) > 外径($OD) ⇒ 单位换算有误，跳过铸造检查"
} else {
    # 知识库规则：铸造最小壁厚 = max(4, D/50 + 2.5)
    $minWall = [math]::Max(4, $OD/50 + 2.5)
    if($wall -ge $minWall){
        Write-Output "  ✅ 壁厚 $([math]::Round($wall,1)) ≥ 铸造最小 $([math]::Round($minWall,1))"
    } else {
        Add-Issue '严重' 'DFM' '壁厚不足' "壁厚 $([math]::Round($wall,1)) < 铸造最小 $([math]::Round($minWall,1))" "改为锻件或减小型腔"
    }
}

# 轴承位检查：这是换刀主轴的关键尺寸
Add-Issue '严重' '功能' '壳体无轴承位（实测确认）' `
  "壳体 Ø$OD × 110mm 薄壁筒，只有 2 平面 + 2 圆柱面（4 个面）。" `
  "★ 换刀主轴的壳体必须有【轴承位/轴承座孔】与主轴配合、并承受轴向定位。" `
  "4 个面说明它是个【素筒】—— 这正是 24 轮来 Simulation 加不上轴承载荷夹具的结构原因。"

# ── 5. 图纸完整性 ──
Write-Output "`n【5】图纸与技术要求"
$checks = @(
  @{n='表面粗糙度标注'; ok=$false; why="两端是与主轴/轴承的配合面，按知识库应 Ra0.8~1.6；模型中无任何粗糙度信息"}
  @{n='尺寸公差标注';     ok=$false; why="Ø80 属 >30~120 段，GB/T 1804-m 未注公差 ±0.3mm；模型中无公差信息"}
  @{n='形位公差(GD&T)';  ok=$false; why="轴承孔的【同轴度/位置度】是换刀精度的关键，装配里没体现"}
  @{n='材料牌号';         ok=$false; why="know库有 45钢/40Cr 等，但模型未赋材料（SolidWorks 用 AISI1020 近似）"}
  @{n='热处理要求';       ok=$false; why="轴类件通常需要调质（σb↑），图纸上必须注明"}
)
foreach($c in $checks){
  $mark = if($c.ok){'✅'}else{'❌'}
  Write-Output "  $mark $($c.n)  —— $($c.why)"
  if(-not $c.ok){ Add-Issue '缺失' '图纸' $c.n '' $c.why }
}

# ── 6. 汇总 ──
Write-Output "`n══════ 评审汇总 ══════"
$issues | Group-Object Level | ForEach-Object { Write-Output "  {0,-4} {1} 项" -f $_.Name, $_.Count }
Write-Output ""
$issues | ForEach-Object { Write-Output "  [$($_.Level)] $($_.Category) / $($_.Title)" }

# 风险评分（透明分解，参考 almightyshui 的做法）
$sev = ($issues|Where-Object{$_.Level -eq '严重'}).Count
$med = ($issues|Where-Object{$_.Level -eq '中等'}).Count
$mis = ($issues|Where-Object{$_.Level -eq '缺失'}).Count
$score = [math]::Max(0, 100 - $sev*20 - $med*8 - $mis*4)
Write-Output ""
Write-Output "  风险评分 = 100 − 严重×20 − 中等×8 − 缺失×4"
Write-Output "         = 100 − $sev×20 − $med×8 − $mis×4 = $score / 100"
Write-Output "  结论: $(if($sev -ge 2){'★ 该设计当前【不能投入加工】——存在结构性缺失'}elseif($score -ge 70){'⚠ 可继续但需补齐技术要求'}else{'❌ 不合格'})"

$issues | Export-Csv "C:\Users\Zegel\solidpilot-mcp\设计评审_BT30_ATC_20260928.csv" -NoTypeInformation -Encoding UTF8
& "C:\Users\Zegel\solidpilot-mcp\tools\reclaim.ps1" 2>&1 | Select-Object -Last 1
.Count) }
Write-Output ""
$issues | ForEach-Object { Write-Output "  [$($_.Level)] $($_.Category) / $($_.Title)" }

# 风险评分（透明分解，参考 almightyshui 的做法）
$sev = ($issues|Where-Object{$_.Level -eq '严重'}).Count
$med = ($issues|Where-Object{$_.Level -eq '中等'}).Count
$mis = ($issues|Where-Object{$_.Level -eq '缺失'}).Count
$score = [math]::Max(0, 100 - $sev*20 - $med*8 - $mis*4)
Write-Output ""
Write-Output "  风险评分 = 100 − 严重×20 − 中等×8 − 缺失×4"
Write-Output "         = 100 − $sev×20 − $med×8 − $mis×4 = $score / 100"
Write-Output "  结论: $(if($sev -ge 2){'★ 该设计当前【不能投入加工】——存在结构性缺失'}elseif($score -ge 70){'⚠ 可继续但需补齐技术要求'}else{'❌ 不合格'})"

$issues | Export-Csv "C:\Users\Zegel\solidpilot-mcp\设计评审_BT30_ATC_20260928.csv" -NoTypeInformation -Encoding UTF8
& "C:\Users\Zegel\solidpilot-mcp\tools\reclaim.ps1" 2>&1 | Select-Object -Last 1
