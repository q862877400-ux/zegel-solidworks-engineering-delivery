# 审计：找出所有【存在性判据】的成功判定（静默失败的温床）
# 判据分级（从强到弱）：
#   ★★★ 产物验证：读回实际结果（面数/文件/体积/插入数）
#   ★★  返回值验证：API 返回 bool/int 有意义（EditDelete 返回 void，只能升级为产物验证）
#   ★   存在性判据：feature != null / object != null  ← 静默失败的温床
param([switch]$Fix)

$svc = "C:\Users\Zegel\solidpilot-mcp\execution\solidworks\SolidworksExecution\Services"

$rows = @()
Get-ChildItem $svc -Filter "*.cs" | ForEach-Object {
  $file = $_.Name
  $lines = Get-Content $_.FullName
  for($i=0; $i -lt $lines.Count; $i++){
    # 找 COMPLETED 判定
    if($lines[$i] -match 'Status\s*=\s*"COMPLETED"'){
      # 往前看 25 行找成功判据线索
      $lo = [Math]::Max(0, $i-25)
      $ctx = $lines[$lo..$i] -join "`n"
      $strength = 'UNKNOWN'
      $evidence = ''
      if($ctx -match 'if \(feature == null\)|if\s*\(feature\s*!=\s*null\)'){ $strength='EXIST'; $evidence='feature != null' }
      if($ctx -match 'GetFaceCount|GetEdgeCount|volume|FaceCount|analyze.*count|reports\.Count|Directory\.GetFiles'){ $strength='PRODUCT'; $evidence='产物验证' }
      if($ctx -match 'LastFeatureName|GetFeatureByName|FindFeatureByName'){ $strength='TREE'; $evidence='特征树复查' }
      if($strength -eq 'UNKNOWN'){ $strength='DIRECT'; $evidence='直接 COMPLETED（需人工看）' }
      $rows += [pscustomobject]@{
        File=$file; Line=($i+1); Strength=$strength; Evidence=$evidence
      }
    }
  }
}

Write-Output "=== 所有 Status=COMPLETED 的位置及其成功判据 ==="
$rows | Group-Object Strength | ForEach-Object {
  "  $($_.Name)  $($_.Count) 处"
}
""
Write-Output "=== 明细 ==="
$rows | Sort-Object Strength, File | ForEach-Object {
  "  [{0,-6}] {1,-36} L{2,-5} {3}" -f $_.Strength, $_.File, $_.Line, $_.Evidence
}
""
Write-Output "=== 重点：EXIST（存在性判据）= 静默失败温床 ==="
$rows | Where-Object { $_.Strength -eq 'EXIST' } | ForEach-Object { "  $($_.File):$($_.Line)" }
Write-Output ""
Write-Output "=== 重点：DIRECT（无任何验证）= 风险最高 ==="
$rows | Where-Object { $_.Strength -eq 'DIRECT' } | ForEach-Object { "  $($_.File):$($_.Line)" }
