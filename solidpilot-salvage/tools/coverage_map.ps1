# 产出：官方接口族 → 服务端能力 → 已测/未测 的映射
# 目的：找出"服务端已实现但我还从没调过"的能力（这是目标里"穷尽式覆盖"的缺口）
$ErrorActionPreference = 'Continue'
$svc = "C:\Users\Zegel\solidpilot-mcp\execution\solidworks\SolidworksExecution"
$api = "C:\swapi\types"

Write-Output "=== 服务端源码规模 ==="
Get-ChildItem $svc -Recurse -Filter *.cs | Sort-Object Length -Descending |
  Select-Object -First 12 | ForEach-Object {
    "  {0,-42} {1,6:N0} 行" -f $_.Name, ((Get-Content $_.FullName | Measure-Object -Line).Lines) }

Write-Output ""
Write-Output "=== 服务端 public/internal 方法（= 实际能力面）==="
$caps = @()
Get-ChildItem $svc -Recurse -Filter *.cs | ForEach-Object {
  $src = $_.Name
  Select-String -Path $_.FullName -Pattern 'public\s+ExecutionResponse\s+(\w+)\s*\(|internal\s+ExecutionResponse\s+(\w+)\s*\(' -AllMatches |
    ForEach-Object { $_.Matches } | ForEach-Object {
      $n = if($_.Groups[1].Success){ $_.Groups[1].Value } else { $_.Groups[2].Value }
      $caps += [pscustomobject]@{ File=$src; Method=$n }
    }
}
Write-Output "  共 $($caps.Count) 个服务方法"
$caps | Group-Object Method | Sort-Object Name | ForEach-Object { "    {0}" -f $_.Name }

Write-Output ""
Write-Output "=== 官方接口族（566 个目录）按前缀归类，与上面做差集 ==="
$dirs = Get-ChildItem $api -Directory
Write-Output "  官方接口目录 = $($dirs.Count)"

# 从服务方法名里提关键词，映射到接口族
$keywords = @{
  'Sketch'   = 'sketch|草图'
  'Extrude'  = 'extrude|拉伸|凸台'
  'Feature'  = 'feature|特征'
  'Hole'     = 'hole|孔'
  'SheetMetal' = 'sheet_metal|钣金|flange'
  'Pattern'  = 'pattern|阵列'
  'Assembly' = 'assembly|assembly|装配|component|mate|insert_component'
  'Drawing'  = 'drawing|工程图|dimension|mark'
  'Motion'   = 'motion|explode|rotation'
  'Bom'      = 'bom|BOM'
  'Material' = 'material|材料'
  'Dimension' = 'dimension|尺寸'
  'Surface'  = 'surface|曲面|loft|rib'
  'Standard' = 'standard|标准件'
  'Import'   = 'import|export|step|stl'
  'Toolbar'  = 'rib|reference|axis|plane'
}
foreach($k in $keywords.Keys | Sort-Object){
  $n = ($dirs | Where-Object { $_.Name -match $k }).Count
  $hit = ($caps | Where-Object { $_.Method -match $keywords[$k] }).Count
  "    {0,-12} 官方 {1,3} 个接口  |  服务端相关方法 {2,2} 个" -f $k, $n, $hit
}
