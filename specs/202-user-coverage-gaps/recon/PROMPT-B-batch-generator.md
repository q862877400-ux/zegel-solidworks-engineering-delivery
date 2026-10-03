# 提示词 B · 批量生成器（★ 整段复制给 Opus 5.5 / Sonnet 5.5）

> ★★ **这份提示词的目标只有一个：让你造出的生成器真的能跑、真的找得全、真的不误报。**
> ★ 它把**三类缺陷各自的确切输入/判据/输出形态**、**仓库的接口契约**、**搜索配方**、
> 以及**一个已经跑通的生成器的完整源码**都写在里面。★ **不需要你猜我要什么形态**。
> ★★ 形式要求只有一条：**先把 `GEN-SPEC.md` 落盘**（设计表），**然后一次做完一个类**，每类立刻落盘。

---

# 第 0 部分 · 背景：为什么"可以批量"（★ 已实测，不要重新论证）

★ 本仓做过一轮**逐条对官方文档**的核对（**30 份**，在
`specs/202-user-coverage-gaps/recon/audit-vs-official/`），★ 分歧**分类**后集中在三类：

| 类 | 占总分歧 | ★ 为什么它可批量 |
|---|---|---|
| ★★ **mark / 前置**（该先选什么、mark 给几）| **33%** | ★ 官方 `## Remarks` 里有**mark 表**；★ 修法是**同一形态**：给 `ToolSpec` 挂 `pre_call` |
| ★★ **用了官方废弃成员** | **20%** | ★ 官方页有 `Obsolete` 行 + **点名后继** ⇒ **映射是数据** |
| ★★ **枚举取值不是合法成员** | **10%** | ★ `C:\swapi\enums\*.md` 是 **name → value** 表 |
| — | ★ **合计 63%** | — |

★★ **三类之外不可批量**（★ 已实测）：★ 参数顺序/类型（要逐条对签名）· ★ 几何语义前置
（如"扫描路径起点必须落在轮廓平面上"）· ★ 接口归属有歧义的部分（**见 §3 约束 1**）。

---

## ★★★ 0.1 先读这一节 —— 前一轮已经量出来的**四条硬结论**（★ 不要重新论证，直接建在上面）

★ 上游刚跑完一轮**全量抽录 + 归因**，产物在
`specs/202-user-coverage-gaps/recon/audit-vs-official/PATTERNS.md`（★ **必读**）。
★ 它把**全 30 份**的分歧抽全（**104 条**；★ 后到 3 份追加后 **117 条**）并归成 **D1–D14 共 14 类**。
★★★ **它给出的四条结论，直接改变你该造什么**：

### 结论 1 · ★★★ 「**找得全**」与「**改得动**」是**两个独立的轴**（★ 我原先混为一谈）
| 口径 | 含义 | ★ 实测覆盖率 |
|---|---|---|
| **一类一查** | 一个静态脚本能把这一类**找全** | ★★ **54 / 104 = 52%** |
| **一类一修** | 再加一个**共用修法**能**全改完** | ★★ **17 / 104 = 16.3%** |
⇒ ★★★ **所以：该投资的是「检测器」，不是「通用修法」。**
★ 而且**严格可批量只有三档、共 17 条**：
| 档 | 类 · 形态 | 条数 | 一个脚本怎么找全 | 共用修法是什么 |
|---|---|---|---|---|
| **①** | ★ **「我们的取值域 = 官方取值域 ∖ k」** | **8** | AST 抽所有传给枚举形参的整数字面量 / `SW_*` 常量 / 白名单元组 × `enums/*.md` 成员表 ∪ 成员页 `## Parameters` 里的区间句式（`valid range is 1 … to 5`）| ★ **以官方成员表为真源重生成我们的取值域/常量表**（★ **不是逐条补值**）|
| **②** | ★★ **「废弃成员 · 只出现在兜底/回退分支」** | **8** | AST 抽调用点 →（官方 `Obsolete` 名单）→ ★★ **对每个命中查「同函数内是否已存在官方后继的调用」** | ★★ **删掉那个冗余分支**（一条规则、零歧义）|
| **③** | ★ **「`System.object` 形参漏传」** | **1** | 我们实参个数 × 官方 `**Signature**` 形参个数（纯 AST + 文本）| 按官方例子把 `System.object` 形参传 `null` |
★★ **档 ② 是"可批量"的理想形态**：★ 判据是**一个布尔**（"后继是否已在同函数被调过"），★ 修法是**一个动作**（删）。
★ 它的 8 条具体是：`S2-09` / `S2-10`（`IView.Name` 兜底，主路径已是 `GetName2`）· `S2-26`（同文件另一处已用 `SketchManager.ActiveSketch`）· `S2-27`（下一行就是 `Select4`）· `S2-28`（`("Select2","Select4")` 里的 `Select2`）· `S1-44`（`except` 回退分支，上一分支已用 `ActivateDoc3`）· `S3-21` / `S3-24`（两条 `ActivateDoc2` 的 `except` 分支）。

