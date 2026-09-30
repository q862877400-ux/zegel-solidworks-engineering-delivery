. "C:\Users\Zegel\solidpilot-mcp\tools\call.ps1"
# loft 判别实验：确认是"选中状态"问题还是"blend 参数"问题
# 变量1：草图名字带引号还是不带
# 变量2：选草图 vs 直接选草图里的圆
# 变量3：StartMatchingType 传 0(None) vs 1(Linear)

function New2Sections {
  $null = Call 'open_new_part' @{}
  $null = Call 'create_sketch' @{ plane='Front Plane' }
  $null = Call 'add_sketch_entity' @{ entity_type='circle'; cx=0; cy=0; radius=0.02 }
  $null = Call 'create_sketch' @{ plane='Top Plane' }
  $null = Call 'add_sketch_entity' @{ entity_type='circle'; cx=0; cy=0; radius=0.04 }
  $f = Call 'analyze_model' @{ analysis_type='features' }
  $names = ($f.cadState.features[0] | ConvertFrom-Json).features |
           Where-Object { $_.type -eq 'ProfileFeature' } | ForEach-Object { $_.name }
  return $names
}

Write-Output "=== 造两个截面 ==="
$n = New2Sections
Write-Output "  草图: $($n -join ', ')"

# 变体 A：两个草图、匹配类型 None（当前实现）
Write-Output "=== A: profiles=两个草图 ==="
$pA = '["' + $n[0] + '","' + $n[1] + '"]'
$rA = Call 'extrude_feature' @{ feature_type='loft'; profiles=$pA } -TimeoutSec 90
Write-Output "  A => $($rA.status) $(if($rA.status -ne 'COMPLETED'){$rA.error.code})"

# 变体 B：先看看草图里到底有没有几何（排除空草图）
Write-Output "=== B: 检查草图内容 ==="
foreach ($s in $n) {
  $sk = Call 'analyze_model' @{ analysis_type='sketch'; name=$s }
  $t = $sk.cadState.features[0] -replace '\s+',' '
  Write-Output "  $s => $($t.Substring(0,[Math]::Min(150,$t.Length)))"
}

# 变体 C：只有一个草图时 loft 报什么（最小场景）
Write-Output "=== C: 单草图（预期 INVALID_PARAMETER，可确认参数解析正常）==="
$pC = '["' + $n[0] + '"]'
$rC = Call 'extrude_feature' @{ feature_type='loft'; profiles=$pC } -TimeoutSec 60
Write-Output "  C => $($rC.status) $(if($rC.status -ne 'COMPLETED'){$rC.error.code})"
