import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

# ── 事实 103 ────────────────────────────────────────────────────────
K = Path(r"D:\AI\SW\docs\known-facts.md")
tk = K.read_text(encoding="utf-8")
FACT = "| 103 | " + "".join([
    "**补上第 37 个能力条目「标准件（Toolbox 索引）」—— 「有实现、有工具、有数据，但没有条目」** —— ",
    "2026-10-01（轮 163）：`scripts/sw_toolbox_index.py`（97 行 · 4 个公开函数 ",
    "`load_index` / `list_standards` / `search` / `part_path`）**早已实现**、`server.py` 也把它暴露成工具，",
    "⚠ 但 `capabilities.yaml` 里 **`toolbox` / `标准件` / `sw_toolbox_index` 三个词各出现 0 次** ⇒ ",
    "★ 这是 **A1/A4 的实打实空白**（有实现无条目）—— 与轮 117 发现的 `sw_sketch` 同一类。",
    "★ **实跑取证**（这就是 `verified` 要的「我们自己的运行证据」）：",
    "`load_index()` ⇒ dict · `list_standards()` ⇒ **19** 套标准 · `len(load_index()['parts'])` ⇒ **1844** 个零件 · ",
    "`search('bearing')` ⇒ **184** 条。",
    "★★ **加条目时被两个门禁当场教育**（都是好正例）：",
    "① **「R12 · 清单形状」抓到 `source` 不在枚举内** —— 我写了 `own-data`，",
    "   正确值是 **`original`**（枚举是 `merged`/`mixed`/`original`/`undetermined`/`upstream`…）",
    "   ⇒ ★ **枚举不是随手编的**，门禁在尽职；",
    "② **`test_unattended_equivalence` 红了** —— 它拿**黄金基线** `tests/unattended_baseline.json` 比对",
    "   「允许无人值守的集合」，而我这条带了 `unattended` ⇒ ★ 更新基线**要讲得出理由**：",
    "   它是**只读索引查询**（无 COM、无文件写入）⇒ 适合无人值守；且门禁「R11 · 授权真源」已 PASS。",
    "   ⇒ **只把这一项加进 `allowed`**（8 → 9），不整体重抓（免得掩盖别的变化）。",
    "★★★ **我这一轮的**第一次**尝试是一份失败判据（如实记）**：我写脚本按「文件名有没有被任何条目提到」",
    "扫「有实现无条目」，得到 **121/125** —— 一眼假：`sw_part.py`（32 个公开函数）显然被 ",
    "`part_and_features` 覆盖。根因：**36 个条目大多不写模块名，只写「能力」** ⇒ ",
    "★ 这是**事实 51**（「分析范围要贴合代码的组织单元」）的又一次实例 —— ",
    "**这次的组织单元是「语义域」，而我扫的是「文件名字符串」** ⇒ **该判据不成立、已弃用**。",
    " | `capabilities.yaml` 的 `standard_parts_toolbox`；`scripts/sw_toolbox_index.py`；",
    "`tests/unattended_baseline.json`；事实 51 / 74；轮 117 |",
])
if "| 103 |" not in tk:
    K.write_text(tk.rstrip() + "\n\n" + FACT + "\n", encoding="utf-8")
    print("  ok known-facts 已加 103")
else:
    print("  已有 103")

