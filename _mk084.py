import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

# ── 事实 104 ────────────────────────────────────────────────────────
K = Path(r"D:\AI\SW\docs\known-facts.md")
tk = K.read_text(encoding="utf-8")
FACT = "| 104 | " + "".join([
    "**「看到异常就定性」是**误判之源** —— `CreateChamfer` 判成「架构性限制」，其实**倒角已经建成**了** —— ",
    "2026-10-01（轮 164）：仓库 docstring（轮 122）看到 `type=2` 报 `com_error 0x80010105`，",
    "就判 `create_sketch_chamfer` 属「**pywin32 到不了需要真实指针的接口**」这一**架构性限制**，",
    "⚠ 并按**事实 53** 停手（**当时看是对的**：那是个规范的动作）。",
    "★★★ 但轮 164 用 `tools/probe_chamfer_forms.py` **逐类型试 + 回读线段数**：",
    "`type=0`（默认）/ `type=1` ⇒ 段数 **2 → 2**（没变）· 返回 `None`；",
    "**`type=2`（`distance_equal`）⇒ 段数 `2 → 3`（倒角真的建出来了）**，",
    "只是**返回对象拿不到**（那个 `com_error` 是在**取返回值**那一步抛的）。",
    "⇒ ★★ 真正的限制是「**拿不到返回对象**」，**不是**「做不了倒角」。",
    "★ **根因**：轮 122 **只看异常、没回读副作用** ⇒ 与**事实 94**（「不信返回值，回读状态」）同源；",
    "⇒ 扩展一句：**也别只信异常** —— 异常可能只发生在**取值**那一步。",
    "★ 已修：`create_sketch_chamfer` 改为**回读线段数**判定（建成则返回 `None` 而不抛）；",
    "拆出独立条目 **`sketch_chamfer`（`verified`）**，真机 **10/10**（段数 2 → 3）；",
    "`sketch_edit_ops` **仍为 `stitched`**（`sketch_mirror` / `convert_entities` 本轮未单独取证）。",
    "★★★ **同一轮我还踩了**事实 61 那个坑**（如实记）**：我用「按行切分字符串」的方式改",
    "`sw_sketch_edit.py` ⇒ **切多了，删掉 `sketch_mirror` 与 `convert_entities` 共 90 行**",
    "（`git diff --stat` = `46 insertions, 90 deletions`）⇒ 回归当场 **9 failed**。",
    "⇒ ★ 修法照 61 的定则：**`git checkout --` 恢复 → 改用 `edit` 工具逐处改** ⇒ `+44/-4`（**只加不删**）",
    "⇒ 真机 10/10 · 契约 16 passed · 回归 1246 passed。",
    "⚠ **61 的定则我明明知道**（「批量脚本跑完先看 `git diff --stat`，有 deletions 就当成自己的 bug」）",
    "⇒ ★ 教训：**知道定则 ≠ 会照着做**；定则要变成**动作的固定顺序**（改完先看 stat）才有用。",
    " | `tools/probe_chamfer_forms.py`；`tools/verify_sketch_edit_smoke.py`（**10/10**）；",
    "`scripts/sw_sketch_edit.py`；事实 28 / 47 / 53 / 61 / 94 |",
])
if "| 104 |" not in tk:
    K.write_text(tk.rstrip() + "\n\n" + FACT + "\n", encoding="utf-8")
    print("  ok known-facts 已加 104")
else:
    print("  已有 104")