### 结论 2 · ★★★ **「废弃成员」这一类只有一个 sed 打不掉它 —— 实测有 8 种改法**
| 改法 | 例子 |
|---|---|
| ① 同型同名 | `Select2` → `Select4` |
| ② **删兜底分支** | ★ 就是上面的档 ②（8 条）|
| ③ 首位换后继 | `CreateSpline2` → 3 |
| ④ ★★ **后继形参变了** | `MoldUndercutDetect` 6→9 · `AddComponent4`→5 多配置名 |
| ⑤ ★ **属性 → 方法** | `IDimension.SystemValue` → `GetSystemValue3` |
| ⑥ ★★ **换宿主接口** | `IModelDoc2.GraphicsRedraw2` → `IModelView.GraphicsRedraw` · `IModelDoc2.SetUserPreferenceIntegerValue` → `IModelDocExtension.SetUserPreferenceInteger` |
| ⑦ ★ 链尾是 `CreateFeature` + `XxxFeatureData` | `FeatureFillet`→2→3 · `FeatureLinearPattern3`→4→5 · `FeatureCircularPattern4`→5 |
| ⑧ ★★★ **by-ref 出参新增** | `GetErrorCode` → `GetErrorCode2` |
⇒ ★★ **所以类 2 的生成器只能出「计划」，且必须按改法**分档**输出**（★ 不要输出一个"统一替换"）。

### 结论 3 · ★★★ **有"明知故犯的防御"，批量替换会把它换成已知会失败的调用**
★ 代码里逐字写着（`S1-20` 的注释）：
> 「`GetErrorCode2` 多一个 by-ref `isWarning` 参数；此处只需拒绝硬错误，
> **使用无歧义的 `GetErrorCode` 可兼容 pywin32 静态与动态代理**」
★★ 而本仓**已知事实 47**：★ **`IAccessSelections` 那族在 pywin32 迟到绑定下不可调用**（20+ 种形态已穷尽）。
⇒ ★★★ **任何"废弃成员批量替换"的生成器，第一步必须是「后继是否多出 by-ref / out 形参」过滤；
   命中即转人工** —— ★ 否则你会把"**明知故犯的防御**"换成"**已知会失败的调用**"。

### 结论 4 · ★★ 三条比"类"更值钱的横向发现
1. ★ **同一个根因被多个核对面各报一次** ⇒ ★★ **104 条 ≠ 104 个修复单元**：
   ★ `GetErrorCode` 的 Obsolete 被**报了三次**（`audit-02-A` / `-C` / `audit-03-C`）⇒
   ★★ **按"代码位置"去重后约 96 个修复单元** ⇒ ★ **"减 8"对排期的影响比"多修一类（+1）"大得多**。
   ⇒ ★ **你的生成器应当同时输出"按代码位置去重后"的分母**。
