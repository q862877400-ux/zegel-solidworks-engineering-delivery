import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

# ── 事实 106 ────────────────────────────────────────────────────────
K = Path(r"D:\AI\SW\docs\known-facts.md")
tk = K.read_text(encoding="utf-8")
FACT = "| 106 | " + "".join([
    "**`IGtolFrame.AddIndicator` 的 `TolType` 只有 5 个合法值；穷尽 20 组后判定「这条后端到不了」** —— ",
    "2026-10-01（轮 166）：`C:/swapi/types/IGtolFrame/AddIndicator.md` 的 Remarks **原文**列出",
    "`TolType` **只能是** `swGcsANG`20 · `swGcsPARALLEL`22 · `swGcsPERP`21 · `swGcsCIRCRUNOUT`25 · `swGcsSYMMETRY`13。",
    "★★ 而 `GTOL_GEOM_SYMBOL` 里另外 **14** 个（`flatness` / `position` / `straightness` …）",
    "**都不在清单里** ⇒ 传它们**必然 `False`** —— 而**契约测试当时正用 `position`(23) 断言它会成功**",
    "（★ 又一次「假对象看不见官方取值限制」）。",
    "★★★ **穷尽式结论**（`tools/probe_gtol_indicator_matrix.py`）：",
    "`BorderType`(0..3) × `TolType`(5 个合法值) = **20 组全试**，",
    "而**每一组的帧都拿到了**（`GetFrame(1)` 非 NULL）⇒ **20 组全返回 `False`**。",
    "⇒ ★ 不是「取值不对」，而是**这条后端（pywin32 迟到绑定）到不了这一个成员** —— ",
    "与**事实 47** 那族同类（多出参 / 需指针的接口）。⚠ 但**证据强度**：47 是「20+ 种形态」，",
    "本轮是「**20 组组合矩阵 + 帧已确认拿到**」。",
    "★ 处置：给 `add_gtol_indicator` 加**清单校验**（错值当场 `ValueError`，不再让它表现出模糊的 `False`）；",
    "拆出 **`gtol_insert`（`verified`）**覆盖「新建 GTol + 帧路径」那半；",
    "`geometric_tolerance` **仍 `stitched`**（含「加指示符」那半，本机到不了）。",
    "★ 这也是本会话**第三次**「取值/形态不对」被读成「做不到」（104 `CreateChamfer` · 105 `AddFrame` 顺序 · 106 本条）。",
    "⚠ 本轮**又两次切坏文件**（事实 61）：一次 `sw_gtol.py`、一次 `test_sw_gtol_contract.py`",
    "（后者是 `t.find(\"import \")` 命中了 `from __future__ import` 中间）",
    "⇒ 两次都靠 `git checkout --` + **改用 `edit` 工具**修好。",
    " | `tools/probe_gtol_indicator_matrix.py`；`scripts/sw_gtol.py`；",
    "`C:/swapi/types/IGtolFrame/AddIndicator.md`；事实 47 / 104 / 105 |",
])
if "| 106 |" not in tk:
    K.write_text(tk.rstrip() + "\n\n" + FACT + "\n", encoding="utf-8")
    print("  ok known-facts 已加 106")
else:
    print("  已有 106")

