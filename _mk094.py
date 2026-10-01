import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

# ── 事实 114 ────────────────────────────────────────────────────────
K = Path(r"D:\AI\SW\docs\known-facts.md")
tk = K.read_text(encoding="utf-8")
FACT = "| 114 | " + "".join([
    "**「从 docstring 推形参接口」这条路**不成立** —— 实测两处都推错，已回退** —— 2026-10-01（轮 174）。",
    "★ 起因：轮 173 的检查器**抓不到它自己的动机**（`mold_evidence(model)` 的 owner 是**形参**）。",
    "★ 试的退路：**没有 `:param` 段时**，若 **① 函数恰好 1 个形参** 且 **② docstring 里出现的反射接口名恰好 1 个** ⇒ 采纳它。",
    "⚠⚠⚠ **实测（`D:/AI/SW/_verify_param_infer.py`）两处都推错**：",
    "```",
    "① insert_parting_line / insert_parting_surface / insert_shut_off_surface /",
    "   insert_core_cavity_solids / mold_draft_analysis",
    "   ⇒ 推成 **`Feature`**  ← docstring 里的**散文词** `feature` 命中了**接口名 `Feature`**",
    "     ⇒ 于是报「`Feature . FeatureManager` 不在 `IFeature` 上」（**荒谬但「技术上成立」**）",
    "② mold_undercut_detect ⇒ 推成 **`IFeatureManager`**",
    "   ← docstring 提到的是**成员全名** `IFeatureManager.MoldUndercutDetect`，**不是形参的类型**",
    "```",
    "⇒ ★★★ **「恰好 1 个」不等于「它是形参的类型」** ⇒ 该退路**已回退**（命中数从 36 回到 20，`sw_mold` 假阳性清零）。",
    "⇒ ★ **定则**：**显式 = 有依据；推断 = 会错** —— 只认 `:param <名>: <接口名>` 这一种写法。",
    "⚠ **后果**：`mold_evidence` 那种「**散文 docstring + 形参 owner**」**仍然抓不到**（而它是本工具的**动机**）",
    "⇒ ★ 要覆盖它，得走**从调用点推**那条路（`mold_evidence(doc)` ⇒ `doc` 的接口）—— **未做**。",
    "★ 这也**印证了事实 113 的那条教训**（「推不出」不许用兜底值/猜测代替）：",
    "轮 173 的兜底是 **`IObject`**、轮 174 的兜底是 **「docstring 里恰好 1 个接口名」** ——",
    "**两次都是「把不知道伪装成知道」，两次都被真机/实测打回**。",
    " | `scripts/check_member_owner_interface.py` 的 `param_ifaces_from_docstring` 注释；",
    "`D:/AI/SW/_verify_param_infer.py`；事实 53 / 113 |",
])
if "| 114 |" not in tk:
    K.write_text(tk.rstrip() + "\n\n" + FACT + "\n", encoding="utf-8")
    print("  ok known-facts 已加 114")
else:
    print("  已有 114")

