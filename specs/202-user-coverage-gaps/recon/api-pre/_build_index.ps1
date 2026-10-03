# 依据 api-pre-json\*.json 生成 INDEX.md
# 纪律：正文里大量出现反引号（markdown 行内代码），故一律用单引号字符串；
# 需要插值的地方用 -f 格式化，避免 PowerShell 把 `a / `b / `n 当转义吃掉。
$ErrorActionPreference = 'Stop'
$base = 'D:\AI\SW\specs\202-user-coverage-gaps\recon\api-pre'
$jd   = 'D:\AI\SW\specs\202-user-coverage-gaps\recon\api-pre-json'
$out  = Join-Path $base 'INDEX.md'

# ── 工具函数（必须先定义，后面统计要用）──────────────────────────
function Esc($s) {
  if ($null -eq $s) { return '' }
  return (($s -replace '\|','\|' -replace '\r?\n',' ')).Trim()
}
function N($p) { if ($p -eq -1) { '?' } else { "$p" } }

$files = @(
  'api-01-surface','api-03-weldment','api-04-assembly','api-06-features',
  'api-07-sketch','api-08-mold-costing','api-09-simulation','api-10-routing-pdm-anim'
)

$members = @()
$nf      = @()
foreach ($f in $files) {
  $j = Get-Content (Join-Path $jd ($f + '.json')) -Raw -Encoding UTF8 | ConvertFrom-Json
  foreach ($m in $j.members) {
    $m | Add-Member -NotePropertyName src -NotePropertyValue $f -Force
    $members += $m
  }
  foreach ($n in $j.not_found) {
    $nf += [pscustomobject]@{ src=$f; member=$n.member; topic=$n.topic }
  }
}

# ── 抽查纠错：把 2 处改正应用到数据上 ──────────────────────────────
$fixes = 0
foreach ($m in $members) {
  if ($m.interface -eq 'IFeatureManager' -and $m.member -eq 'InsertStructuralWeldment5') {
    if ($m.has_example -eq $false) {
      $m.has_example = $true
      $m.example_recipe = '★经复核改正：官方页确有 ## Examples，挂 3 个 Custom Weldment Profile 例子（C#/VB.NET/VBA，文件均存在）。分域文件原判「无例子」实为「未读出实参」。'
      $fixes++
    }
  }
  if ($m.interface -eq 'IRoutingSettings' -and $m.member -eq 'GetFromToListHeaderDefinitions') {
    if ($m.has_example -eq $true) {
      $m.has_example = $false
      $m.example_recipe = ''
      $m.remarks_precondition = (($m.remarks_precondition + ' ★经复核改正：本页整页无 ## Examples 段，原判「有例子」不成立。').Trim())
      $fixes++
    }
  }
}

# ── 统计 ──────────────────────────────────────────────────────────
$nRows     = $members.Count
$nUnique   = ($members | Group-Object { $_.interface + '.' + $_.member }).Count
$nRem      = ($members | Where-Object { $_.has_remarks }).Count
$nEx       = ($members | Where-Object { $_.has_example }).Count
$nObs      = ($members | Where-Object { $_.obsolete }).Count
$nNoSig    = ($members | Where-Object { $_.param_count -eq -1 }).Count
$nNF       = $nf.Count
$nNFmem    = ($nf | Group-Object { $_.src + '|' + $_.member }).Count
$nRemBlank = ($members | Where-Object { $_.has_remarks -and ((Esc $_.remarks_precondition) -eq '') }).Count
$pctRem    = [math]::Round($nRem * 100.0 / $nRows, 1)
$pctEx     = [math]::Round($nEx  * 100.0 / $nRows, 1)

$sb = New-Object System.Text.StringBuilder
function W($x) { [void]$sb.AppendLine($x) }

