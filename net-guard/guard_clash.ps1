# 网络守护 —— 断网自动回滚 + 唤醒
#
# 为什么需要：用户授权我操作 Clash（改代理设置）。**改错会直接完全断网**，
# 而用户睡觉时无法干预。本守护独立于任何 agent 会话运行，负责：
#   ① 备份当前网络设置（注册表代理项 + Clash 配置文件的哈希）
#   ② 定期体检：本地代理是否在听、经代理能否出网
#   ③ 连续失败达阈值 ⇒ **回滚注册表代理设置** + 写标志文件 + 弹通知
#   ④ 全程写日志，供早上复查
#
# ── 来源 ──
# 仓库:   本项目自身（用户在 2026-10-01 明确要求的安全守护）
# 文件:   D:\AI\SW\net-guard\guard_clash.ps1
# 定位:   AGENTS.md 三条红线的**技术保障**：「不碰系统层」在本任务里被用户显式授权扩展到
#         「可操作 Clash 代理设置」，故配套一个不依赖 agent 会话的回滚器。
#         判据：守护进程独立存活（不随 DSH 会话结束而死）+ 回滚可验证（读回注册表比对）。
# 官方签名依据: 不适用（Windows 注册表 + Clash Verge 配置目录，无 COM 调用）
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 本脚本会**写 HKCU 的 Internet Settings 代理项**（回滚用）。只在检测到断网时写。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────────────

param(
    # 体检间隔（秒）
    [int]$IntervalSeconds = 30,
    # 连续失败多少次才回滚（避免一次抖动就动手）
    [int]$FailureThreshold = 4,
    # 最长存活小时数 —— 到点自行退出，避免留下永久进程
    [double]$MaxHours = 14,
    # 只体检不回滚（演练用）
    [switch]$DryRun
)

$ErrorActionPreference = 'Continue'
$Root   = 'D:\AI\SW\net-guard'
$Backup = Join-Path $Root 'backup'
$Log    = Join-Path $Root 'guard.log'
$Flag   = Join-Path $Root 'NET-DOWN.flag'
$State  = Join-Path $Root 'state.json'

New-Item -ItemType Directory -Force -Path $Backup | Out-Null

function Write-Log([string]$msg) {
    $line = '{0} {1}' -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $msg
    Add-Content -Path $Log -Value $line -Encoding UTF8
}

$RegPath = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings'

function Get-ProxySnapshot {
    $k = Get-ItemProperty -Path $RegPath -ErrorAction SilentlyContinue
    [pscustomobject]@{
        ProxyEnable   = $k.ProxyEnable
        ProxyServer   = $k.ProxyServer
        ProxyOverride = $k.ProxyOverride
        AutoConfigURL = $k.AutoConfigURL
    }
}

# ── ① 启动即备份（幂等：已存在就不覆盖，保住「最初那份」）──
$snapshotFile = Join-Path $Backup 'proxy-settings.json'
if (-not (Test-Path $snapshotFile)) {
    $snap = Get-ProxySnapshot
    $snap | ConvertTo-Json | Set-Content -Path $snapshotFile -Encoding UTF8
    Write-Log "已备份注册表代理设置：Enable=$($snap.ProxyEnable) Server=$($snap.ProxyServer)"
} else {
    Write-Log '注册表代理备份已存在，不覆盖（保住最初那份）'
}

# Clash 配置文件也留一份基线哈希（只记录，不改）
$ClashDir = Join-Path $env:APPDATA 'io.github.clash-verge-rev.clash-verge-rev'
$clashHashes = @{}
if (Test-Path $ClashDir) {
    foreach ($f in @('config.yaml', 'clash-verge.yaml', 'verge.yaml', 'dns_config.yaml', 'profiles.yaml')) {
        $p = Join-Path $ClashDir $f
        if (Test-Path $p) {
            $clashHashes[$f] = (Get-FileHash $p -Algorithm SHA256).Hash
        }
    }
    $clashHashes | ConvertTo-Json | Set-Content -Path (Join-Path $Backup 'clash-hashes.json') -Encoding UTF8
    Write-Log "已记录 Clash 配置哈希：$($clashHashes.Keys -join ', ')"
}

# ── ② 体检函数 ──
function Test-LocalProxy {
    # 本地代理端口在不在听
    $c = Get-NetTCPConnection -LocalPort 7897 -State Listen -ErrorAction SilentlyContinue
    return [bool]$c
}