# ── Spec Kit 086 ────────────────────────────────────────────────────
S = Path(r"D:\AI\SW\specs\086-gtol-indicator-exhaustive")
S.mkdir(parents=True, exist_ok=True)
spec = """# 086 · `AddIndicator` 穷尽 20 组后判定「这条后端到不了」—— 并拆出可用那一半

**Status**: Implemented（轮 166）· ✅ `gtol_insert` 升 `verified`

## 一、动机（顺 `085` 的尾巴）
`085` 把帧路径打通了，但 `AddIndicator` 仍 `False` ⇒ 本轮**先读官方 Remarks**（上轮刚学到的）。

## 二、★★★ Remarks 里藏着**取值限制**
```
C:/swapi/types/IGtolFrame/AddIndicator.md 的 Remarks **原文**列出：
  TolType may be one of only swGtolGeomCharSymbol_e.:
    swGcsANG(20) · swGcsPARALLEL(22) · swGcsPERP(21) · swGcsCIRCRUNOUT(25) · swGcsSYMMETRY(13)
⇒ ★★ 而 GTOL_GEOM_SYMBOL 里另外 **14** 个（flatness / position / straightness …）**都不在清单里**
⇒ 传它们**必然 False** —— 而★**契约测试当时正用 `position`(23) 断言它会成功**
  （又一次「假对象看不见官方取值限制」）
```

## 三、★★★ 穷尽式结论（`tools/probe_gtol_indicator_matrix.py`）
```
BorderType(0..3) × TolType(5 个合法值) = **20 组全试**
★ 每一组的帧**都拿到了**（GetFrame(1) 非 NULL）
⇒ **20 组全返回 False**
⇒ 不是「取值不对」⇒ **这条后端（pywin32 迟到绑定）到不了这一个成员**
  （与事实 47 那族同类：多出参 / 需指针的接口）
```

## 四、★ 处置（三条）
```
① 给 add_gtol_indicator 加**清单校验** ⇒ 错值当场 ValueError
   （过去它表现为模糊的 False，会被读成"到不了"）
② **拆出 `gtol_insert`（verified）** 覆盖「新建 GTol + 帧路径」那一半
③ `geometric_tolerance` **仍 `stitched`**（含「加指示符」那半）
   ★ 与轮 164 倒角那次**同一决策**：**冒烟只覆盖哪一半，就只升哪一半**
```

## 五、判据
| ID | 判据 |
|---|---|
| SC-8601 | ★★ 读 Remarks 找出**取值限制**（只允许 5 个）|
| SC-8602 | ★★ 给函数加**清单校验**（错值当场报）|
| SC-8603 | ★★★ **20 组穷尽矩阵** ⇒ 断定「这条后端到不了」 |
| SC-8604 | ★ 拆出 `gtol_insert`（verified）；`geometric_tolerance` 留 `stitched` |
| SC-8605 | ★★ 改契约测试（它**用了非法值**）+ 写明理由 |
| SC-8606 | 能力 **38 → 39**（verified **32 → 33**）；门禁 + 回归不退化（回归 **1246 passed**）|
| SC-8607 | ⚠ **如实记下本轮又两次切坏文件**（事实 61）|

## ⚠ 明确记下的限度
* ⚠ `AddIndicator` 只是「**这 20 组在这条后端上不成**」⇒ **不排除**换后端（`comtypes`）能成；
* ⚠ 未试 `SetSymbolXml`（XML 路径）—— ⚠ 但它也**需要先拿到 frame**，而 frame 已拿到 ⇒ 值得下次试；
* ⚠ `gtol_insert` 只证「拿到对象」，**不证公差标得对**；
* ⚠ 本轮**两次**切坏文件（`sw_gtol.py` / `test_sw_gtol_contract.py`）⇒ 都用 `git checkout` 恢复 +
  改用 `edit`；★ **「改完先看 `git diff --stat`」这条我仍未养成动作习惯**。
"""
plan = """# 086 · Plan

## 步骤
1. `085` 把帧打通了，`AddIndicator` 仍 False ⇒ **先读官方 Remarks**
2. ★★ Remarks 里找到**取值限制**（只允许 5 个 tol type）
3. ⇒ 改冒烟用清单内的值 ⇒ **仍 False** ⇒ 类型不是唯一卡点
4. ★★★ 做**穷尽矩阵**（4 border × 5 tol = 20 组，每次新 Gtol）
5. ⇒ **20 组全 False，而帧全部拿到** ⇒ 判定「这条后端到不了」
6. ★ 加**清单校验** + 拆出 `gtol_insert`（verified）+ 改契约测试
7. ⚠ 中途两次切坏文件 ⇒ `git checkout` + `edit` 修好
8. 事实 106 → 门禁 + 回归 → 收工

## 风险与对策
| 风险 | 对策 |
|---|---|
| 猜参数 | ★ **先读 Remarks**（本轮正是这么找到取值限制的）|
| 试几个就下结论 | ★ **穷尽矩阵**（20 组，且每次新对象避状态污染）|
| 整个 entry 一起升级 | ★ **拆条目**（只升覆盖到的那半）|
| 契约测试钉着非法值 | ★ 改测试 + **写明是测试用了非法值** |
| 切坏文件 | ⚠ 本轮又两犯 ⇒ **`git checkout` + `edit`**（61 的定则）|
"""
tasks = """# 086 · Tasks（全部完成，轮 166）

- [x] T-8601 读 Remarks 找出取值限制（只允许 5 个 tol type）
- [x] T-8602 加清单校验（错值当场 `ValueError`）
- [x] T-8603 ★★★ 穷尽矩阵 `→ 验收:` `python tools/probe_gtol_indicator_matrix.py`（**20 组全 False**）
- [x] T-8604 拆出 `gtol_insert`（verified）
- [x] T-8605 改契约测试 `→ 验收:` `python -m pytest tests/test_sw_gtol_contract.py -q`（**16 passed**）
- [x] T-8606 事实 106 + 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
"""
converge = """# 086 · Converge

**Converged**: 2026-10-01（轮 166）

## 一、结果
| 判据 | 结论 |
|---|---|
| SC-8601 读 Remarks 找限制 | ✅ 只允许 5 个 |
| SC-8602 清单校验 | ✅ |
| SC-8603 20 组穷尽矩阵 | ✅ 全 False（帧全拿到）|
| SC-8604 拆条目 | ✅ verified 32 → 33 |
| SC-8605 改契约测试 | ✅ 16 passed |
| SC-8606 门禁 + 回归 | ✅ `release_check` exit 0 · **1246 passed** |
| SC-8607 记下两次切坏文件 | ✅ |

## 二、★★ 「取值不对」被读成「做不到」—— 这已是**第三次**
```
事实 104（轮 164）：CreateChamfer —— 「返回值拿不到」被读成「接口到不了」
事实 105（轮 165）：AddFrame      —— 「顺序不对」被读成「帧取不到」
事实 106（轮 166）：AddIndicator  —— 「**取值不在清单里**」被读成「到不了」
⇒ ★★ 三次的共同点：**我试的是这个 API 的某一种用法，却把结论写成了这个 API 的性质。**
⇒ ★ 而三次的**解药都是同一个动作**：**读官方 Remarks**（那里写着用法前提）。
```

## 三、★ 本轮的**排除法**做对了
```
第一次试：清单内的 tol type ⇒ 仍 False ⇒ **类型不是唯一卡点**
第二次：穷尽 20 组（且**每次新 Gtol**，避状态污染）⇒ 全 False，而**帧全部拿到**
⇒ ★ 这才有资格说「**这条后端到不了**」—— **排除法 + 穷尽**，不是"换个写法试试"
```

## 四、未查证
* ⚠ 只是「这 20 组在这条后端上不成」⇒ 不排除换后端（`comtypes`）能成；
* ⚠ 未试 `SetSymbolXml`（XML 路径）—— 但 frame 已拿到 ⇒ **值得下次试**；
* ⚠ `gtol_insert` 只证「拿到对象」，不证公差标得对。
"""
for name, text in (("spec.md", spec), ("plan.md", plan), ("tasks.md", tasks), ("converge.md", converge)):
    (S / name).write_text(text, encoding="utf-8")
    print("  written %s" % name)

