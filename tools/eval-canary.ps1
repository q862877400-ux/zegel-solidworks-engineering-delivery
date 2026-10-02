# ─────────────────────────────────────────────────────────────────────
# 用途：用最小 agent 循环评测 Pixel Canary 的**实际写代码能力**（不经 DSH 委派通道）。
# 为什么自己驱动：workflow 的 agent() 通道在本环境整体失效（对照实验里
#   已知的 omniroute 路由同样返回 null），无法用来评测模型本身。
#   但直连 API 已证实 tool_calls / streaming / reasoning 均正常，
#   故在此自行实现 read_file / write_file / run_python 三个工具并驱动循环。
#
# 任务边界（硬约束，违反即判不合格）：
#   - 禁止启动 SolidWorks、禁止任何真实 COM 调用
#   - 禁止编译 C#/C++
#   - 禁止出现「已验证 / 实测 / 跑通 / 验证通过 / 已跑通」
#
# 用法：pwsh -File eval-canary.ps1
# ─────────────────────────────────────────────────────────────────────
$ErrorActionPreference = 'Continue'

$cred = Get-Content "$env:USERPROFILE\.dsh\.credentials.yaml" -Raw
$key  = (($cred -split "`n" | Where-Object { $_ -match '^\s*AI_GATEWAY_API_KEY:' }) `
         -replace '^\s*AI_GATEWAY_API_KEY:\s*','').Trim().Trim('"').Trim("'")
$url  = 'https://ai-gateway.vercel.sh/v1/chat/completions'
$hdr  = @{ Authorization = "Bearer $key"; 'Content-Type' = 'application/json' }

#: ★ 2026-10-03 合并后自定位：仓库根 = 本脚本所在目录的上一级。
$R = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$TARGET = Join-Path $R 'tests\test_sw_sheet_metal_contract.py'
# 评测记录（不要改这两行的理由）：
#   首轮 max_tokens=8192  → 第 5 轮 finish=length，预算耗尽、没给出最终回复，零产出
#   次轮 max_tokens=32768 → 仍不够（medium 档的推理本身就要吃掉大量预算）
#   本轮直接按该模型的单次输出上限 131072 拉满，
#   避免把「预算不够」误当成「能力不行」。
$MAX_TURNS = 12
$MAX_TOKENS = 131072

$TOOLS = @(
  @{ type='function'; function=@{ name='read_file'; description='读取一个文本文件，返回内容'
      parameters=@{ type='object'; properties=@{ path=@{type='string';description='文件绝对路径'} }
                    required=@('path') } } }
  @{ type='function'; function=@{ name='write_file'; description='写入一个文本文件（覆盖）'
      parameters=@{ type='object'; properties=@{ path=@{type='string'}; content=@{type='string'} }
                    required=@('path','content') } } }
  @{ type='function'; function=@{ name='run_python'; description='运行一条 python 命令并返回 stdout+stderr'
      parameters=@{ type='object'; properties=@{ cmd=@{type='string';description='要执行的 python 命令'} }
                    required=@('cmd') } } }
)

$SYSTEM = @'
你是一个 SolidWorks Python 代码库的补测任务。你可以用 read_file / write_file / run_python 三个工具。

绝对禁止：
- 启动 SolidWorks、任何真实 COM 调用、import 并执行 win32com
- 编译 C#/C++
- 在任何文件或回复里出现这些词：已验证、实测、跑通、验证通过、已跑通（你没实测过，没资格说）

你只能用纯 Python 假对象模拟，不得连接任何东西。
测试必须零 pytest 依赖：纯 assert + if __name__ == "__main__" 入口。
'@

$USER = @"
目标文件：$TARGET （目前不存在，需要你新建）

先做这几步：
1. read_file 读 tests/test_sw_surface_signature_contract.py（相对仓库根）
   —— 这是你必须照抄写法的范本。
2. read_file 读 scripts/sw_sheet_metal.py（相对仓库根） —— 了解被测对象。
3. write_file 写出 $TARGET。
4. run_python 跑 `python tests\test_sw_sheet_metal_contract.py` 确认通过。
5. 最后用一段话报告：通过数、关键取舍、遇到的不确定之处。不要粉饰。

"@

$messages = @(
  @{ role='system'; content=$SYSTEM },
  @{ role='user';   content=$USER }
)

for ($turn = 1; $turn -le $MAX_TURNS; $turn++) {
  $body = @{
    model = 'stealth/pixel-canary'
    messages = $messages
    tools = $TOOLS
    max_tokens = $MAX_TOKENS
    reasoning_effort = 'medium'
  }
  $sw = [System.Diagnostics.Stopwatch]::StartNew()
  try {
    $r = Invoke-RestMethod -Uri $url -Method Post -Headers $hdr `
         -Body ($body | ConvertTo-Json -Depth 20 -Compress) -TimeoutSec 900
  } catch {
    Write-Host "[FATAL] 第 $turn 轮请求失败: $($_.Exception.Message)"
    Write-Host "[HINT] 该模型单轮实测可达 280 秒以上（medium 档），TimeoutSec 需 >= 900"
    exit 1
  }
  $sw.Stop()
  $msg = $r.choices[0].message
  $usage = $r.usage
  Write-Host ("--- turn {0}  {1:N1}s  finish={2}  in={3} out={4}" -f `
              $turn, $sw.Elapsed.TotalSeconds, $r.choices[0].finish_reason, $usage.prompt_tokens, $usage.completion_tokens)
  $messages += $msg

  if (-not $msg.tool_calls -or $msg.tool_calls.Count -eq 0) {
    Write-Host "`n=== 最终回复 ==="
    Write-Host $msg.content
    exit 0
  }

  foreach ($tc in $msg.tool_calls) {
    $fn = $tc.function.name
    $argText = $tc.function.arguments
    $arg = if ($argText) { $argText | ConvertFrom-Json } else { @{} }
    $out = ''
    switch ($fn) {
      'read_file' {
        $p = [string]$arg.path
        if (Test-Path -LiteralPath $p) { $out = Get-Content -LiteralPath $p -Raw }
        else { $out = "[ERROR] 文件不存在: $p" }
        if ($out.Length -gt 24000) { $out = $out.Substring(0, 24000) + "`n...[截断]" }
      }
      'write_file' {
        $p = [string]$arg.path
        $dir = Split-Path -Parent $p
        if (-not (Test-Path -LiteralPath $dir)) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
        [System.IO.File]::WriteAllText($p, [string]$arg.content, [System.Text.UTF8Encoding]::new($false))
        $out = "[OK] 已写入 $p ($((Get-Item -LiteralPath $p).Length) 字节)"
      }
      'run_python' {
        $cmd = [string]$arg.cmd
        Push-Location $R
        $env:PYTHONPATH = $R
        $o = & pwsh -NoProfile -Command $cmd 2>&1 | Out-String
        Pop-Location
        $out = if ($o.Length -gt 12000) { $o.Substring(0,12000) + "`n...[截断]" } else { $o }
      }
      default { $out = "[ERROR] 未知工具 $fn" }
    }
    Write-Host ("    工具 {0}({1}) -> {2} 字符" -f $fn, (($argText -replace '\s+',' ').Substring(0,[Math]::Min(90,($argText -replace '\s+',' ').Length))), $out.Length)
    $messages += @{ role='tool'; tool_call_id=$tc.id; content=$out }
  }
}
Write-Host "[FATAL] 达到最大轮次 $MAX_TURNS 仍未给出最终回复"
exit 1
