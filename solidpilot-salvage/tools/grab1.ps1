# SOLIDWORKS 官方文档抓取器 v2
# 关键点（踩过的坑）：
#  1) 页面是 Next.js SPA，HTML 里没有正文；正文在 <script id="__NEXT_DATA__"> 的 JSON 里
#  2) 页面塞满 scoped CSS（<style> 里几百 KB），必须先剥掉，否则输出会炸屏
#  3) URL 里的年份/大小写很挑：从搜索结果拿到的 URL 最可靠（/2016/ /2014/ 这类旧版本反而有，
#     /2021/ 某些页面会 404）
# 用法: pwsh -File grab1.ps1 -Url "<完整URL>" -Out "<输出.txt>"
param(
  [Parameter(Mandatory=$true)][string]$Url,
  [Parameter(Mandatory=$true)][string]$Out
)
$ErrorActionPreference = 'Stop'
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.SecurityProtocolType]::Tls12

$r = Invoke-WebRequest $Url -TimeoutSec 60 -UseBasicParsing
$html = $r.Content

# 剥掉所有 style/script 块（scoped CSS 全在里面）
$body = $html -replace '(?s)<style[^>]*>.*?</style>', ' '
$body = $body -replace '(?s)<script[^>]*>.*?</script>', ' '

# 优先从 __NEXT_DATA__ 拿 helpContentData.html（真正的正文）
$text = ''
$m = [regex]::Match($html, '<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', 'Singleline')
if ($m.Success) {
  try {
    $j = $m.Groups[1].Value | ConvertFrom-Json
    $hc = $j.props.pageProps.helpContentData
    if ($hc -and $hc.PSObject.Properties.Name -contains 'html') { $body = $hc.html }
    else { Write-Host ("  ! helpContentData 无正文: " + $hc.ErrorMessage) }
  } catch { }
}

# 转纯文本
$text = ($body -replace '<[^>]+>', "`n") `
       -replace '&nbsp;', ' ' -replace '&amp;', '&' -replace '&lt;', '<' `
       -replace '&gt;', '>' -replace '&quot;', '"' -replace '&#x27;', "'"
$lines = $text -split "`n" | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne '' -and $_.Length -lt 500 }
$out = $lines -join "`n"

[IO.File]::WriteAllText($Out, $out, (New-Object Text.UTF8Encoding($false)))
Write-Host ("OK {0} -> {1} 字符, {2} 行" -f $Url.Split('/')[-1], $out.Length, $lines.Count)
# 只打印前 15 行预览，绝不倾倒全文
$lines | Select-Object -First 15 | ForEach-Object { Write-Host ("  | " + $_.Substring(0, [Math]::Min(150, $_.Length))) }