2. ★★★ **一整类「无源常量」横跨全表，任何单片都发现不了**：
   ★ `audit-02-sheetmetal-C` 与 `audit-03-weldment-C` **各自独立**记下：
   `swFeatureNameID_e.md` 的 `enum_member_count: 130`，★ 而成员表**不全**
   ⇒ ★ 我们代码里的 `SW_FM_BASE_FLANGE=34` / `SW_FM_DRAFT=3` / `SW_FM_ONE_BEND=33` / `SW_FM_SKETCH_BEND=35` … **来源不明**。
   ★★ **这不是"某一条分歧"，是一条"一次普查可解"的系统性问题** ——
   ★ **应当按"普查"推进，不该按"条"修**；★ 第三源是反射 `D:\AI\SW\_raw\**\enum_values_sldworks.txt`
   （★ 本仓已知事实 43 已用它解过 `swFeatureNameID_e`）。
   ★ 而且它一旦解出来，**档 ①（取值域）与 `CreateDefinition` 白名单档（`S1-30`）会同时受益**。
   ⇒ ★★ **这可能是"第四个可批量档"，★ 而且它比前三档更大** —— ★ 值得你单独评估。
3. ★ 「**改了会坏**」的坑已经写在代码注释里 ⇒ ★ 见结论 3。


★★★ 而且：★ 我在**只到 17 份核对表**时做过一次分类抽样，结果是
**mark 类 20 条（33%）· 废弃类 12 条（20%）· 参数个数 7 条 · 枚举类 6 条（10%）**
（分类器：`tools/classify_audit_divergences.py`，★ **你可以直接跑它**）。

---

# 第 1 部分 · 仓库的接口契约（★ 你必须按这些写，否则生成的东西挂不上去）

## 1.1 `ToolSpec` 的字段（★ 在 `mcp-server/tool_registry.py`）
| 字段 | 类型 | 语义 |
|---|---|---|
| `name` | str | 工具名（`solidworks_xxx`）|
| `title` / `doc` | str | 标题与文档（★ **`doc` 是人读的，★ 也是我的判据来源之一**）|
| `module` / `function` | str | 目标在 `scripts/<module>.py` 的 `<function>` |
| `inject` | str | ★ 解析器键（`"model"` / `"sw"` / `"study"` / `"cost_manager"` …）★ 注册器会 `kwargs[inject] = RESOLVERS[inject](params)` |
| `params` | list[`Param`] | ★ **`Param(name, kind, default=..., description=...)`** —— ★★ **字段名是 `kind`，不是 `type`**；★ 无默认值的哨兵是 **`Ellipsis`** |
| `param_alias` | dict | ★★ **`{声明名: 目标形参名}`**；★ **值为 `None` = 「由解析器/`pre_call` 消费、不进目标函数」** |
| `pre_call` | callable | ★★ **`pre_call(params) -> 任意`** —— ★ **它跑在注入之后、目标函数之前** ⇒ ★ **只有在这里做的选择才活得到目标函数** |
| `derived_args` | callable | ★ `derived_args(params) -> dict`，★ 其结果 `update` 进 `kwargs` |

## 1.2 ★★ 注册器的调用顺序（★ 这是理解"前置"的钥匙）
```python
kwargs[inject] = RESOLVERS[inject](params)     # ① 注入
result = spec.pre_call(params)                  # ② ★★ 只有这里做的选择才活得到 ④
kwargs.update(spec.derived_args(params) or {})  # ③
getattr(mod, spec.function)(**kwargs)           # ④ 目标函数
```
★★ **为什么"前置"必须走 `pre_call`**：★ **MCP 客户端根本没有"在调用工具之前先选好某个东西"这条通路**
（★ 不是因为解析器会清选区 —— ★ 那个机制我实测**证伪**过，见 §5）。