# ── Spec Kit 094 ────────────────────────────────────────────────────
S = Path(r"D:\AI\SW\specs\094-param-iface-inference-reverted")
S.mkdir(parents=True, exist_ok=True)
spec = """# 094 · 「从 docstring 推形参接口」这条退路**不成立** —— 实测两处都推错，已回退

**Status**: Implemented（轮 174）· ⚠ **负结果**（这本身就是产出）

## 一、动机
轮 173 的检查器**抓不到它自己的动机**：`mold_evidence(model)` 的 owner 是**形参** ⇒ 静态推不出接口。
★ 本轮试一条退路：**没有 `:param` 段时**，若 **① 恰好 1 个形参** 且 **② docstring 里出现的反射接口名恰好 1 个**
⇒ 采纳它。

## 二、⚠⚠⚠ 实测**两处都推错**
```
① insert_parting_line / insert_parting_surface / insert_shut_off_surface /
   insert_core_cavity_solids / mold_draft_analysis
   ⇒ 推成 **`Feature`**  ← docstring 里的**散文词** `feature` 命中了**接口名 `Feature`**
     ⇒ 于是报「`Feature . FeatureManager` 不在 `IFeature` 上」（**荒谬但「技术上成立」**）
② mold_undercut_detect ⇒ 推成 **`IFeatureManager`**
   ← docstring 提到的是**成员全名** `IFeatureManager.MoldUndercutDetect`，**不是形参的类型**
```

## 三、★ 处置：**回退**
```
命中数 20 → 36（含 6 处 `sw_mold` 假阳性）⇒ 回退后 **36 → 20**，`sw_mold` 假阳性**清零**
★ 并把「试过、不成立」**写进代码注释**（防下一个人再试一遍）
```

## 四、★ 定则（本轮最值钱的一句）
```
**显式 = 有依据；推断 = 会错** —— 只认 `:param <名>: <接口名>` 这一种写法。
⇒ ★★ 这也**印证了事实 113 的教训**（「推不出」不许用兜底值代替）：
   轮 173 的兜底是 **`IObject`**，轮 174 的兜底是 **「docstring 里恰好 1 个接口名」** ——
   **两次都是「把不知道伪装成知道」，两次都被实测打回。**
```

## 五、判据
| ID | 判据 |
|---|---|
| SC-9401 | ★★ 试一条**具体**的退路（不是空谈）|
| SC-9402 | ★★★ **实测**它推错（两处，且能指出各自根因）|
| SC-9403 | ★★ **回退**并核对（36 → 20，假阳性清零）|
| SC-9404 | ★ 把「试过、不成立」**写进代码**（防重复试）|
| SC-9405 | ★★ 记下定则「**显式 = 有依据；推断 = 会错**」，并与事实 113 的教训**接上** |
| SC-9406 | ⚠ **如实记下后果**：`mold_evidence` 那类**仍然抓不到**（动机未覆盖）|

## ⚠ 明确记下的限度
* ⚠ **没有解决问题** —— `mold_evidence` 那种「散文 docstring + 形参 owner」**仍然抓不到**；
* ⚠ 从**调用点**推形参接口那条路**未做**（它是下一步）；
* ⚠ 本轮**没有**动那 20 处命中（仍是静态，**未真机核**）；
* ⚠ 回退过程中我**两次写坏文件**（一次脚本语法错、一次 `return {}` 缩进错）⇒
  ★ 都靠 `git checkout --` 恢复；**最终用 `edit` 工具加注释**（事实 61 的定则**又**用上了）。
"""
plan = """# 094 · Plan

## 步骤
1. 轮 173 的局限：形参 owner 推不出 ⇒ 检查器抓不到自己的动机
2. ★ 设计退路：**:param 缺失时**用「恰好 1 形参 + docstring 里恰好 1 个反射接口名」
3. ★★ **实测** ⇒ **两处都推错**（散文词 `feature` 命中接口名 `Feature`；成员全名被当类型）
4. ★ **回退**（36 → 20，`sw_mold` 假阳性清零）
5. ★ 把「试过、不成立」写进代码注释
6. 事实 114 → 门禁 + 回归 → 收工

## 风险与对策
| 风险 | 对策 |
|---|---|
| 猜出来的东西当成依据 | ★ 本轮**实测推错**并**回退** |
| 回退时改坏文件 | ⚠ **两次都改坏** ⇒ `git checkout --` + **改用 `edit`** |
| 把负结果说成「有进展」 | ★ 结论里明写**没解决问题** |
| 下一个人再试一遍 | ★ **把「试过、不成立」写进代码注释** |
"""
tasks = """# 094 · Tasks（全部完成，轮 174）

- [x] T-9401 试退路（`:param` 缺失时的 docstring 推断）
- [x] T-9402 ★★★ 实测两处推错 `→ 验收:` `python D:/AI/SW/_verify_param_infer.py`
- [x] T-9403 回退 `→ 验收:` `python scripts/check_member_owner_interface.py`（**20 处**，`sw_mold` 无命中）
- [x] T-9404 把「试过、不成立」写进代码注释
- [x] T-9405 事实 114
- [x] T-9406 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
"""
converge = """# 094 · Converge

**Converged**: 2026-10-01（轮 174）

## 一、结果
| 判据 | 结论 |
|---|---|
| SC-9401 试具体退路 | ✅ |
| SC-9402 实测推错 | ✅ 两处，根因各不同 |
| SC-9403 回退并核对 | ✅ 36 → 20 |
| SC-9404 写进代码注释 | ✅ `+17/-0` |
| SC-9405 定则并与 113 接上 | ✅ |
| SC-9406 记下后果 | ✅ 动机仍未覆盖 |

## 二、★★★ 本轮的产出是**负结果**，而这正是它该有的样子
```
试了一条退路 ⇒ **实测两处都推错** ⇒ **回退** ⇒ 把「试过、不成立」写进代码
⇒ ★ 与「猜一个兜底值然后接进工具」相比，**负结果 + 代码注释**才是可累积的：
  下一个人不会在同一个地方再试一遍。
```

## 三、★★ 与事实 113 的教训**接上了**
```
113：兜底值 `IObject` ⇒ 把「我不知道」变成「它有错」
114：兜底推断「docstring 里恰好 1 个接口名」 ⇒ 同样把「不知道」伪装成「知道」
⇒ ★★ **两次都是同一个错误形状** ⇒ 定则：**显式 = 有依据；推断 = 会错。**
```

## 四、未查证
* ⚠ `mold_evidence` 那类**仍然抓不到**（动机未覆盖）；
* ⚠ **从调用点推**那条路**未做**；
* ⚠ 20 处命中仍是**静态**，**未真机核**。
"""
for name, text in (("spec.md", spec), ("plan.md", plan), ("tasks.md", tasks), ("converge.md", converge)):
    (S / name).write_text(text, encoding="utf-8")
    print("  written %s" % name)