# ── Spec Kit 084 ────────────────────────────────────────────────────
S = Path(r"D:\AI\SW\specs\084-chamfer-was-misjudged")
S.mkdir(parents=True, exist_ok=True)
spec = """# 084 · `CreateChamfer` 被判「架构性限制」是**误判** —— 倒角其实建成了

**Status**: Implemented（轮 164）· ✅ **`sketch_chamfer` 升 `verified`**

## 一、动机（A4 的正面工作）
5 条 `stitched` 里 **`sketch_edit_ops` 最近**（8/10，只有倒角失败）⇒ 修好即可升 `verified`。

## 二、★★★ 真机现象与仓库文档**不一致**
```
仓库 docstring（轮 122）：type=2 ⇒ **com_error 0x80010105**（判为"架构性限制"，按事实 53 停手）
**轮 164 真机**（默认 type=0）：**返回 None**（不是 com_error）
⇒ ★★ 表现不一样 ⇒ 按「一条的性质不能推广成整族」的纪律，**值得逐类型试**
```

## 三、★★ 逐类型试 + **回读线段数**（`tools/probe_chamfer_forms.py`）
```
type=0（默认 distance_angle，角度 0）  ⇒ 段数 2 → 2（没变）· 返回 None
type=0（角度 45°）                     ⇒ 段数 2 → 2（没变）· 返回 None
type=1（distance_distance 5/3）       ⇒ 段数 2 → 2（没变）· 返回 None
type=2（distance_equal，d=5）         ⇒ 段数 **2 → 3**（**变了 ✚**）· com_error 0x80010105
```
⇒ ★★★ **`type=2` 的倒角真的建出来了** —— 那个 `com_error` 是在**取返回值**（`SketchSegment`）
那一步抛的，**不影响倒角本身**。
⇒ ★★ 真正的限制是「**拿不到返回对象**」，**不是**「做不了倒角」。

## 四、★ 根因（一条可复用的）
```
轮 122 **只看异常、没回读副作用** ⇒ 与**事实 94**（「不信返回值，回读状态」）同源
⇒ 扩展一句：**也别只信异常** —— 异常可能只发生在**取值**那一步。
```

## 五、★ 修法与取证
```
修：create_sketch_chamfer 改为**回读线段数**判定（建成则返回 None 而不抛）
拆：独立条目 `sketch_chamfer`（level: verified）—— 因为冒烟**只覆盖了倒角这一条**
    ★ 这正是「一条的性质不能推广成整族」的**正面应用**：
      `sketch_edit_ops`（含 mirror / convert_entities）**仍为 stitched**
取：python tools/verify_sketch_edit_smoke.py ⇒ **10/10 verdict: pass**（段数 2 → 3）
```

## 六、★★★ 同一轮我还踩了**事实 61** 那个坑（如实记）
```
我用「按行切分字符串」的方式改 sw_sketch_edit.py ⇒ **切多了**，
删掉 `sketch_mirror` 与 `convert_entities` 共 **90 行**（git diff --stat: 46 insertions, 90 deletions）
⇒ 回归当场 **9 failed**
⇒ 修法照 61 的定则：**git checkout -- 恢复 → 改用 `edit` 工具逐处改** ⇒ `+44/-4`（**只加不删**）
⇒ 真机 10/10 · 契约 16 passed · 回归 1246 passed
⚠ **61 的定则我明明知道** ⇒ ★ 教训：**知道定则 ≠ 会照着做**；
  定则要变成**动作的固定顺序**（改完先看 `git diff --stat`）才有用。
```

## 七、判据
| ID | 判据 |
|---|---|
| SC-8401 | ★★ 发现「真机现象」与「仓库文档」**不一致** ⇒ 值得重验 |
| SC-8402 | ★★★ **逐类型试 + 回读线段数** ⇒ 定位 `type=2` 能成 |
| SC-8403 | ★★★ **更正**「架构性限制」这个定性（真因是**拿不到返回对象**）|
| SC-8404 | ★ 修 `create_sketch_chamfer`（回读线段数判定）|
| SC-8405 | ★★ 拆出 `sketch_chamfer`（`verified`，真机 **10/10**）· `sketch_edit_ops` 留 `stitched` |
| SC-8406 | ★★★ **如实记下自己踩的事实 61 那个坑**（-90 行）与修法 |
| SC-8407 | 能力 **37 → 38**（verified **31 → 32**）；门禁 + 回归不退化（回归 **1246 passed**）|

## ⚠ 明确记下的限度
* ⚠ 只证「**线段数 2 → 3**」（倒角建出来了），**不证倒角距离 5mm 的数值对不对**；
* ⚠ `sketch_mirror` / `convert_entities` **仍未单独取证** ⇒ `sketch_edit_ops` 留 `stitched`；
* ⚠ `type=0`/`type=1` **为什么不做任何事**，**未查明**（只记录了它们的表现）。
"""
plan = """# 084 · Plan

## 步骤
1. 5 条 `stitched` 里挑最近的 `sketch_edit_ops`（8/10，只差倒角）
2. ★ 发现真机现象（返回 None）与仓库文档（com_error）**不一致**
3. ★★ 写探针：**逐类型试 + 每次回读线段数**
4. ⇒ 定位 **`type=2` 段数 2 → 3**（倒角真的建成了）
5. ⇒ ★★★ 更正轮 122 的「架构性限制」定性
6. 修 `create_sketch_chamfer` + 拆分条目
7. ⚠ 中途我切多了删掉 90 行 ⇒ **git checkout 恢复 + 改用 edit**（事实 61）
8. 事实 104 → 门禁 + 回归 → 收工

## 风险与对策
| 风险 | 对策 |
|---|---|
| 看到异常就定性 | ★ **回读副作用**（本轮的核心）|
| 整个 entry 一起升级 | ★ **冒烟只覆盖一条就只升那一条**（拆条目）|
| 批量脚本切多 | ★ **改完先看 `git diff --stat`**（本轮又踩了，已记）|
| 只证"没抛异常" | ★ 判据是**线段数变化**（空操作不变）|
"""
tasks = """# 084 · Tasks（全部完成，轮 164）

- [x] T-8401 逐类型判别 `→ 验收:` `python tools/probe_chamfer_forms.py`（type2 段数 2→3）
- [x] T-8402 ★★★ 更正「架构性限制」的定性并修 `create_sketch_chamfer`
- [x] T-8403 真机冒烟 `→ 验收:` `python tools/verify_sketch_edit_smoke.py`（**10/10**）
- [x] T-8404 拆出 `sketch_chamfer`（verified）+ 更正 `sketch_edit_ops`
- [x] T-8405 契约测试 `→ 验收:` `python -m pytest tests/test_sw_sketch_edit_contract.py -q`（**16 passed**）
- [x] T-8406 事实 104 + 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
"""
converge = """# 084 · Converge

**Converged**: 2026-10-01（轮 164）

## 一、结果
| 判据 | 结论 |
|---|---|
| SC-8401 现象与文档不一致 | ✅ |
| SC-8402 逐类型 + 回读线段数 | ✅ type2 能成 |
| SC-8403 更正定性 | ✅ |
| SC-8404 修函数 | ✅ |
| SC-8405 拆条目 | ✅ verified 31 → 32 |
| SC-8406 记下自己踩的坑 | ✅ -90 行 |
| SC-8407 门禁 + 回归 | ✅ `release_check` exit 0 · **1246 passed** |

## 二、★★★ 「看到异常就定性」是误判之源
```
轮 122：`com_error 0x80010105` ⇒ 判「架构性限制、到不了」⇒ **误判**
轮 164：**回读线段数** ⇒ 段数 2 → 3 ⇒ **倒角其实建成了**
⇒ ★ 那个 com_error 只在**取返回值**那一步抛 —— "取值失败" ≠ "动作失败"
★ 与事实 94（不信返回值、回读状态）**同源**，而本轮把它**扩展**成：
  **也别只信异常。**
```

## 三、★ 「一条的性质不能推广成整族」的**正面应用**
```
链条另一头：**也不该把「一条验过」推广成「整族可用」**
⇒ 冒烟**只覆盖了倒角**（`sketch_mirror` / `convert_entities` 各 0 次）
⇒ ★ 所以**拆条目**：`sketch_chamfer` 升 `verified`，`sketch_edit_ops` 留 `stitched`
★ 这是同一条纪律的**两个方向**：既不许"一条坏 ⇒ 全族坏"，也不许"一条好 ⇒ 全族好"。
```

## 四、⚠ 我自己踩的坑（事实 61）
```
按行切分改 sw_sketch_edit.py ⇒ **删掉 90 行**（mirror + convert_entities）⇒ 回归 9 failed
⇒ git checkout 恢复 + 改用 edit 工具 ⇒ +44/-4（只加不删）⇒ 全绿
★ 61 的定则我**明明知道** ⇒ 教训：**知道定则 ≠ 会照着做**；
  定则要变成**动作的固定顺序**（改完先看 git diff --stat）才有用。
```

## 五、未查证
* ⚠ 只证**线段数变化**，不证倒角**距离 5mm** 的数值；
* ⚠ `type=0`/`type=1` **为什么不做任何事**，未查明；
* ⚠ `sketch_mirror` / `convert_entities` **仍未单独取证**。
"""
for name, text in (("spec.md", spec), ("plan.md", plan), ("tasks.md", tasks), ("converge.md", converge)):
    (S / name).write_text(text, encoding="utf-8")
    print("  written %s" % name)