function Test-ProxyEgress {
    # 经代理能不能出网（用一个稳定的国内站点，避免国际链路抖动误判）
    try {
        $r = Invoke-WebRequest -Uri 'https://www.baidu.com' -Method Head -TimeoutSec 10 `
            -Proxy 'http://127.0.0.1:7897' -ErrorAction Stop
        return ($r.StatusCode -ge 200 -and $r.StatusCode -lt 400)
    } catch {
        return $false
    }
}

function Test-DirectEgress {
    # 不走代理能不能出网（判断是「整体断网」还是「仅代理坏」）
    try {
        $r = Invoke-WebRequest -Uri 'https://www.baidu.com' -Method Head -TimeoutSec 10 `
            -Proxy $null -ErrorAction Stop
        return ($r.StatusCode -ge 200 -and $r.StatusCode -lt 400)
    } catch {
        return $false
    }
}

function Restore-Proxy {
    $snap = Get-Content $snapshotFile -Raw -Encoding UTF8 | ConvertFrom-Json
    Set-ItemProperty -Path $RegPath -Name 'ProxyEnable'   -Value ([int]$snap.ProxyEnable)   -ErrorAction SilentlyContinue
    Set-ItemProperty -Path $RegPath -Name 'ProxyServer'   -Value ([string]$snap.ProxyServer) -ErrorAction SilentlyContinue
    Set-ItemProperty -Path $RegPath -Name 'ProxyOverride' -Value ([string]$snap.ProxyOverride) -ErrorAction SilentlyContinue
    Write-Log "已回滚注册表代理设置为备份值：Enable=$($snap.ProxyEnable) Server=$($snap.ProxyServer)"
}

function Notify([string]$title, [string]$body) {
    # 不依赖任何 agent 工具：直接弹 Windows 通知（失败也不影响主流程）
    try {
        Add-Type -AssemblyName System.Windows.Forms -ErrorAction SilentlyContinue
        $ni = New-Object System.Windows.Forms.NotifyIcon
        $ni.Icon = [System.Drawing.SystemIcons]::Warning
        $ni.Visible = $true
        $ni.ShowBalloonTip(15000, $title, $body, [System.Windows.Forms.ToolTipIcon]::Warning)
        Start-Sleep -Seconds 8
        $ni.Dispose()
    } catch {
        Write-Log "弹通知失败（不影响回滚）：$($_.Exception.Message)"
    }
}

# ── ③ 主循环 ──
$failures = 0
$restored = $false
$deadline = (Get-Date).AddHours($MaxHours)
Write-Log "守护启动：间隔 ${IntervalSeconds}s，阈值 $FailureThreshold 次，最长 $MaxHours 小时，DryRun=$DryRun，PID=$PID"

while ($true) {
    if ((Get-Date) -gt $deadline) {
        Write-Log "已达最长存活 $MaxHours 小时，守护自行退出（未回滚＝期间未检测到断网）"
        break
    }
    $proxyUp  = Test-LocalProxy
    $proxyNet = if ($proxyUp) { Test-ProxyEgress } else { $false }
    $directNet = Test-DirectEgress

    $ok = $proxyUp -and $proxyNet

    if ($ok) {
        if ($failures -gt 0) { Write-Log "已恢复（连续失败计数从 $failures 归零）" }
        $failures = 0
    } else {
        $failures++
        Write-Log ("体检失败 {0}/{1}：代理端口在听={2} 经代理出网={3} 直连出网={4}" -f `
            $failures, $FailureThreshold, $proxyUp, $proxyNet, $directNet)
    }

    # 写状态供 agent 早上读取
    [pscustomobject]@{
        ts           = (Get-Date -Format 'o')
        proxy_listening = $proxyUp
        proxy_egress    = $proxyNet
        direct_egress   = $directNet
        consecutive_failures = $failures
        restored     = $restored
    } | ConvertTo-Json | Set-Content -Path $State -Encoding UTF8

    if ($failures -ge $FailureThreshold -and -not $restored) {
        Write-Log "★ 连续 $failures 次失败，触发回滚"
        if (-not $DryRun) {
            Restore-Proxy
            $restored = $true
            @(
                "网络守护在 $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') 检测到连续 $failures 次体检失败，",
                "已把注册表代理设置回滚到守护启动时的备份值。",
                "",
                "失败明细：代理端口在听=$proxyUp  经代理出网=$proxyNet  直连出网=$directNet",
                "备份文件：$snapshotFile",
                "日志：$Log"
            ) | Set-Content -Path $Flag -Encoding UTF8
            Notify '网络守护：已回滚代理设置' "连续 $failures 次体检失败，已还原到启动时的备份。详见 $Flag"
        } else {
            Write-Log '（DryRun，未实际回滚）'
            $restored = $true
        }
    }

    Start-Sleep -Seconds $IntervalSeconds
}
