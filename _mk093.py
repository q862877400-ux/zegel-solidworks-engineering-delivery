import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

# ── 事实 113 ────────────────────────────────────────────────────────
K = Path(r"D:\AI\SW\docs\known-facts.md")
tk = K.read_text(encoding="utf-8")
FACT = "| 113 | " + "".join([
    "**新检查器 `check_member_owner_interface.py`：用出厂反射推「成员该在哪个接口」，",
    "命中 20 处（含我前几轮真机踩过的两个坑）—— 但**抓不到它自己的动机**（形参 owner）** —— 轮 173。",
    "## 判据（**可核验**，零启发式）",
    "```",
    "① 反射 `_raw/reflect_sldworks/iface_sldworks.txt` 有 `## <Iface>` 分段",
    "   ⇒ 直接解析出 **接口名 → 成员名集合**（1032 个接口 / 16732 个成员）",
    "② `X = get_com_member(<owner>, \"<Member>\")` ⇒ 由 `<owner>` 的接口查 `Member` 的**返回类型**",
    "   ⇒ 得到 `X` 的接口（★ 返回类型就在反射行首：`FeatureManager get_FeatureManager()`）",
    "③ `get_com_member(X, \"<Member2>\")` ⇒ `Member2` **完全不在** `X` 接口的谱系里 ⇒ **报**",
    "```",
    "## ★★★ 我一个人在这一处**连踩两个假阳性**（如实记）",
    "```",
    "第一版：**113** 处命中 —— 大量假阳性",
    "  根因①：反射里**属性带 `get_` 前缀**（`FeatureManager get_FeatureManager()`），",
    "         而代码写 `get_com_member(model, \"Extension\")` ⇒ 不做规范化 ⇒ 属性读**全被误报**",
    "第二版：**47** 处 —— 仍混假阳性",
    "  根因②：推不出接口时我落到了 **`IObject` 兜底** ⇒ ★ **兜底值必然不在成员谱系里 ⇒ 必报**",
    "第三版：**20** 处 —— 去掉兜底（**推不出就留白、不检查**）",
    "```",
    "⇒ ★ 教训：**「推不出」不许用兜底值代替** —— 兜底会把「我不知道」变成「它有错」。",
    "## ★★ 20 处高度可信（**独立于我的记忆**的两个佐证）",
    "```",
    "`GetBodies2` 在 IModelDoc2 上 ⇒ 实际在 **IPartDoc / IComponent2**  ← ★ **轮 161 真机踩过**",
    "`GetSketchSegments2` ⇒ 反射里**没有**                        ← ★ **轮 162 真机踩过**",
    "`GetSheetNames` ⇒ IDrawingDoc · `AddMate5` ⇒ IAssemblyDoc · `GetTitle` ⇒ IModelDoc/IModelDoc2",
    "```",
    "★ 并**核实**了判据本身：`FeatureByName` **确实不在 IModelDoc2 上**（反射里只在",
    "IAssemblyDoc / IComponent2 / IDrawingDoc / IPartDoc）⇒ ★ **不是解析漏了**。",
    "## ⚠⚠⚠ **关键局限：它抓不到它自己的动机**",
    "```",
    "`mold_evidence(model)` 的 owner 是**形参** ⇒ 静态推不出接口 ⇒ 被「留白」排除",
    "⇒ ★★ **检查器抓不到 `mold_evidence`**（而那正是写它的起因）",
    "```",
    "★ 可补的两条路（**未做**）：① **docstring 里的 `:param` 说明**（本仓库 docstring 常写接口名）；",
    "② **从调用点推**（`mold_evidence(doc)` ⇒ `doc` 的接口）。",
    "## ⚠ 定位：**诊断工具，不接门禁**",
    "判据**还没证到能当门禁**的程度（20 处里仍有需要逐条真机核的，如 `FeatureByName` 的 `model`",
    "到底是不是 `IModelDoc2`）⇒ ★ **不接 `release_check.py`**，与事实 53 同族（**证据不进工具**）。",
    " | `scripts/check_member_owner_interface.py`；`D:/AI/SW/output/member-owner-interface.json`；",
    "事实 36 / 53 / 62 / 112 |",
])
if "| 113 |" not in tk:
    K.write_text(tk.rstrip() + "\n\n" + FACT + "\n", encoding="utf-8")
    print("  ok known-facts 已加 113")
else:
    print("  已有 113")

