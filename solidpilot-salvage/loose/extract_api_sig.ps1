# 从已下载的 SOLIDWORKS API 页面提取官方方法签名
# 页面是 Next.js SPA，签名以 JSON 转义形式嵌在 HTML 里（\u003c = <, \u0026nbsp; = nbsp）
# 做法：在每个 "ByVal <i><a class=parameter id=XXX" 处取 id，再取前面的参数名
param(
  [string]$Dir = 'D:\AI\SW\AI Solidworks\官方文档\SWhelp\cosworks',
  [string]$Prefix = 'ICWLoadsAndRestraintsManager~'
)
$ErrorActionPreference='Continue'

function Unescape($s){
  $s = $s -replace '\\u003c','<' -replace '\\u003e','>' -replace '\\u0026nbsp;',' ' `
       -replace '\\u0026amp;','&' -replace '\\n',"`n" -replace '\\t',' ' -replace '\\"','"'
  return $s
}

$files = Get-ChildItem $Dir -Filter "$Prefix*.html" -EA SilentlyContinue
"处理 $($files.Count) 个方法页`n"
foreach($f in $files){
  $name = $f.Name.Replace($Prefix,'').Replace('.html','')
  $h = [IO.File]::ReadAllText($f.FullName)
  # 取所有  id="ParamName"  参数
  $params = [regex]::Matches($h,'id=\\?"(\w+)\\?"\s+href=\\?"#\\?"') | ForEach-Object { $_.Groups[1].Value }
  $params = $params | Select-Object -Unique
  # 也找 C# 风格签名
  $sigC = ''
  $m = [regex]::Match($h,'class=\\?"parameter\\?"\s+id=\\?"[^"]+?\\?"[^>]*>\w+?\s*\w+\s*(As\s+\S+)?')
  if($m.Success){ $sigC = Unescape $m.Value }

  "{0,-38} ({1}) {2}" -f $name, $params.Count, ($params -join ', ')
}