# ── ROADMAP 游标 ────────────────────────────────────────────────────
R = Path(r"D:\AI\SW\docs\ROADMAP.md")
B = """           495 🎯 **Spec Kit `086`：`AddIndicator` 穷尽 20 组后判定「这条后端到不了」—— 并拆出可用那一半**（轮 166）——
               `085` 把帧路径打通了，但 `AddIndicator` 仍 `False` ⇒ 本轮**先读官方 Remarks**（上轮刚学到的）。
            496 ★★★ **Remarks 里藏着取值限制**：
               > TolType may be one of only swGtolGeomCharSymbol_e.:
               >   swGcsANG(20) · swGcsPARALLEL(22) · swGcsPERP(21) · swGcsCIRCRUNOUT(25) · swGcsSYMMETRY(13)
               ★★ 而 `GTOL_GEOM_SYMBOL` 里另外 **14** 个（`flatness` / `position` / `straightness` …）
               **都不在清单里** ⇒ 传它们**必然 `False`` —— 而 ★**契约测试当时正用 `position`(23) 断言它会成功**
               （又一次「**假对象看不见官方取值限制**」）。
            497 ★★★ **穷尽式结论**（`tools/probe_gtol_indicator_matrix.py`）：
               ```
               BorderType(0..3) × TolType(5 个合法值) = **20 组全试**
               ★ 每一组的帧**都拿到了**（GetFrame(1) 非 NULL）
               ⇒ **20 组全返回 False**
               ⇒ 不是「取值不对」⇒ **这条后端（pywin32 迟到绑定）到不了这一个成员**
                 （与事实 47 那族同类：多出参 / 需指针的接口）
               ```
               ★ **排除法做对了**：第一次改合法值仍 False（⇒ 类型不是唯一卡点）⇒ 才做**穷尽矩阵**
                 （且**每次新 Gtol**，避状态污染）⇒ **这才有资格说"到不了"**。
            498 ★ **处置三条**：① 给 `add_gtol_indicator` 加**清单校验**（错值当场 `ValueError`，
               不再让它表现为模糊的 `False`）· ② **拆出 `gtol_insert`（verified）** 覆盖「新建 GTol + 帧路径」
               那一半 · ③ `geometric_tolerance` **仍 `stitched`**（含「加指示符」那半）。
               ★★ 与轮 164 倒角那次**同一决策**：**冒烟只覆盖哪一半，就只升哪一半。**
            499 ★★★ **「取值/形态不对」被读成「做不到」—— 这已是第三次**：
               ```
               事实 104（轮 164）：CreateChamfer —— 「**返回值拿不到**」被读成「接口到不了」
               事实 105（轮 165）：AddFrame      —— 「**顺序不对**」被读成「帧取不到」
               事实 106（轮 166）：AddIndicator  —— 「**取值不在清单里**」被读成「到不了」
               ⇒ ★★ 三次的共同点：**我试的是这个 API 的某一种用法，
                 却把结论写成了这个 API 的性质。**
               ⇒ ★ 而三次的**解药都是同一个动作**：**读官方 Remarks**（那里写着用法前提）。
               ```
            500 能力 **38 → 39**（verified **32 → 33**）· 门禁 + `release_check` exit 0 · 回归 **1246 passed**。
               ⚠⚠ **本轮又两次切坏文件**（事实 61）：一次 `sw_gtol.py`、一次 `test_sw_gtol_contract.py`
               （后者是 `t.find("import ")` **命中了 `from __future__ import` 中间**）
               ⇒ 两次都靠 `git checkout --` + **改用 `edit` 工具**修好。
               ★ **「改完先看 `git diff --stat`」这条我仍未养成动作习惯** —— 连着两轮犯规。
               ⚑ **未查证**：⚠ 只是「这 20 组在**这条后端**上不成」⇒ **不排除**换后端（`comtypes`）能成；
                 ⚠ 未试 `SetSymbolXml`（XML 路径）—— 但 frame 已拿到 ⇒ **值得下次试**；
                 ⚠ `gtol_insert` 只证「拿到对象」，**不证公差标得对**。
               下轮候选：① 试 `SetSymbolXml`（frame 已到手，XML 路径值得一搏）；
               ② 顺同一线索查 `surface_modeling` / `mold_tools`（那两条 `stitched` **连 evidence 都没有**）；
               ③ 回到「真缺」继续补。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None, "找不到『阻塞:』锚点"
before = "".join(lines)
if re.search(r"^\s+495 ", before, re.M):
    print("  游标 495 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+500 ", R.read_text(encoding="utf-8"), re.M), "复核失败"
    print("  复核: 500 行已存在 ✓")
