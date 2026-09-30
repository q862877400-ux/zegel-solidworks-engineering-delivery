<#
    SOLIDWORKS 官方文档检索器（离线，2390 页）
    查 C:\swdoc（CHM 解包）与 D:\AI\SW\AI Solidworks\官方文档\SWhelp（网页版 API）

    用法:
      .\swdoc2.ps1 -Q 'AddRestraint'                  # 全文搜索
      .\swdoc2.ps1 -Q 'fixture' -Group sim            # 限定产品组
      .\swdoc2.ps1 -List                             # 列出所有产品组
      .\swdoc2.ps1 -Q 'terminal' -Show 2               # 看命中正文
#>
param(
  [string]$Q,
  [string]$Group,
  [int]$Show = 0,
  [switch]$List
)
$ErrorActionPreference='Continue'
$ROOT = 'C:\swdoc'

if($List -or -not $Q){
  Write-Host "=== 产品组 ==="
  Get-ChildItem $ROOT -Directory | Sort-Object Name | ForEach-Object {
    $n = (Get-ChildItem $_.FullName -Recurse -File -Include *.htm,*.html -EA SilentlyContinue).Count
    "{0,-26} {1,5} 页" -f $_.Name, $n
  }
  return
}

$paths = if($Group){ "$ROOT\$Group*" } else { $ROOT }
$files = Get-ChildItem $paths -Recurse -File -Include *.htm,*.html -EA SilentlyContinue
if(-not $files){ "未找到文档（组=$Group）"; return }

"在 $($files.Count) 个文件中搜索 '$Q' …"
$hits = $files | Select-String -Pattern $Q -SimpleMatch -List -EA SilentlyContinue
if(-not $hits){ "无命中。试试更短的词，或 -List 看有哪些组。"; return }
"命中 $($hits.Count) 个文件："
$hits | ForEach-Object { "  " + $_.Path.Replace("$ROOT\","").Replace('.htm','') } | Select-Object -First 40

if($Show -gt 0){
  "`n===== 正文摘录 ($Show 个) ====="
  foreach($h in $hits | Select-Object -First $Show){
    "`n--- " + $h.Path.Replace("$ROOT\","").Replace('.htm','') + " ---"
    $t = [IO.File]::ReadAllText($h.Path)
    $t = $t -replace '(?s)<script.*?</script>',' ' -replace '(?s)<style.*?</style>',' '
    $t = ($t -replace '<[^>]+>',"`n") -replace '&nbsp;',' ' -replace '&amp;','&' -replace '&lt;','<' -replace '&gt;','>'
    $lines = $t -split "`n" | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne '' -and $_ -match [regex]::Escape($Q) }
    $lines | Select-Object -First 12 | ForEach-Object { "   | " + $_.Substring(0,[Math]::Min(180,$_.Length)) }
  }
}