## 1.3 ★ 仓内**现成的、已验证过的**帮手（★ 直接用，不要重写）
| 帮手 | 在哪 | 干什么 |
|---|---|---|
| `_select_sketch_by_name(model, name, mark, append)` | `mcp-server/tool_specs_batch4.py` | ★ 按**名字**选草图并给 `mark`（★ `SelectByID2(name, "SKETCH", 0,0,0, append, mark, **空 VARIANT**, 0)`）|
| `_mark_count(model, mark)` | 同上 | ★ **回读**某档 mark 的选中数（★ 事实 8：只有计数算数）|
| `_select_sketches_in_order(model, names, mark, at_least, what)` | 同上 | ★ ★★ **按给定顺序** `append` 选多个（★ 顺序在放样/扫描里**是语义**）· **不够就抛** |
| `_pre_sweep_sketches(params)` | 同上 | ★ 轮廓 mark=1 · 路径 mark=4 |
| `_pre_loft_profiles(params)` | 同上 | ★ 放样轮廓全 mark=1、按顺序 |
| `_select_faces_for(mark, count)` | `mcp-server/tool_specs_batch74.py` | ★ 按对象遍历体→面、按 mark 选、**回读计数** |
| `resolve_selection(model, selector, kind)` | `scripts/sw_selection_spec.py` | ★ 声明式选择（`"index:0"` / `"__current_selection__"`），★ **自带回读、0 就抛** |
| `create_empty_dispatch_variant()` | `scripts/sw_connect.py` | ★★ `SelectByID2` 的 `Callout` **必须**传它（★ 传 `None` 报"类型不匹配"，★ **且那个错误看不出是 Callout 的问题**）|

## 1.4 ★★ "回读计数"是唯一可信的判据
★ `Select4` / `SelectByID2` / `AddSelectionListObject` 的**布尔返回值都不可信**
（★ 本仓实测：`SelectByID2` 12 次全回 `false` 而计数 = 12）。
⇒ ★★ **生成器生成的 `pre_call` 必须回读**：`GetSelectedObjectCount2(mark)`。

---

# 第 2 部分 · ★★★ 一个**已经跑通的生成器**（★ 完整源码，照这个写）

★ 这是 `tools/gen_precall_patch.py` 的**核心结构** —— ★ **它就是你要写的东西的模板**：

```python
"""★ 一句话说清这个文件干什么。"""

# ── 来源 ─────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# ─────────────────────────────────────────────
from __future__ import annotations
import ast, json, re, sys, time
from pathlib import Path

REPO = Path(r"D:\AI\SW")
CAND = REPO / "specs" / "202-user-coverage-gaps" / "recon" / "precall-cand"
OUT  = REPO / "output" / "precall-patch-plan.json"

def _specs_by_tool() -> dict:
    """★ 只读源码文本，★ 不 import —— 免得拉 COM。"""
    out = {}
    for f in sorted((REPO / "mcp-server").glob("tool_specs_batch*.py")):
        t = f.read_text(encoding="utf-8", errors="replace")
        for blk in re.split(r"ToolSpec\(", t)[1:]:
            nm = re.search(r'name="(solidworks_[a-z0-9_]+)"', blk)
            if not nm:
                continue
            out[nm.group(1)] = {
                "file": f.name,
                "has_pre_call": "pre_call=" in blk,
                "has_param_alias": "param_alias=" in blk,
                "params": re.findall(r'Param\(\s*"([a-z0-9_]+)"', blk),
            }
    return out

def _cand_pre_calls() -> dict:
    """★ 用 AST 抽 `_pre_<x>(params)` —— ★ 不执行候选代码。"""
    out = {}
    for f in sorted(CAND.glob("precall-cand-*.py")):
        tree = ast.parse(f.read_text(encoding="utf-8", errors="replace"))
        out[f.name] = {
            "pre_calls": [n.name for n in ast.walk(tree)
                          if isinstance(n, ast.FunctionDef) and n.name.startswith("_pre_")],
            "helpers":   [n.name for n in ast.walk(tree)
                          if isinstance(n, ast.FunctionDef) and n.name.startswith("_")
                          and not n.name.startswith("_pre_")],
        }
    return out

def main() -> int:
    specs, cands = _specs_by_tool(), _cand_pre_calls()
    plan = []
    for cname, info in cands.items():
        for fn in info["pre_calls"]:
            tool = "solidworks_" + fn[len("_pre_"):]      # _pre_part_sweep -> solidworks_part_sweep
            cur = specs.get(tool)
            plan.append({
                "candidate": cname, "pre_call_fn": fn, "tool": tool,
                "tool_registered": cur is not None,
                "spec_file": (cur or {}).get("file"),
                "already_has_pre_call": (cur or {}).get("has_pre_call"),
                "action": ("★ 已挂（跳过）" if (cur or {}).get("has_pre_call")
                           else ("★ 要挂：" + fn) if cur else "★ 工具没注册 —— 核对名字"),
            })
    OUT.write_text(json.dumps({"plan": plan}, ensure_ascii=False, indent=1), encoding="utf-8")
    #: ★★ 覆盖面自报（★ 判据必须自证在跑）
    print("★ 输入：仓内 **%d** 条工具 · 候选 **%d** 份" % (len(specs), len(cands)))
    for r in plan:
        print("%-26s %-22s %-22s %s" % (r["pre_call_fn"], r["tool"], r["spec_file"], r["action"]))
    return 0
```
★ **它的实测输出**（★ **这就是"一份生成器计划"长什么样**）：
```
_pre_mold_parting_line     → tool_specs_batch1.py    ★ 要挂
_pre_mold_parting_surface  → tool_specs_batch9.py    ★ 要挂
_pre_part_axis             → tool_specs_batch49.py   ★ 要挂
_pre_part_wrap             → tool_specs_batch50.py   ★ 要挂
_pre_part_sweep            → tool_specs_batch48.py   ★★ 已挂（跳过）
_pre_part_loft             → tool_specs_batch47.py   ★★ 已挂（跳过）
_pre_parting               → ★ 工具没注册（★ 它是共用的实现，不是工具）
```
★★★ **注意两件事**：① ★ 它**自己认出了已被手工挂好的两条** ⇒ ★ **说明它读仓内状态是准的**；
② ★ 它**如实报** `_pre_parting` 对不上工具（★ 那是两路共用的实现）⇒ **不硬凑**。