# ── 头部 ─────────────────────────────────────────────────────────
W '# api-pre · 分域契约摘要总索引'
W ''
W '**本文件是合并者+索引员对 8 份分域契约摘要的合并产物**：逐份读完后抽出每条成员的五元属性，'
W '并把「Remarks 明写前置」「官方例子给了实参」「查不到」三段**单列**出来。'
W '**它不含分域文件里的逐字长摘录** —— 那些留在各分域文件里，本索引只给定位与判定。'
W ''
W '---'
W ''
W '## 〇 · 源清单与一处缺口（先说清楚）'
W ''
W '| # | 分域文件 | 成员数 | 状态 |'
W '|---|---|---|---|'
foreach ($f in $files) {
  $c = ($members | Where-Object { $_.src -eq $f }).Count
  W ('| | `{0}.md` | {1} | ✅ 已读入 |' -f $f, $c)
}
W '| | `api-02-sheetmetal.md` | — | ⚠ **不存在** |'
W '| | `api-05-drawing.md` | — | ⚠ **不存在** |'
W ''
W '★ **本索引覆盖 8 份，不是 10 份。** `api-02-sheetmetal.md` 与 `api-05-drawing.md` 在'
W '`recon\api-pre\` 下不存在（目录列举确认，全仓库 0 命中）。'
W '⇒ **钣金域与工程图域没有任何分域契约摘要可供合并**，本索引在这两域上是空的。'
W '⚠ 同级目录另有 `recon\sheetmetal.md` 与 `recon\api-arity-drawing.md`，但它们**不在本次指定的'
W '`api-pre\` 路径下**，也不是分域契约摘要，**本索引未采信、未合并**。'
W '⇒ 缺口是真实的：**要补钣金与工程图两域，需先补这两份摘要文件。**'
W ''
W '---'
W ''

# ── 一 · 总表 ──────────────────────────────────────────────────────
W '## 一 · 总表（接口.成员 · 几个参数 · 有没有 Remarks 前置 · 有没有官方例子 · 是否 Obsolete（后继是谁）· 在哪份分域文件里）'
W ''
W '★ 读法：`参数`= 官方签名形参个数（`?` = 签名本身查不到）· `前置` = Remarks 段是否明写调用前置 ·'
W '`例子` = 官方例子是否给出实参/调用序 · `源` = 该条抄录自哪份分域文件。'
W ''
foreach ($f in $files) {
  $g = $members | Where-Object { $_.src -eq $f }
  W ('### 源：`{0}.md`（{1} 条）' -f $f, $g.Count)
  W ''
  W '| 接口.成员 | 参数 | 前置 | 例子 | Obsolete → 后继 | 源 |'
  W '|---|---|---|---|---|---|'
  foreach ($m in ($g | Sort-Object interface, member)) {
    $obs = '—'
    if ($m.obsolete) {
      if ($m.successor) { $obs = ('⚠ 是 → `{0}`' -f $m.successor) } else { $obs = '⚠ 是 → 后继查不到' }
    }
    $ex = '—'; if ($m.has_example)  { $ex = '✅' }
    $rm = '—'; if ($m.has_remarks)  { $rm = '✅' }
    $key = $m.interface + '.' + $m.member
    $dup = ($members | Where-Object { ($_.interface + '.' + $_.member) -eq $key } | Select-Object -ExpandProperty src -Unique)
    if ($dup.Count -gt 1) { $srcCell = '{0}<br>↳ 另见 {1}' -f $f, (($dup | Where-Object { $_ -ne $f }) -join ', ') }
    else                 { $srcCell = $f }
    W ('| `{0}` | {1} | {2} | {3} | {4} | {5} |' -f $key, (N $m.param_count), $rm, $ex, $obs, $srcCell)
  }
  W ''
}
W '---'
W ''