# ── Spec Kit 093 ────────────────────────────────────────────────────
S = Path(r"D:\AI\SW\specs\093-member-owner-interface-checker")
S.mkdir(parents=True, exist_ok=True)
spec = """# 093 · 新检查器：用出厂反射判「成员该在哪个接口」—— 命中 20 处，但抓不到它自己的动机

**Status**: Implemented（轮 173）· ⚠ **诊断工具，不接门禁**

## 一、动机（接轮 172）
轮 172 查出 `mold_evidence` 从**错的接口**读（成员在 `I*FeatureData` 上）。
★ 仓库**已有** `check_interface_member_ownership.py`，⚠ 但它只覆盖
「`data = CreateDefinition(<CONST>)` ⇒ `data.X`」**那一条路径**
⇒ ★★ **「从某个管理器直接取成员」这种形态它看不见** ⇒ 本轮补这个盲点。

## 二、判据（**可核验**，零启发式）
```
① 反射 `_raw/reflect_sldworks/iface_sldworks.txt` 有 `## <Iface>` 分段
   ⇒ 直接解析出 **接口名 → 成员名集合**（**1032 个接口 / 16732 个成员**）
② `X = get_com_member(<owner>, "<Member>")` ⇒ 由 `<owner>` 的接口查 `Member` 的**返回类型**
   ⇒ 得到 `X` 的接口（★ 返回类型就在反射行首：`FeatureManager get_FeatureManager()`）
③ `get_com_member(X, "<Member2>")` ⇒ `Member2` **完全不在** `X` 接口的谱系里 ⇒ **报**
```

## 三、★★★ 我一个人在这一处**连踩两个假阳性**
```
第一版：**113** 处
  根因① 反射里**属性带 `get_` 前缀**，而代码写不带前缀 ⇒ 属性读**全被误报**
第二版：**47** 处
  根因② 推不出接口时落到了 **`IObject` 兜底** ⇒ ★ **兜底值必然不在成员谱系里 ⇒ 必报**
第三版：**20** 处（去掉兜底：**推不出就留白、不检查**）
⇒ ★ 教训：**「推不出」不许用兜底值代替** —— 兜底会把「我不知道」变成「它有错」。
```

## 四、★★ 20 处高度可信（**独立于我的记忆**的两个佐证）
| 命中 | 实际在 | 佐证 |
|---|---|---|
| `IModelDoc2.GetBodies2` | `IPartDoc` / `IComponent2` | ★ **轮 161 真机踩过** |
| `ISketch.GetSketchSegments2` | 反射里**没有** | ★ **轮 162 真机踩过** |
| `IModelDoc2.GetSheetNames` | `IDrawingDoc` | — |
| `IModelDoc2.AddMate5` | `IAssemblyDoc` | — |
| `IPartDoc.GetTitle` | `IModelDoc` / `IModelDoc2` | — |

★ 并**核实**了判据本身：`FeatureByName` **确实不在 IModelDoc2 上**
（反射里只在 `IAssemblyDoc` / `IComponent2` / `IDrawingDoc` / `IPartDoc`）⇒ **不是解析漏了**。

## 五、⚠⚠⚠ 关键局限：**它抓不到它自己的动机**
```
`mold_evidence(model)` 的 owner 是**形参** ⇒ 静态推不出接口 ⇒ 被「留白」排除
⇒ ★★ **检查器抓不到 `mold_evidence`**（而那正是写它的起因）
```
★ 可补的两条路（**未做**）：① **docstring 的 `:param` 说明**；② **从调用点推**。

## 六、判据
| ID | 判据 |
|---|---|
| SC-9301 | ★★★ **反射给接口→成员表**（1032 接口 / 16732 成员），零启发式 |
| SC-9302 | ★★ 用**返回类型**推变量接口（反射行首）|
| SC-9303 | ★★★ **连踩两个假阳性并都修掉**（`get_` 前缀 · `IObject` 兜底）—— 如实记 |
| SC-9304 | ★★ 20 处命中**含两个真机踩过的坑** ⇒ 判据可信的独立佐证 |
| SC-9305 | ★★ **核实判据本身**（`FeatureByName` 确实不在 IModelDoc2）|
| SC-9306 | ⚠⚠⚠ **如实记「抓不到形参 owner」这个关键局限**（含动机本身）|
| SC-9307 | ⚠ **不接门禁**（判据未证到那个程度）· 检查量为 0 时非 0 退出（事实 46）|

## ⚠ 明确记下的限度
* ⚠ **抓不到形参 owner**（`mold_evidence` 就是这种）⇒ **动机未被覆盖**；
* ⚠ 20 处里仍有需**逐条真机核**的（如 `model` 到底是不是 `IModelDoc2` ⇒ `FeatureByName` 那处）；
* ⚠ **不接门禁** —— 判据还没证到能当门禁的程度（事实 53 同族：**证据进文档，不进工具**）；
* ⚠ 没有真机验证那 20 处（本轮**只做静态**）。
"""
plan = """# 093 · Plan

## 步骤
1. 轮 172 的盲点：现有 owner 检查器只管 `CreateDefinition` 那条路径
2. ★ 设计：反射解析出「接口 → 成员」+ 用**返回类型**推变量接口
3. ⚠ 第一版 **113** 处 ⇒ **假阳性**（属性带 `get_` 前缀）⇒ 加规范化
4. ⚠ 第二版 **47** 处 ⇒ 仍假（**`IObject` 兜底**）⇒ 去掉兜底（推不出就留白）
5. ★ 第三版 **20** 处 ⇒ 含**两个我前几轮真机踩过的坑** ⇒ 判据可信
6. ★ 核实判据本身（`FeatureByName` 确实不在 IModelDoc2）
7. ⚠⚠ **发现关键局限**：形参 owner 推不出 ⇒ **抓不到 `mold_evidence`**（动机本身）
8. 事实 113 → 门禁 + 回归 → 收工

## 风险与对策
| 风险 | 对策 |
|---|---|
| 假阳性多还接门禁 | ★ **两轮假阳性都被发现并修**；**不接门禁** |
| 用兜底值代替「不知道」 | ★ **推不出就留白**（本轮的核心教训）|
| 只报数量不核判据 | ★ **核实 `FeatureByName`**（证明不是解析漏）|
| 把"抓到 20 处"说成"动机解决了" | ★ **明写抓不到 `mold_evidence`** |
"""
tasks = """# 093 · Tasks（全部完成，轮 173）

- [x] T-9301 建检查器 `→ 验收:` `python scripts/check_member_owner_interface.py`（**20 处**）
- [x] T-9302 修两个假阳性根因（`get_` 前缀 · `IObject` 兜底）
- [x] T-9303 核实判据本身（`FeatureByName` 确实不在 IModelDoc2）
- [x] T-9304 记下关键局限（形参 owner 抓不到 · **动机本身**）
- [x] T-9305 事实 113
- [x] T-9306 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
"""
converge = """# 093 · Converge

**Converged**: 2026-10-01（轮 173）

## 一、结果
| 判据 | 结论 |
|---|---|
| SC-9301 反射建表 | ✅ 1032 接口 / 16732 成员 |
| SC-9302 用返回类型推接口 | ✅ |
| SC-9303 连修两个假阳性 | ✅ 113 → 47 → 20 |
| SC-9304 含两个真机踩过的坑 | ✅ `GetBodies2` · `GetSketchSegments2` |
| SC-9305 核实判据 | ✅ `FeatureByName` |
| SC-9306 记下关键局限 | ✅ **抓不到动机** |
| SC-9307 不接门禁 | ✅ |

## 二、★★★ 本轮最有价值的**不是 20 处命中，而是"两次假阳性"**
```
113 →（修 get_ 前缀）→ 47 →（去掉 IObject 兜底）→ 20
⇒ ★ 两次都不是「判据不够严」，而是**我的实现把「不知道」伪装成了「知道」**：
  · 属性名没规范化 ⇒ 属性读全被当成"反射里没有"
  · 推不出接口就落 `IObject` ⇒ 必然误报
⇒ ★★ 可复用的教训：**分析工具里，"推不出"必须留白**；
  任何**兜底值**都会把「我不知道」变成「它有错」。
```

## 三、★★ 判据可信的**独立佐证**
```
20 处命中里有 2 处，正是我**前几轮在真机上踩过的坑**（轮 161 `GetBodies2` · 轮 162 `GetSketchSegments2`）
⇒ ★ **检查器独立复现了我的真机经验** ⇒ 这比「看起来合理」强得多。
```

## 四、⚠⚠⚠ 关键局限（必须记住）
```
抓不到 `mold_evidence` —— 它的 owner 是**形参**，静态推不出接口
⇒ ★ **检查器抓不到它自己的动机**。
★ 可补：docstring 的 `:param` 说明 / 从调用点推 —— **都未做**。
```

## 五、未查证
* ⚠ 形参 owner（含动机本身）；
* ⚠ 20 处里需逐条真机核的（`model` 到底是不是 `IModelDoc2`）；
* ⚠ **没有真机验证那 20 处**（本轮只做静态）；
* ⚠ 不接门禁（判据未证到那个程度）。
"""
for name, text in (("spec.md", spec), ("plan.md", plan), ("tasks.md", tasks), ("converge.md", converge)):
    (S / name).write_text(text, encoding="utf-8")
    print("  written %s" % name)