# ── Spec Kit 083 ────────────────────────────────────────────────────
S = Path(r"D:\AI\SW\specs\083-standard-parts-toolbox-entry")
S.mkdir(parents=True, exist_ok=True)
spec = """# 083 · 补第 37 个能力条目「标准件（Toolbox 索引）」—— A1/A4 的实打实补格

**Status**: Implemented（轮 163）

## 一、| 起因（换题）
`080`~`082` 三轮都花在「在上下文编辑」这条链上，未打通。
⇒ ★ 按**事实 53**（同一处 ≥3 次即停）**换题**，回到目标核心：**A1/A4「有实现、有能力，但没有条目」**。

## 二、★★★ 先做了一次**失败的扫描**（如实记）
```
我想扫出所有「有实现无条目」的模块：按「文件名有没有被任何条目提到」判 ⇒ **121/125**
⇒ 一眼假：sw_part.py（32 个公开函数）显然被 `part_and_features` 覆盖
根因：**36 个条目大多不写模块名，只写「能力」**
⇒ ★ 这是**事实 51**（「分析范围要贴合代码的组织单元」）的又一次实例 ——
   **这次的组织单元是「语义域」，而我扫的是「文件名字符串」**
⇒ **该判据不成立，已弃用**（不接门禁）。
```

## 三、★ 改查一个**可硬核实**的：`sw_toolbox_index`
```
文件在（97 行）· 4 个公开函数：load_index / list_standards / search / part_path
server.py **提到它** ⇒ 有 MCP 工具
capabilities.yaml：`toolbox` **0 次** · `标准件` **0 次** · `sw_toolbox_index` **0 次**
⇒ ★ 典型的「**有实现、有工具、有数据，但没有条目**」（与轮 117 的 `sw_sketch` 同一类）
```

## 四、★ 实跑取证（`verified` 要的「我们自己的运行证据」）
```
load_index() ⇒ dict（键 source_root / note / standards / count / parts）
list_standards() ⇒ **19** 套标准（GB / Ansi Inch / DIN / JIS / ISO / KS / Unistrut / AS …）
len(load_index()['parts']) ⇒ **1844** 个零件
search('bearing') ⇒ **184** 条（检索可用）
```

## 五、★★ 加条目时**被两个门禁当场教育**（都是好正例）
```
① 「R12 · 清单形状」：`source='own-data'` **不在枚举内** ⇒ 正确值 **`original`**
   ⇒ ★ **枚举不是随手编的**，门禁在尽职
② `test_unattended_equivalence` 红了：它拿**黄金基线**比对「允许无人值守的集合」，
   而我这条带 `unattended` ⇒ 更新基线**要讲得出理由**：
   它是**只读索引查询**（无 COM、无文件写入）⇒ 适合无人值守；且「R11 · 授权真源」已 PASS
   ⇒ **只把这一项加进 `allowed`**（8 → 9），**不整体重抓**（免得掩盖别的变化）
```

## 六、判据
| ID | 判据 |
|---|---|
| SC-8301 | ★★★ **实跑取证**：19 套 / 1844 零件 / search 184 条 |
| SC-8302 | ★★ 补条目 `standard_parts_toolbox`（`level: verified`，限度**照抄模块头**）|
| SC-8303 | ★★ 门禁抓出 `source` 枚举错 ⇒ 改成 `original` |
| SC-8304 | ★★ 基线更新**只加一项**且写得出理由 |
| SC-8305 | ★ 能力数 **36 → 37**（verified **30 → 31**）；`union_conventions` exit 0 |
| SC-8306 | ★★ **如实记下我那份失败的扫描判据**（121/125 假阳性）|
| SC-8307 | 事实 103 入库；门禁 + 回归不退化（回归 **1246 passed**）|

## ⚠ 明确记下的限度
* ⚠ 索引**不含型号→尺寸的工程数据**（导轨行程 / 丝杆导程 / 额定载荷…）—— 模块头明写，**照抄进限度**；
* ⚠ 索引来自**本机** `D:\\SOLIDWORKS Data\\browser\\` ⇒ **换机器要重建**；
* ⚠ 只给**路径**，**不代为插入装配体**（插入仍走 `sw_assembly.add_component`）；
* ⚠ **A1 的整幅地图没有重算** —— 本轮只补了**一个可硬核实的格**，没有全面审计。
"""
plan = """# 083 · Plan

## 步骤
1. `080`~`082` 三轮未打通在上下文链 ⇒ 按**事实 53 换题**
2. ★ 想扫「有实现无条目」⇒ 第一版判据（按文件名）**121/125 假阳性** ⇒ **弃用**
3. ★ 改查一个**可硬核实**的：`sw_toolbox_index`（提案附注提过）
4. ⇒ 核实：实现有、工具有、**条目 0**
5. ★ 实跑取证（19 套 / 1844 零件 / search 184）
6. 补条目 ⇒ ⚠ 门禁抓 `source` 枚举错 ⇒ 改 `original`
7. ⚠ 基线测试红了 ⇒ **只加一项** + 写理由
8. 事实 103 → 门禁 + 回归 → 收工

## 风险与对策
| 风险 | 对策 |
|---|---|
| 拿一个假阳性高的扫描当结论 | ★ **一眼假就弃用**（121/125 里 `sw_part.py` 显然有覆盖）|
| 给枚举随手编值 | ★ 门禁会抓（本轮正是）—— 改用它认的值 |
| 基线整体重抓 | ★ **只加一项**，免得掩盖别的变化 |
| 把「补一格」说成「A1 完成了」 | ★ 限度里写明**整幅地图没重算** |
"""
tasks = """# 083 · Tasks（全部完成，轮 163）

- [x] T-8301 换题 + 第一版扫描判据**弃用**（121/125 假阳性）
- [x] T-8302 ★★★ 核 `sw_toolbox_index` 并**实跑取证**
  `→ 验收:` `python -c "import sw_toolbox_index as tb; print(len(tb.list_standards()), len(tb.load_index()['parts']))"`
  （**19 1844**）
- [x] T-8303 补条目 `standard_parts_toolbox`
- [x] T-8304 修 `source` 枚举 + 更新无人值守基线
  `→ 验收:` `python scripts/check_union_conventions.py`（exit 0）· `pytest tests/test_unattended_equivalence.py`（**7 passed**）
- [x] T-8305 事实 103
- [x] T-8306 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
"""
converge = """# 083 · Converge

**Converged**: 2026-10-01（轮 163）

## 一、结果
| 判据 | 结论 |
|---|---|
| SC-8301 实跑取证 | ✅ 19 / 1844 / 184 |
| SC-8302 补条目 | ✅ level=verified |
| SC-8303 `source` 枚举 | ✅ 门禁抓的，改成 `original` |
| SC-8304 基线只加一项 | ✅ 8 → 9 |
| SC-8305 能力 36 → 37 | ✅ verified 30 → 31 · `union_conventions` exit 0 |
| SC-8306 记下失败判据 | ✅ |
| SC-8307 事实 103 + 门禁 + 回归 | ✅ `release_check` exit 0 · **1246 passed** |

## 二、★★★ 本轮的两个「门禁在尽职」的正例
```
① 「R12 · 清单形状」：`source='own-data'` 不在枚举 ⇒ **当场 FAIL**
   ⇒ ★ 我编的枚举值被挡住 —— 这正是 A3 想要的效果
② `test_unattended_equivalence`：拿**黄金基线**比对「允许无人值守的集合」
   ⇒ 新允许一个能力**必须更新基线**，而那条测试里还有一条
     `test_no_newly_allowed_capability_bypasses_r11` ——
     ★ **说明"新允许一个能力"是被设计过的动作**（要有 R11 依据），不是顺手写的
```

## 三、★ 又一次「判据与分析范围不匹配」（事实 51）—— 这已是**第 4 次**
```
本轮：组织单元是「**语义域**」，我扫的是「**文件名字符串**」⇒ 121/125 假阳性
之前：组织单元是「**文件前缀**」（提案扫 sw_*.py 漏掉 sketch_relations.py）
      「**函数**」（行窗口跨函数吞了别的特征的成员）
      「**同义词集合**」（21 份复制的 modal_dialogs）
⇒ ★★ 四次的共同点：**判据的"范围"与目标的"组织单元"不是同一个东西**。
```

## 四、未查证
* ⚠ 索引**不含型号→尺寸的工程数据**；
* ⚠ 索引来自**本机**目录 ⇒ 换机器要重建；
* ⚠ **A1 的整幅地图没重算** —— 只补了一个可硬核实的格。
"""
for name, text in (("spec.md", spec), ("plan.md", plan), ("tasks.md", tasks), ("converge.md", converge)):
    (S / name).write_text(text, encoding="utf-8")
    print("  written %s" % name)