---

# 第 3 部分 · ★★★ 三类各自的**确切形态**（★ 照着做）

## 类 1 · **mark / 前置**（★ 优先级最高，33%）

**输入**（★ 全是结构化的）：
- ★ 候选文件：`specs/202-user-coverage-gaps/recon/precall-cand/precall-cand-{A,B,C}.py`
  ★ 形态：★ 每条工具一个 `_pre_<name>(params)` + 共用帮手 + **每条自带官方依据（mark 表 + 出处页 + 例子行范围）**；
- ★ 仓内 spec 现状：`mcp-server/tool_specs_batch*.py`（★ 读它的 `params` / 有无 `pre_call`）；
- ★ 目标函数的前置：`scripts/sw_*.py` 里的 `GetSelectedObjectCount2`（★ 它**读出几档 mark、阈值多少**）。

**判据**（★ 怎么判"这条工具有 mark/前置缺陷"）：
★★ **`目标函数读了 mark 的选区计数` 且 `spec 既没有 pre_call、也没有一个能提供选区的参数`** ⇒ **必然失败**。
★ 佐证：★ 真机跑一次会停在 `{"ok": False, "stage": "selection"}`。

**输出**：★ 补丁计划，每条含 `tool` / `spec_file` / `要加的 pre_call` / `要加的 param_alias` / `要不要加新参数（名字+类型+描述）`。

**应用方式**（★ 写清，但**不要执行**）：
★ 给那条 `ToolSpec` 加三处：`pre_call=<候选里的函数>` · `param_alias={"<新参数>": None}` ·
★ `params` 里加 `Param("<新参数>", str|list, default=..., description="…")`。
★★ **已经手工做过的两条可以拿来对**（★ 看它们的实际改法）：
- `mcp-server/tool_specs_batch47.py`（`part_loft`：加了 `profile_sketches`（list）+ `pre_call=_pre_loft_profiles` + `param_alias`）
- `mcp-server/tool_specs_batch48.py`（`part_sweep`：加了 `profile_sketch` / `path_sketch` + `pre_call=_pre_sweep_sketches` + `param_alias`）
★ 这两条的**真机验证**：★ `part_loft` **建成 `放样1`**（`type_name=Blend` · `args_count=18` · `mark1_selected=2`）；
★ `part_sweep` 前置成立（`mark1=1 · mark4=1`）但特征未建成（★ 那是**另一个问题**，★ 不是前置）。