# ── ROADMAP 游标 ────────────────────────────────────────────────────
R = Path(r"D:\AI\SW\docs\ROADMAP.md")
B = """           483 🎯 **Spec Kit `084`：`CreateChamfer` 被判「架构性限制」是****误判**** —— 倒角其实建成了**（轮 164）——
               动机（A4 的正面工作）：5 条 `stitched` 里 **`sketch_edit_ops` 最近**（8/10，只差倒角）。
            484 ★★★ **真机现象与仓库文档**不一致****：
               ```
               仓库 docstring（轮 122）：type=2 ⇒ **com_error 0x80010105**（判为"架构性限制"，按事实 53 停手）
               **轮 164 真机**（默认 type=0）：**返回 None**（不是 com_error）
               ⇒ ★★ 表现不一样 ⇒ 按「一条的性质不能推广成整族」的纪律，**值得逐类型试**
               ```
            485 ★★ **逐类型试 + 每次回读线段数**（`tools/probe_chamfer_forms.py`）：
               ```
               type=0（默认 distance_angle，角度 0）  ⇒ 段数 2 → 2（没变）· 返回 None
               type=0（角度 45°）                     ⇒ 段数 2 → 2（没变）· 返回 None
               type=1（distance_distance 5/3）       ⇒ 段数 2 → 2（没变）· 返回 None
               type=2（distance_equal，d=5）         ⇒ 段数 **2 → 3**（**变了 ✚**）· com_error 0x80010105
               ```
               ⇒ ★★★ **`type=2` 的倒角真的建出来了** —— 那个 `com_error` 是在**取返回值**
                 （`SketchSegment`）那一步抛的，**不影响倒角本身**。
               ⇒ ★★ 真正的限制是「**拿不到返回对象**」，**不是**「做不了倒角」。
               ★ **根因**：轮 122 **只看异常、没回读副作用** ⇒ 与**事实 94**（不信返回值、回读状态）同源
                 ⇒ 扩展一句：**也别只信异常** —— 异常可能只发生在**取值**那一步。
            486 ★ **修法与取证**：`create_sketch_chamfer` 改为**回读线段数**判定（建成则返回 `None` 而不抛）；
               拆出独立条目 **`sketch_chamfer`（`verified`）** ⇒ 真机 **10/10**（段数 2 → 3）；
               `sketch_edit_ops` **仍为 `stitched`**（`sketch_mirror` / `convert_entities` 本轮未单独取证）。
               ★★ 这是「一条的性质不能推广成整族」的**正面应用** ——
                 **两个方向都不许**：既不许「一条坏 ⇒ 全族坏」，也不许「一条好 ⇒ 全族好」。
            487 ⚠⚠⚠ **同一轮我还踩了**事实 61** 那个坑（如实记）**：我用「按行切分字符串」的方式改
               `sw_sketch_edit.py` ⇒ **切多了，删掉 `sketch_mirror` 与 `convert_entities` 共 90 行**
               （`git diff --stat` = `46 insertions, 90 deletions`）⇒ 回归当场 **9 failed**。
               ⇒ 修法照 61 的定则：**`git checkout --` 恢复 → 改用 `edit` 工具逐处改**
                 ⇒ `+44/-4`（**只加不删**）⇒ 真机 10/10 · 契约 16 passed。
               ⚠ **61 的定则我明明知道** ⇒ ★ 教训：**知道定则 ≠ 会照着做**；
                 定则要变成**动作的固定顺序**（改完先看 `git diff --stat`）才有用。
            488 能力 **37 → 38**（verified **31 → 32**）· 门禁 + `release_check` exit 0 ·
               回归 **1246 passed**。
               ⚑ **未查证**：⚠ 只证「**线段数 2 → 3**」（倒角建出来了），**不证倒角距离 5mm 的数值对不对**；
                 ⚠ `type=0`/`type=1` **为什么不做任何事**，**未查明**；⚠ `sketch_mirror` / `convert_entities`
                 **仍未单独取证** ⇒ `sketch_edit_ops` 留 `stitched`。
               下轮候选：① 给 `sketch_mirror` / `convert_entities` 各自取证（补上 `sketch_edit_ops` 的另一半）；
               ② 顺 `com_error 0x80010105` 这个线索回查：**还有哪些能力是被"只看异常"误判的**？
               ③ 回到「真缺」继续补。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None, "找不到『阻塞:』锚点"
before = "".join(lines)
if re.search(r"^\s+483 ", before, re.M):
    print("  游标 483 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+488 ", R.read_text(encoding="utf-8"), re.M), "复核失败"
    print("  复核: 488 行已存在 ✓")
