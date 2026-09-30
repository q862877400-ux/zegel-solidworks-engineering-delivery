# 批量下载 SOLIDWORKS 官方 API 文档
# 页面很脏（含大量内联 CSS），本脚本只抽取正文纯文本存 .txt，便于检索。
# 用法: pwsh -File dl_docs.ps1 -Product cosworks -Iface ICWLoadsAndRestraintsManager
param(
  [string]$Product = 'cosworks',
  [string]$Iface,
  [int]$Ver = 2021,
  [string]$OutDir = 'D:\AI\SW\AI Solidworks\官方文档\SWhelp'
)
$ErrorActionPreference = 'Continue'
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.SecurityProtocolType]::Tls12

$base = "https://help.solidworks.com/$Ver/English/api/${Product}api"

function Save-Doc($url, $path) {
  try {
    $r = Invoke-WebRequest $url -TimeoutSec 45 -UseBasicParsing -ErrorAction Stop
    [IO.File]::WriteAllText($path, $r.Content, (New-Object Text.UTF8Encoding($false)))
    return $r.Content
  } catch { return $null }
}

function Get-Plain($html) {
  if (-not $html) { return '' }
  # 去掉 script/style/head，再去标签，最后解实体
  $t = $html -replace '(?s)<script.*?</script>', ' '
  $t = $t -replace '(?s)<style.*?</style>', ' '
  $t = $t -replace '(?s)<head.*?</head>', ' '
  $t = $t -replace '<[^>]+>', "`n"
  $t = $t -replace '&nbsp;', ' ' -replace '&amp;', '&' -replace '&lt;', '<' -replace '&gt;', '>' -replace '&quot;', '"'
  ($t -split "`n" | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne '' }) -join "`n"
}

$dir = Join-Path $OutDir $Product
New-Item -ItemType Directory -Force -Path $dir | Out-Null

# 1) 成员总表（这是入口，能拿到该接口的全部方法名）
$membersUrl = "$base/SolidWorks.Interop.$Product~SolidWorks.Interop.$Product.I${Iface}_members.html"
$membersPath = Join-Path $dir "${Iface}_members.html"
$html = Save-Doc $membersUrl $membersPath
if ($html) {
  "下载成员表: $([math]::Round((Get-Item $membersPath).Length/1KB,1)) KB"
  $plain = Get-Plain $html
  [IO.File]::WriteAllText((Join-Path $dir "${Iface}_members.txt"), $plain, (New-Object Text.UTF8Encoding($false)))
  $methods = [regex]::Matches($html, "I${Iface}~(\w+)\.html") | ForEach-Object { $_.Groups[1].Value } | Sort-Object -Unique
  "该接口共 $($methods.Count) 个成员: $($methods -join ', ')"
  # 2) 逐个下载方法页
  $n = 0
  foreach ($m in $methods) {
    $u = "$base/SolidWorks.Interop.$Product~SolidWorks.Interop.$Product.I${Iface}~$m.html"
    $p = Join-Path $dir "${Iface}~$m.txt"
    if (Test-Path $p) { continue }
    $h = Save-Doc $u ((Join-Path $dir "${Iface}~$m.html"))
    if ($h) { [IO.File]::WriteAllText($p, (Get-Plain $h), (New-Object Text.UTF8Encoding($false))); $n++ }
  }
  "新增下载 $n 个方法页 -> $dir"
} else {
  "成员表下载失败: $membersUrl"
}