**风险**：★ 加了参数会**改变工具的公开签名** ⇒ ★ 但这一族**当前根本不可用** ⇒ **无回归风险**。

---

## 类 2 · **用了官方废弃成员**（20%）

**输入**：
- ★ `specs/202-user-coverage-gaps/recon/official-obsolete-index.json`
  ⇒ 每条：`{interface, member, successor, obsolete_line, page}`（**1671** 条，1586 条有后继）；
- ★ `specs/202-user-coverage-gaps/recon/official-members-index.json`
  ⇒ 全量：**566 接口 · 8239 唯一成员名 · 每个成员的所属接口与是否废弃**；
- ★ 我们这边的成员名来源：`grep -oh 'get_com_member([^,]*, *"[A-Za-z_][A-Za-z0-9_]*"' scripts/*.py`

**判据**（★★ **这里有个必须做对的步骤**）：
1. ★ 先从全量索引算出**「在所有接口上都废弃」的成员名集合**（★ 实测量：**1163** 个）
   ⇒ ★★ **只有这批"按名字判"才是安全的**；
2. ★★ **再算出「有歧义」的**（★ 部分接口废弃、部分不废弃；★ 实测量：**292** 个）
   ⇒ ★ **这批**不许自动生成**，★ 只许出"人工确认"清单；
3. ★ 我们的成员名 ∩ 那 1163 个 ⇒ **这才是可自动生成的目标**。

**★★★ 为什么必须这么判（★ 这是本仓已付出代价的教训）**：
★ 我第一版按**名字**直接对，报出 **870 处** —— ★★ **头几名全是假阳性**：
| 名字 | 定义它的接口数 | 其中废弃的 | 说明 |
|---|---|---|---|
| ★★ **`FeatureCut4`** | 2 | 1 | ★★ **本仓事实 1 逐字说它才是"切除的正确入口"** |
| ★ **`Name`** | **24** | **2** | ★ 极常见 |
| ★ `GetBodies2` | 2 | 1 | ★ `IComponent2` 那个废弃，★ `IModelDoc2` 的好好的 |
| ★ `CreateLine` / `GetEdges` | 3 / 8 | 1 | 同型 |
⇒ ★★ **官方 API 是「接口 × 成员」的二维表**；★ 而 `get_com_member(x, "GetBodies2")` 里
**`x` 属于哪个接口，静态源码里看不出来**（运行时对象）。

**输出**：★ 补丁计划，每条含 `我们的调用点` / `现成员` / `官方后继` / `官方那句原文` / `置信度（高=1163 那批，★ 低=需人工确认）`。

**风险**：★ 换后继成员可能**改参数个数**（如 `Select2(Append, Mark)` → `Select4(Append, SelectData)`）
⇒ ★★ **必须逐条对签名**，★ 所以这一类**只能出计划、不能自动落笔**。

---

## 类 3 · **枚举取值不是合法成员**（10%）

**输入**：
- ★ `C:\swapi\enums\*.md` ⇒ **name → value** 表；
- ★ 我们这边的字面量：`grep -n "get_com_member(.*, *[0-9]\{1,4\}" scripts/*.py`
  （★ 以及 `CreateDefinition(...)` 那类**只接受固定常量集**的调用）；
- ★★ **重要**：★ 本仓已知 `C:\swapi\enums\swFeatureNameID_e.md` 的「Value」列**装的是描述、不是数值**
  ⇒ ★ **数值必须去反射**：`D:\AI\SW\_raw\**\enum_values_sldworks.txt`（130 个成员）。★ **三源互证**。