# ── ROADMAP 游标 ────────────────────────────────────────────────────
R = Path(r"D:\AI\SW\docs\ROADMAP.md")
B = """           478 🎯 **Spec Kit `083`：补第 37 个能力条目「标准件（Toolbox 索引）」—— ****A1/A4 的实打实补格******（轮 163）——
               `080`~`082` 三轮都花在「在上下文编辑」链上未打通 ⇒ ★ 按**事实 53**（同一处 ≥3 次即停）**换题**，
               回到目标核心：**A1/A4「有实现、有能力，但没有条目」**。
            479 ★★★ **先做了一次**失败的扫描**（如实记）**：按「文件名有没有被任何条目提到」扫
               「有实现无条目」⇒ **121/125** ⇒ 一眼假（`sw_part.py` 32 个公开函数显然被
               `part_and_features` 覆盖）⇒ 根因：**36 个条目大多不写模块名，只写「能力」**
               ⇒ ★ 这是**事实 51**（「分析范围要贴合代码的组织单元」）的又一次实例 ——
                 **这次的组织单元是「语义域」，而我扫的是「文件名字符串」** ⇒ **该判据不成立、已弃用**。
            480 ★ **改查一个可硬核实的**：`scripts/sw_toolbox_index.py`（97 行 · 4 个公开函数）
               **早已实现**、`server.py` 也把它暴露成工具，⚠ 但 `capabilities.yaml` 里
               **`toolbox` / `标准件` / `sw_toolbox_index` 三个词各出现 0 次** ⇒
               ★ 典型的「**有实现、有工具、有数据，但没有条目**」（与轮 117 的 `sw_sketch` 同一类）。
               ★ **实跑取证**（这就是 `verified` 要的「我们自己的运行证据」）：
               `list_standards()` ⇒ **19** 套 · `len(load_index()['parts'])` ⇒ **1844** 个零件 ·
               `search('bearing')` ⇒ **184** 条。
            481 ★★ **加条目时被两个门禁当场教育**（都是**好正例**）：
               ```
               ① 「R12 · 清单形状」：`source='own-data'` **不在枚举内** ⇒ **当场 FAIL**
                  ⇒ 正确值 **`original`** ⇒ ★ **枚举不是随手编的**，门禁在尽职
               ② `test_unattended_equivalence` 红了 —— 它拿**黄金基线** `tests/unattended_baseline.json`
                  比对「允许无人值守的集合」，而我这条带 `unattended`
                  ⇒ ★ 更新基线**要讲得出理由**：它是**只读索引查询**（无 COM、无文件写入）
                    ⇒ 适合无人值守；且「R11 · 授权真源」已 PASS
                  ⇒ **只把这一项加进 `allowed`**（8 → 9），**不整体重抓**（免得掩盖别的变化）。
                  ★ 而那条测试里还有 `test_no_newly_allowed_capability_bypasses_r11` ——
                    **说明「新允许一个能力」是被设计过的动作**，不是顺手写的。
               ```
            482 ★★ **能力数 36 → 37（verified 30 → 31）** · `union_conventions` exit 0 ·
               `release_check` exit 0 · 回归 **1246 passed**。
               ★★★ 「判据与分析范围不匹配」这已是**第 4 次**：（本轮）语义域 vs 文件名字符串 ·
                 （提案）文件前缀 · 行窗口跨函数 · 同义词集合 ——
                 ★ 四次的共同点：**判据的「范围」与目标的「组织单元」不是同一个东西**。
               ⚑ **未查证**：⚠ 索引**不含型号→尺寸的工程数据**（模块头明写，已照抄进限度）；
                 ⚠ 索引来自**本机**目录 ⇒ 换机器要重建；⚠ 只给**路径**、**不代为插入装配体**；
                 ⚠ **A1 的整幅地图没重算** —— 本轮只补了**一个可硬核实的格**，**没有全面审计**。
               下轮候选：① 继续补同类空白（**用语义域对照，不要再按文件名扫**）；
               ② 回到在上下文链但要**先设计能证伪的判据**；③ 给剩下 5 条 `stitched` 冒烟。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None, "找不到『阻塞:』锚点"
before = "".join(lines)
if re.search(r"^\s+478 ", before, re.M):
    print("  游标 478 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+482 ", R.read_text(encoding="utf-8"), re.M), "复核失败"
    print("  复核: 482 行已存在 ✓")
