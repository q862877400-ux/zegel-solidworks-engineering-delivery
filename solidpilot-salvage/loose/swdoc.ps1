<#
  SolidWorks 官方文档全文检索（本地离线）
  文档来源：D:\AI\SW\AI Solidworks\官方文档\  （由 SolidWorks 安装目录 api\*.chm 用 hh.exe -decompile 解出，
           共 29,650 个文件 / 243.6 MB，覆盖 sldworksapi、swconst、sldworksapivb6 三册）

  用法：
    .\swdoc.ps1 -Q "FeatureCut4"
    .\swdoc.ps1 -Q "swEndCondUpToSelection" -Max 5
    .\swdoc.ps1 -File "AddComponent5"          # 按文件名定位
    .\swdoc.ps1 -List                          # 列出三册概况
#>
param(
  [string]$Q,
  [string]$File,
  [int]$Max = 12,
  [switch]$List
)
$ErrorActionPreference = 'Stop'
$Root = 'D:\AI\SW\AI Solidworks\官方文档'

if ($List -or (-not $Q -and -not $File)) {
  foreach ($d in Get-ChildItem $Root -Directory) {
    $f = Get-ChildItem $d.FullName -Recurse -File -EA SilentlyContinue
    "{0,-18} {1,6} 文件  {2,7:N1} MB" -f $d.Name, $f.Count, ((($f|Measure-Object Length -Sum).Sum)/1mb)
  }
  "`n用法: -Q '关键词'  |  -File '页面名'  |  -List"
  return
}

# HTML -> 纯文本（去脚本/样式/标签，解实体，保留表格分隔）
function H2T([string]$p, [int]$max) {
  $h = Get-Content $p -Raw -Encoding UTF8
  $h = $h -replace '(?s)<script.*?</script>', '' -replace '(?s)<style.*?</style>', ''
  $h = $h -replace '(?i)</(p|div|tr|li|h[1-6]|table)>', "`n"
  $h = $h -replace '(?i)</t[dh]>', ' | '
  $h = $h -replace '<[^>]+>', ''
  $h = [System.Net.WebUtility]::HtmlDecode($h)
  $h = ($h -split "`n" | ForEach-Object { $_.Trim() } | Where-Object { $_ -and $_ -ne '|' }) -join "`n"
  if ($h.Length -gt $max) { $h.Substring(0,$max) + "`n...[截断]" } else { $h }
}

if ($File) {
  $hits = Get-ChildItem $Root -Recurse -File -Include *.htm,*.html -EA SilentlyContinue |
          Where-Object { $_.BaseName -like "*$File*" } | Select-Object -First 3
  if (-not $hits) { "未找到: $File"; return }
  foreach ($h in $hits) {
    "================ $($h.Directory.Name)\$($h.Name) ================"
    H2T $h.FullName 3500
    ""
  }
  return
}

"### 检索 '$Q' （上限 $Max 条）"
$files = (Get-ChildItem $Root -Recurse -File -Include *.htm,*.html -EA SilentlyContinue).FullName
$found = Select-String -Path $files -Pattern ([regex]::Escape($Q)) -List -EA SilentlyContinue |
         Select-Object -First $Max
if (-not $found) { "无结果"; return }
foreach ($s in $found) {
  $rel = $s.Path.Replace("$Root\", '')
  "--- $rel  (行 $($s.LineNumber)) ---"
  $txt = H2T $s.Path 200000
  $lines = $txt -split "`n"
  $hit  = $lines | Where-Object { $_ -like "*$Q*" } | Select-Object -First 3
  $hit | ForEach-Object { "    " + $_.Trim() }
  ""
}

