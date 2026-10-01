import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW\docs\ROADMAP.md")
B = """           607 🎯 **Spec Kit `109`：用**类型库方向信息**复核既有 byref 口径 ⇒ ****负结果：口径无害****（但机制性反例存在）**（轮 189）——
               起因：`scripts/audit_byref_args.py` 的口径写「`Int32&` **算**一个（必须传），
               `Object&` / `Variant&` / `Dispatch&` **不算**（纯出参，不用传）」——
               ★ 它**来自反射文本**，而反射的 `&` **只说明"按引用"、不区分方向** ⇒ 那原本是**假设**。
               ★★ 而轮 188 用**类型库方法表**（第 4 套源）发现它**给方向**，且
               `PutDouble(VariantArray = **in,out**)` 是**必须传**的数组形参 ⇒ 机制上会漏。
            608 ★★★ **实测**（`tools/audit_inout_array_params.py`，纯静态）：
               ```
               扫了 **507** 个接口
               含 `in,out` 数组类形参（VARIANT / LP_tagVARIANT / POINTER(IDispatch) / POINTER(IUnknown)）
                 = **62** 条记录 ⇒ 去重 **29** 对（IBody2.GetMiddleSurface · IFeature.GetBox ·
                 ICustomPropertyManager.GetAll/2/3 · IBomFeature.GetConfigurations …）
               ★★ 而**本仓库生产代码按字面量调用过的 = 0**（命中的 2 个只在探针里）
               ★ **扩大检查面**（全仓库、排除探针/登记表/测试/生成物、**连点调用也算**）⇒ **仍 0**
               ```
               ⇒ ★★★ **那条口径在实践中**目前**无害** —— 不是因为它对，而是因为**我们还没碰那 29 对成员**。
               ⇒ ★★ **机制上成立 ≠ 调用面上命中**：前者说明「**将来会踩**」，不等于「**现在有缺陷**」。
                 处置**不是改规则**（那会是"没人用的守卫" —— 事实 40 的教训），而是
                 **把查证写进口径说明 + 把清单存档**，等真要碰时先查。
            609 ★★★ **顺手抓到一处**源间方向分歧**（铁律 4 的具体实例）**：
               ```
               同一个 PutDouble 的 VariantArray：
                 · swapi md    : `out`        （"void PutDouble( out System.object VariantArray, …)"）
                 · 反射文本    : `Object&`    （只说明按引用，**无方向**）
                 · 类型库      : **`in,out`** （comtypes flag=3）
                                 ★ 同表里 GetInfo 的 Count/Type 是 **flag=10 = out** ⇒ 它**确实在区分**，不是默认值
                 · 实测（轮 188）: 传**全新** VARIANT() ⇒ **没回写** ⇒ 与 **in,out** 一致
                                   （PutDouble 是**往已有数组里追加** ⇒ 需要**已有的**数组）
               ⇒ ★ 按**铁律 4**（冲突以**出厂类型库**为准）⇒ **类型库赢**，md 的 `out` 是**简化措辞**。
               ```
            610 ★ **产出**：① `tools/audit_inout_array_params.py` + 清单 `output/inout-array-params.json`；
               ② ★ 把查证结果**写回 `scripts/audit_byref_args.py` 的口径段** ⇒ 那条规则从**假设**变成**被查证过**；
               ③ ★ **将来要调那 29 对成员**（**必须先传一个已构造的数组**）⇒ **先查那张清单**。
               ★★ 而"扩大检查面"这一步是本轮**唯一挡住假结论**的东西：第一版只查字面量形态 ⇒ 报「2 命中」，
                 若就此收工，「生产代码 0 命中」**是没保证的**（点调用看不见）⇒ 扩大后仍 0 ⇒ 结论才站得住。
               门禁 + `release_check` exit 0 · 回归 **1248 passed**。
               ⚑ **未查证**：⚠ **只覆盖 `sldworks.tlb`**（`cosworks.tlb` 等 20+ 个未扫）；
                 ⚠ **走变量传成员名**的调用**看不见**；⚠「29 对都不调」**只对当前树成立**；
                 ⚠ comtypes 的 `flags` 为 **`None`** 的那部分**未逐条列出**（本轮只统计）；
                 ⚠ 本轮**没改任何生产逻辑**（只改注释/口径说明）。
               下轮候选：① 把方向扫描**扩到 `cosworks.tlb`**（仿真域是我们真正大量调用的那一块）；
               ② 逐条判审计 §八 那 25 个零调用族「该做 / 不做 + 原因」；
               ③ 回到在上下文链（`SketchUseEdge3` 静默无效）。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None, "找不到『阻塞:』锚点"
before = "".join(lines)
if re.search(r"^\s+607 ", before, re.M):
    print("  游标 607 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+610 ", R.read_text(encoding="utf-8"), re.M), "复核失败"
    print("  复核: 610 行已存在 ✓")