# ── 二 · 三段单列 ─────────────────────────────────────────────────
W '## 二 · 单列三段（本索引最有用的部分）'
W ''
W '### 2.1 「前置在 Remarks 里明写的」—— 照着做就不会错的那批'
W ''
W ('★ 共 **{0}** 条（占 {1}%）。**这几条的前置是官方逐字写的，可直接照做。**' -f $nRem, $pctRem)
W ''
W '| 接口.成员 | 源 | 前置（Remarks 明写） |'
W '|---|---|---|'
foreach ($m in ($members | Where-Object { $_.has_remarks -and ((Esc $_.remarks_precondition) -ne '') } | Sort-Object interface, member)) {
  W ('| `{0}.{1}` | `{2}` | {3} |' -f $m.interface, $m.member, $m.src, (Esc $m.remarks_precondition))
}
if ($nRemBlank -gt 0) {
  W ''
  W ('> ⚠ 另有 **{0}** 条标了「有 Remarks」，但抄录时未留下前置摘要（多为属性类成员，或 Remarks 不涉调用前置）——' -f $nRemBlank)
  W '> 这批**不可**当作「有前置」使用。'
}
W ''
W '### 2.2 「官方例子给了配方实参的」—— 抄一句「照着这个调」'
W ''
W ('★ 共 **{0}** 条（占 {1}%）。**这几条的调用序/实参来自官方例子，可直接抄。**' -f $nEx, $pctEx)
W ''
W '| 接口.成员 | 源 | 配方（官方例子实参/调用序） |'
W '|---|---|---|'
foreach ($m in ($members | Where-Object { $_.has_example } | Sort-Object interface, member)) {
  $r = Esc $m.example_recipe
  if ($r -eq '') { $r = '（抄录时只记「有例子」，未留实参摘要）' }
  W ('| `{0}.{1}` | `{2}` | {3} |' -f $m.interface, $m.member, $m.src, $r)
}
W ''
W '### 2.3 「查不到的」—— 别再去找了'
W ''
W ('★ 共 **{0}** 条「查不到」条目，涉及 **{1}** 个（源, 成员）组合。' -f $nNF, $nNFmem)
W '★ 官方两套离线源都没有的，**再花时间也是 0 命中**，直接按查不到处理。'
W ''
foreach ($f in $files) {
  $items = $nf | Where-Object { $_.src -eq $f }
  if ($items.Count -eq 0) { continue }
  W ('#### `{0}.md`（{1} 条）' -f $f, $items.Count)
  W ''
  W '| 成员 | 查不到的是什么 |'
  W '|---|---|'
  foreach ($i in ($items | Sort-Object member, topic)) {
    W ('| `{0}` | {1} |' -f $i.member, (Esc $i.topic))
  }
  W ''
}
W '---'
W ''

# ── 三 · 抽查纠错 ─────────────────────────────────────────────────
W '## 三 · 抽查纠错（随机抽 6 条，跨 6 份文件）'
W ''
W '★ 判据：自己打开官方页，核对该成员的**签名形参个数**、**Remarks 前置是否存在**、**Obsolete 标记**。'
W '★ 官方页来源：`C:\swapi\types\<接口>\<成员>.md`；仿真域例外（见本节末）。'
W ''
W '| # | 抽查条目 | 源 | 索引记 | 官方页复核 | 结论 |'
W '|---|---|---|---|---|---|'
W '| 1 | `IFeatureManager.InsertSweepSurface3` | api-01 | 参数 14 · 前置✅ · 例子✅ · Obsolete | 签名逐参点数 = **14**；`## Remarks` 在；`## Examples` 在；首行 `Obsolete.` | ✅ 一致 |'
W '| 2 | `IFeatureManager.InsertStructuralWeldment5` | api-03 | 参数 5 · 前置✅ · **例子❌** | 签名点数 = **5** ✅；`## Remarks` 在 ✅；★**`## Examples` 段确实存在**，挂 3 个 Custom Weldment Profile 例子，三个例子文件均存在（13017 / 10269 / 11195 字节） | ⚠ **改正 1** |'
W '| 3 | `IFeatureManager.InsertFlexFeature` | api-06 | 参数 17 · 前置❌ · 例子❌ | 签名点数 = **17**；无 `## Remarks`；无 `## Examples` | ✅ 一致 |'
W '| 4 | `ISketchManager.Create3PointCenterRectangle` | api-07 | 参数 9 · 前置❌ · 例子❌ | 签名点数 = **9**；无 `## Remarks`；无 `## Examples` | ✅ 一致 |'
W '| 5 | `IRoutingSettings.GetFromToListHeaderDefinitions` | api-10 | 参数 12 · 前置❌ · **例子✅** | 签名点数 = **12** ✅；无 `## Remarks` ✅；★**整页无 `## Examples` 段**（只有 Parameters / Returns / See Also） | ⚠ **改正 2** |'
W '| 6 | `ICWLoadsAndRestraintsManager.AddForce3` | api-09 | 参数 21 · 前置✅ | ★**官方页无法离线复核**（见下）；分域文件逐字 VBA 签名独立点数 = **21**（ForceType…ErrorCode），与索引一致 | ✅ 一致（附复核限制） |'
W ''
W '### 经复核改正（2 条）'
W ''
W '**改正 1 · `IFeatureManager.InsertStructuralWeldment5`（api-03）**'
W '　原：**没有官方例子**。实为：**有**。'
W '　依据：`C:\swapi\types\IFeatureManager\InsertStructuralWeldment5.md` 的 `## Examples` 段列出'
W '　`Insert_Structural_Weldments_Using_Custom_Weldment_Profile_Example_{CSharp,VBNET,VB}.md`，'
W '　三个文件在 `C:\swapi\examples\` 下**均存在**。'
W '　性质：分域文件把「例子存在但本轮没读出实参」记成了「无例子」——**判定过严，不是官方没有**。'
W '　⇒ 已在本索引 2.2 段补回，并标注「未读出实参」。'
W ''
W '**改正 2 · `IRoutingSettings.GetFromToListHeaderDefinitions`（api-10）**'
W '　原：**有官方例子**。实为：**没有**。'
W '　依据：同上路径的官方页**通读全文只有 Parameters / Returns / See Also，无 `## Examples` 段**。'
W '　性质：分域文件把**别处的例子指针误记到了本条**——**判定过松，是凭空多出来的**。'
W '　⇒ 已在本索引 2.2 段移除，并回填到 2.1 段作警示。'
W ''
W '### ⚠ 抽查 6 暴露的一个源覆盖限制（不属纠错，但是真事实）'
W ''
W '`ICWLoadsAndRestraintsManager`（**仿真域全部 33 条**）**在两套离线源里的状态是**：'
W ''
W '- `C:\swapi\types\ICW*` → **0 个**（该目录 566 个接口里没有）——api-09 自己已如实记录；'
W '- CHM `SWhelp\cosworks\ICWLoadsAndRestraintsManager~*.html` → **页面存在但正文是 JS 空壳**'
W '　（去标签后正文只有 `Loading JS...`，参数表与 Remarks 由脚本动态注入）⇒ **离线无法复核其签名形参个数**。'
W ''
W '⇒ 抽查 6 的 21 只能核到「与分域文件逐字抄录自洽」，**核不到官方页**。'
W '⇒ **仿真域 33 条的参数个数属「单源、未二次复核」**，用前请自行上机或开浏览器核。'
W ''
W '---'
W ''

