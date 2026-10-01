import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
S = Path(r"D:\AI\SW\specs\026-enum-dump-coverage")
S.mkdir(parents=True, exist_ok=True)

spec = """# 026 · 补齐枚举门禁的**转储覆盖**：75 条「查不到」→ **0**

**Status**: Implemented（轮 107）

## 背景
`025` 建的门禁（第 16 道）实跑时报 **75 条「查不到」**（多为 Simulation 的 `sws*` 枚举），
当时记为「未查证」。本轮把它查清。

## 查到的事实
```
`swsAnalysisStudyTypeBuckling` 落在 **SolidWorks.Interop.cosworks.dll**
  ⇒ 那是**另一个程序集**（Simulation / COSMOSWorks），不是 sldworks
而 `_raw\\reflect\\enum_cosworks.txt` **已有对应转储**（363 个枚举节，格式完全相同）
```
★ ⇒ **不是"官方没有"，是我只读了一份转储。**

## 做法
把门禁从「读一份转储」改成「**读多份并合并**」：
* `_raw\\enum_values_sldworks.txt`（sldworks 程序集）
* `_raw\\reflect\\enum_cosworks.txt`（cosworks 程序集）
* 合并顺序即优先级（`sw*` 与 `sws*` 前缀不重叠，实测无冲突）；
* 记下**每个成员来自哪份转储**；
* `DSH_ENUM_DUMP` 支持多份（`;` 分隔）。

## 结果
```
                 轮 106        轮 107
转储份数            1             2
合并成员         8,216         **10,588**
有据可查的值       15             **90**（全部一致）
查不到             75             **0**
两源冲突            1             1（仍是 024 那个）
```

## 判据
| ID | 判据 |
|---|---|
| SC-2201 | 门禁读**≥2 份**转储并合并 |
| SC-2202 | ★ **`sws*` 能查到**：`swsAnalysisStudyTypeBuckling == 2`，且记下来自 cosworks |
| SC-2203 | 合并时**先出现的赢**（冲突时行为确定）|
| SC-2204 | 实跑 **0 条查不到**，且仍报得出 024 那处冲突 |
| SC-2205 | 全拿不到转储时 **SKIP exit 0**（便携性）|
| SC-2206 | 门禁 + 回归不退化（回归 **1074 passed**）|

## ⚠ 本轮自己踩的坑
改 `gate-classification.json` 时把 Windows 路径写进 JSON 字符串
⇒ **非法转义 `\\e`** ⇒ JSON 解析失败 ⇒ `gate_wiring` / `release_check` 连着红。
⇒ 改用正斜杠。★ 教训：**往 JSON 里塞 Windows 路径要先想转义**。
"""

plan = """# 026 · Plan

## 步骤
1. 查 75 条「查不到」的成员到底属于哪个程序集
   ⇒ 搜遍 `api\\redist` 下所有 DLL ⇒ 命中 **cosworks.dll**
2. 发现 `_raw/reflect/enum_cosworks.txt` **已有**该程序集的枚举转储
3. ⇒ **不新建转储**（不重造），改门禁读多份
4. 加测试：`sws*` 能查到 + 合并优先级
5. ★ 改 `gate-classification.json` 时踩了 **JSON 转义**（Windows 路径）⇒ 修正
6. 收工

## 风险与对策
| 风险 | 对策 |
|---|---|
| 以为"官方没有"就到此为止 | ★ 先确认是**哪个程序集**，再找该程序集的转储 |
| 自己再造一份转储 | **不造** —— 已有 `enum_cosworks.txt` |
| 往 JSON 里写 Windows 路径 | 用正斜杠（本轮踩过）|
"""

tasks = """# 026 · Tasks（全部完成，轮 107）

- [x] T-2201 搜遍 `api\\redist` 下所有 DLL ⇒ 定位 `sws*` 在 **cosworks.dll**
- [x] T-2202 确认 `_raw/reflect/enum_cosworks.txt` 已含该程序集（363 个枚举节）
- [x] T-2203 门禁改成读**多份**转储并合并（`DUMPS` + `parse_dumps`）
  `→ 验收:` `python scripts/check_enum_values_vs_reflection.py`（**0 条查不到**）
- [x] T-2204 加测试：`sws*` 可查 + 合并优先级（**10 passed**）
  `→ 验收:` `python -m pytest tests/test_enum_values_gate.py -q`
- [x] T-2205 更新 `docs/gate-classification.json`（并修正 JSON 转义）
  `→ 验收:` `python scripts/check_gate_wiring.py`（16 道全部接线）
- [x] T-2206 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
"""

converge = """# 026 · Converge

**Converged**: 2026-10-01（轮 107）

## 一、结果
| 判据 | 结论 |
|---|---|
| SC-2201 读 ≥2 份转储并合并 | ✅ 合并 **10,588** 个成员 |
| SC-2202 `sws*` 能查到 | ✅ `swsAnalysisStudyTypeBuckling == 2`，来源记为 cosworks |
| SC-2203 合并优先级确定 | ✅ 先出现的赢（测试钉住）|
| SC-2204 实跑 0 条查不到 + 仍报 024 冲突 | ✅ **90 条全部一致** · 1 处冲突 |
| SC-2205 拿不到转储则 SKIP | ✅ |
| SC-2206 门禁 + 回归 | ✅ `release_check` exit 0 · **1074 passed** |

## 二、★ 这一轮把「未查证」兑现成了「查清」
`025` 结束时写的是：
> **75 条"查不到"未逐条核** —— 多半来自 `swsimulation` 程序集（不在本转储里），
> **未验证**是否有对应的反射源可查。

本轮查清：**有** —— 它们在 **cosworks.dll**，而对应的转储**早就存在**。
★ **⇒ 那句"未查证"里藏着一个错误前提**：我当时猜是 `swsimulation`（其实没有这个程序集名），
真正的程序集是 **cosworks**（Simulation 的前身叫 COSMOSWorks）。
**猜测写进"未查证"里，读起来像事实。**

## 三、门禁现在的覆盖（可复算）
```
2 份转储 · 10,588 个成员 · 代码里 90 条「值 + 官方成员名」
  ├─ 90 条与出厂反射一致
  ├─  0 条查不到
  └─  1 处两源冲突（swSketchChamfer_DistanceDistance：反射 1 · md −1）
```
⇒ **代码里每一个写了官方成员名的枚举值，现在都有据可查、且都对。**

## 四、⚠ 本轮自己踩的坑
改 `gate-classification.json` 时把 Windows 路径 `reflect\\enum_cosworks.txt` 写进 JSON 字符串
⇒ **非法转义 `\\e`** ⇒ JSON 解析失败 ⇒ `gate_wiring` 与 `release_check` **连着红两次**。
⇒ 改用正斜杠。★ **往 JSON 里塞 Windows 路径要先想转义。**

## 五、未查证
* 门禁**不判**「成员名挂的是不是对的枚举」，也**不判**值的语义；
* **还有没有别的程序集**的枚举被我们用到了（本轮只解决了 sldworks + cosworks 两个）；
  其余 interop 程序集（`swmotionstudy` / `swdocumentmgr` / `swdimxpert` / `dsgnchk` /
  `fworks` / `sldcostingapi` / `SWRoutingLib` …）**未逐一检查是否有对应转储**。
"""

for name, text in (("spec.md", spec), ("plan.md", plan), ("tasks.md", tasks), ("converge.md", converge)):
    (S / name).write_text(text, encoding="utf-8")
    print("  written %s" % name)
