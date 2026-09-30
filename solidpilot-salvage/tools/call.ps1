# 直连执行层的通用调用助手（手册 §三）
# 用法：. C:\Users\Zegel\AppData\Local\Temp\swprobe\call.ps1
# 然后： $r = Call 'tool_name' @{ param = value }

[System.Net.WebRequest]::DefaultWebProxy = New-Object System.Net.WebProxy

function Call {
    param([string]$tool, [hashtable]$params, [int]$timeoutSec = 200)
    $sv = [int](Invoke-RestMethod "http://localhost:5000/api/tool/state" -TimeoutSec 20).stateVersion
    $b  = @{operationId=[guid]::NewGuid().ToString(); tool=$tool; stateVersion=$sv; params=$params} |
          ConvertTo-Json -Depth 10 -Compress
    try {
        Invoke-RestMethod "http://localhost:5000/api/tool/execute" -Method Post -TimeoutSec $timeoutSec `
            -ContentType 'application/json; charset=utf-8' -Body ([Text.Encoding]::UTF8.GetBytes($b))
    } catch {
        @{status='ERR'; error=@{message=$_.ErrorDetails.Message}}
    }
}

# 紧凑打印：只给 status / error / result 前 N 字符
function Show($r, $n = 600) {
    $s = $r | ConvertTo-Json -Depth 12 -Compress
    if ($s.Length -gt $n) { $s.Substring(0, $n) + " ...[trunc]" } else { $s }
}

# 取 payload 字段（result 可能是 JSON 字符串）
function Payload($r) {
    try { return ($r.result | ConvertFrom-Json) } catch { return $null }
}