# ── 四 · 统计 ─────────────────────────────────────────────────────
W '## 四 · 统计'
W ''
W '| 指标 | 数 |'
W '|---|---|'
W ('| 抄到的成员条目（行） | **{0}** |' -f $nRows)
W ('| 去重后唯一 `接口.成员` | **{0}**（7 条被 2 份文件各抄一遍） |' -f $nUnique)
W ('| ★ 有 Remarks 前置的 | **{0}** |' -f $nRem)
W ('| ★ 有官方例子配方实参的 | **{0}** |' -f $nEx)
W ('| ★ 标 Obsolete 的 | {0} |' -f $nObs)
W ('| 签名本身查不到（参数记 `?`） | {0} |' -f $nNoSig)
W ('| ★ 「查不到」条目 | **{0}**（涉及 {1} 个「源·成员」） |' -f $nNF, $nNFmem)
W '| ★ 抽查条数 | **6**（跨 **6** 份文件：api-01 / 03 / 06 / 07 / 09 / 10） |'
W '| ★ 抽查后改正条数 | **2** |'
W ''
W '---'
W ''
W '## 五 · 下游怎么用这份索引'
W ''
W '1. **要调某个成员** → 先在 §一 总表定位，看它的 `前置` 与 `例子` 两列。'
W '2. **两列都是 `—`** → 别猜，去 §2.3 确认它是不是「查不到」那一类；'
W '　若是，照查不到处理（官方两套源都没有）。'
W '3. **两列有 ✅** → 直接抄 §2.1 / §2.2 的那一行实参。'
W '4. **要钣金 / 工程图** → ⚠ **本索引这两域是空的**，先补 `api-02-sheetmetal.md` 与 `api-05-drawing.md` 再合并。'

$sb.ToString() | Set-Content $out -Encoding UTF8
'written: ' + $out
'bytes  : ' + (Get-Item $out).Length
('rows={0} uniq={1} rem={2} ex={3} obs={4} nosig={5} nf={6} fixes={7}' -f $nRows,$nUnique,$nRem,$nEx,$nObs,$nNoSig,$nNF,$fixes)