**判据**：★ 代码里当枚举传的**整数**，★ 在那个枚举的**合法成员值集合**里**找不到** ⇒ 报。

**输出**：★ 计划：`调用点` / `传的值` / `该枚举的合法值` / `建议的成员名`。

**真实实例**：★ `swSurfaceExtendEndCondUpToSurface` · `swRuledSurfaceType_TangentToSurface`
—— ★ 这两个名字**不是合法枚举成员**。

---

# 第 4 部分 · ★★★ 三条**硬约束**（★ 违反则产物作废；★ 都是本仓付出代价换来的）

## 约束 1 · **官方 API 是「接口 × 成员」的二维表**（★ 事实 511）
★ 见类 2 的判据。⇒ ★★ **凡按名字生成，必须自带"该名字在几个接口上出现、其中几个命中"的检查**；
★ **命中数 < 出现数 ⇒ 不许自动生成，只许出"人工确认"清单**。

## 约束 2 · **生成器只出计划，不许落笔**（★ M3）
★ **集成与真机验证由 Lead 做**。★ 你的输出必须是**一份计划**（JSON / `.patch`）+ **一句"该怎么应用"**。
★ 理由：★ 本仓已修 **18 条**"注册 ≠ 能跑"（★ 注入键 ≠ 形参名 11 · 缺必填参 1 · 硬前置 1 · 显式拒 4 · **缺 `return` 1**）
  ⇒ ★★ **生成出来的东西必须逐条真机验过才算数**。
★ 已发生的事故：★ `create_sweep_report` **成功路径没有 `return`** ⇒ 调用方拿到 `None`，
  ★ 一度被读成"API 没建成"（★ 结论碰巧对了、★ **但当时没有证据**）。

## 约束 3 · **批量脚本必须先证明只做加法**（★ 事实 61，★ 本仓真出过事故）
★ 曾有脚本把 `process_queue` **连 232 行一起删掉**（`git diff --stat` 显示 **232 deletions**）。
⇒ ★★ **你的生成器不许直接改文件**；★ 若将来有人拿它落笔，★ **必须先 `git diff --stat` 确认 `deletions == 0`**。

---

# 第 5 部分 · ★★ 你的生成器**必须**在这两个上不误报（★ 并在报告里报结果）

| 负例 | 为什么 |
|---|---|
| ★★ **`FeatureCut4`** | ★ 本仓事实 1：它是**正确入口**，★ 却在废弃名单里 ⇒ ★ **任何"扫到废弃名字就报"的生成器都必须不报它** |
| ★ **`Name` / `GetBodies2` / `GetEdges` / `CreateLine`** | ★ 同名不同接口，只有个别接口废弃 |
| ★★ **`part_sweep` / `part_loft`** | ★★ **已手工修好** ⇒ 说它们"缺 `pre_call`"**是过期的** |
| ★ **`surface_fill` 的硬前置** · ★ **`create_sweep_report` 缺 `return`** · ★ **`Select2` → `Select4`** | ★ **都已修** |

---

# 第 6 部分 · ★★★ 输出要求（★ 按此顺序，做到哪算哪）

## ★★ 第一步（★ 先做这个并落盘）
`specs/202-user-coverage-gaps/recon/GEN-SPEC.md`
★ 一张总设计表：★ 每类一行 ——
`类名 · 输入（哪个文件、什么字段）· 判据（怎么判"这一类"）· 输出（计划长什么样）· 应用方式 · 风险 · 优先级`

## ★★ 第二步：**只挑一类，把它做完**（★ 不要三类同时半成品）
★ 实现 `tools/gen_<类名>.py`，★ 要求（★ 每条都对着本仓已有的教训）：
- ★ **只读**；★ 输出写 `output/gen-<类名>-plan.json`；
- ★★ **自带覆盖面自报**：★ 必须打印「**扫了几条 spec / 判了几条 / 命中几条**」
  （★ 教训：★ 我曾写出"0 处不符"的**空判据**，★ 是因为读了不存在的字段 `p.type`，★ 而真字段是 `p.kind`）；
- ★★ **判据要跟调用图**：★ 只看 spec 文档会把范围判大，★ **要落到函数体**
  （★ 教训：★ 我把 3 个 `pre_call` 判成"没回读计数"，★ 而它们其实是**薄包装**，★ 跟着调用图才发现）；
- ★★ **先标定再输出**：★ 报"命中几条"，★ 并**抽 5 条自证**是不是假阳性；
- ★★ **自带负例**：★ 跑一遍第 5 部分，★ 报出它**不会**误报那些。

## ★ 第三步：★ 再挑第二类，同样做完
## ★（★ 还有额度）★ 第四步：★ 给"应用器"设计（★ 把计划落成 `.patch` 的东西，★ 但**仍然不落笔**）

---

# 第 7 部分 · ★ 搜索配方（★ 直接用）

```bash
cd D:\AI\SW

# ① 所有 ToolSpec 的 pre_call / param_alias / 参数现状
grep -n "pre_call=\|param_alias=\|^        name=\"\|Param(" mcp-server/tool_specs_batch*.py

# ② 所有"读到选区计数"的前置（★ 这些必须有 pre_call 或"给选区"的参数）
grep -n "GetSelectedObjectCount2" scripts/*.py mcp-server/*.py

# ③ 所有 COM 成员名（★ 拿去与 official-members-index.json 对）
grep -oh 'get_com_member([^,]*, *"[A-Za-z_][A-Za-z0-9_]*"' scripts/*.py | sort | uniq -c | sort -rn

# ④ 当字面量传的整数（★ 拿去与 C:\swapi\enums\ 对）
grep -n "get_com_member(.*, *[0-9]\{1,4\}" scripts/*.py

# ⑤ ★★ 全仓"声明返回 dict、但最后一条语句不是 return"的（★ 这是已找到的一类通用形态）
python - <<'PY'
import ast, pathlib
for f in list(pathlib.Path("scripts").glob("*.py")) + list(pathlib.Path("mcp-server").glob("*.py")):
    try: t = ast.parse(f.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError: continue
    for n in ast.walk(t):
        if (isinstance(n, ast.FunctionDef) and n.body
                and not isinstance(n.body[-1], (ast.Return, ast.Raise))
                and n.returns is not None and "dict" in ast.unparse(n.returns)):
            print(f"{f}:{n.lineno} {n.name}  最后一条={type(n.body[-1]).__name__}")
PY

# ⑥ 已有的分类/统计脚本（★ 可以直接跑）
python tools/classify_audit_divergences.py      # 30 份核对表的分歧分类
python tools/gen_precall_patch.py               # 生成器原型（类 1）
```

---

# 第 8 部分 · 纪律

- ★★ **只写你亲手读到的**；★ 每条论断给**可搜索的原文位置**（★ **不写行号**，★ 写**原文片段**）；
- ★★ **查不到就说查不到**（★ 本仓铁律 5）；
- ★★ **不许写"建议注意 / 建议进一步分析"**；
- ★★ **宁少勿滥** —— ★ **一个做完的类好过三个半成品**（★ 半成品无法验证 = 零）；
- ★★ **每完成一步立刻落盘**；
- ★★ **不要改仓库里任何文件**（★ 你的产物只写进 `output/` 与 `specs/.../recon/`）。

---

# 第 9 部分 · ★ 你可以（也鼓励）挑战的既有结论

★★ 如果你认为 §0 里"三类可批量"的划分**不对**（★ 比如某类其实不可批量、★ 或还有**第四类**没被列出），
★ **直接说，并给判据与证据**。★ 本仓**欢迎推翻既有结论** —— ★ 这一轮我就自己推翻了三条：
★ 事实 **509** 证伪了 **503** 的机制 · ★ 事实 **510** 证伪了"判据报 0 就没问题" · ★ 事实 **511** 证伪了"按名字扫废弃"。
★★ 但**推翻必须带证据**，★ 且**必须拿第 5 部分的负例试过**。
