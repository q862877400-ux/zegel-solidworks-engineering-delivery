import json
import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

# ── 事实 112 ────────────────────────────────────────────────────────
K = Path(r"D:\AI\SW\docs\known-facts.md")
tk = K.read_text(encoding="utf-8")
FACT = "| 112 | " + "".join([
    "**`mold_evidence` 真机**永远全 None** —— 它从**错的接口**读（成员在 `I*FeatureData` 上），",
    "而**假对象恰好有那些成员** ⇒ 17 处契约测试全绿** —— 2026-10-01（轮 172）。",
    "★ 起因：`mold_tools` 是 `stitched` 且 **evidence 为空**，我想给它的 **COM 侧**取证。",
    "★ 真机（`tools/probe_mold_evidence_readers.py`，**新零件**，**两种取法都试**）：",
    "```",
    "IFeatureManager.GetPartingLinesCount / GetPartingSurfacesCount /",
    "  GetCavitySurfacesCount / GetCoreSurfacesCount   ⇒ **全 AttributeError: <unknown>.X**",
    "IModelDoc2.PartingType / CoreCavitySplit          ⇒ **同样不存在**",
    "（get_com_member 与 call_com_member **两种**取法结果一致 ⇒ 不是「取法」问题）",
    "```",
    "★★★ **查反射/swapi 得到真正的归属**（**事实 36** 那一族：**成员在别的接口上**）：",
    "```",
    "GetPartingLinesCount    ⇒ **IPartingLineFeatureData**（另有 IDraftFeatureData2 同名成员）",
    "GetPartingSurfacesCount ⇒ I*FeatureData（swapi 有独立说明页）",
    "PartingType             ⇒ **IPartingSurfaceFeatureData**",
    "CoreCavitySplit         ⇒ **IPartingLineFeatureData**",
    "```",
    "⇒ ★★★ 所以从 `FeatureManager` / `model` 上读**永远是 None** ⇒ 「全 None」**不是「空件没有分型」**，",
    "而是**读错了对象**。⚠ **要真读到**必须先拿到对应的 `I*FeatureData`**（从**已存在的**分型线/分型面特征上取）",
    "⇒ ★ **前提是零件上已经有那些特征**；空零件上**本来就取不到**（**两者表象相同，别混**）。",
    "★★ **这是「假对象测试看不见真契约」的第 4 次**（前三次：事实 99 干涉检查三个成员名全错 ·",
    "101 `sketch_relations` 漏扫 · 106 `AddIndicator` 取值不在清单）：",
    "**假对象有那个成员 ⇒ 测试绿 ⇒ 真机全空**。",
    "★ 处置：① **如实更正** `mold_evidence` 的 docstring（写明它**在真机上只会全 None**，",
    "**不假装能读** —— 铁律 5）；② 补一条**能开火**的负例测试",
    "（用**没有那些成员**的假对象 ⇒ 断言**必须是 None、不许变成 0**）；③ 修法（从 FeatureData 取）",
    "**需要**有分型特征的零件才能验证 ⇒ **未做**，记在限度里。",
    " | `tools/probe_mold_evidence_readers.py`；`C:/swapi/types/IPartingLineFeatureData/`；",
    "`IPartingSurfaceFeatureData/PartingType.md`；事实 36 / 99 / 101 / 106 |",
])
if "| 112 |" not in tk:
    K.write_text(tk.rstrip() + "\n\n" + FACT + "\n", encoding="utf-8")
    print("  ok known-facts 已加 112")
else:
    print("  已有 112")

# ── Spec Kit 092 ────────────────────────────────────────────────────
S = Path(r"D:\AI\SW\specs\092-mold-evidence-wrong-interface")
S.mkdir(parents=True, exist_ok=True)
spec = """# 092 · `mold_evidence` 从**错的接口**读 ⇒ 真机永远全 None；假对象测试全绿

**Status**: Implemented（轮 172）· ⚠ **未修功能**（只更正了文档 + 补了负例）· `mold_tools` 仍 `stitched`

## 一、动机
`mold_tools` 是 **`stitched`** 且 **`evidence` 为空**；它的第 3 条限度说
「本机没有 OCP/cadquery/trimesh ⇒ 涉及 **headless-occt** 的声明无法复现」。
★ 但同一条目的第 1 条说「新增 `scripts/sw_mold.py`（… + `mold_evidence`）」——
★★ **那是我们自己的 COM 侧能力**，**可以真机验** ⇒ 本轮给它取证。

## 二、★★★ 真机结果（`tools/probe_mold_evidence_readers.py`）
```
IFeatureManager.GetPartingLinesCount / GetPartingSurfacesCount /
  GetCavitySurfacesCount / GetCoreSurfacesCount   ⇒ **全 AttributeError: <unknown>.X**
IModelDoc2.PartingType / CoreCavitySplit          ⇒ **同样不存在**
（get_com_member 与 call_com_member **两种**取法结果一致 ⇒ 不是「取法」问题）
```

## 三、★★★ 根因：成员在**别的接口**上（事实 36 那一族）
```
GetPartingLinesCount    ⇒ **IPartingLineFeatureData**（另有 IDraftFeatureData2 同名成员）
GetPartingSurfacesCount ⇒ I*FeatureData（swapi 有独立说明页）
PartingType             ⇒ **IPartingSurfaceFeatureData**
CoreCavitySplit         ⇒ **IPartingLineFeatureData**
```
⇒ 从 `FeatureManager` / `model` 上读**永远是 None** ⇒
★ **「全 None」不是「空件没有分型」，而是「读错了对象」。**
⚠ **要真读到**必须先拿到对应的 `I*FeatureData`（从**已存在的**分型线/分型面特征上取）
⇒ ★ **前提是零件上已经有那些特征**；空零件上**本来就取不到**（**两者表象相同，别混**）。

## 四、★★ 这是「假对象测试看不见真契约」的**第 4 次**
| 次 | 事实 | 假对象看不见的东西 |
|---|---|---|
| 1 | 99 | 干涉检查用了**三个不存在的成员名** |
| 2 | 101 | `sketch_relations` 因为**无 `sw_` 前缀**被整体漏扫 |
| 3 | 106 | `AddIndicator` 的 `TolType` **取值不在官方清单** |
| 4 | **112** | `mold_evidence` 的成员**在错的接口上** ⇒ 假对象恰好**有**它们 |

## 五、处置（三条）
```
① **如实更正** `mold_evidence` 的 docstring：写明它**在真机上只会全 None**、**不假装能读**（铁律 5）
② 补一条**能开火**的负例测试：用**没有那些成员**的假对象 ⇒ 断言**必须是 None、不许变成 0**
③ 修法（从 FeatureData 取）**需要**有分型特征的零件才能验证 ⇒ **未做**，记进限度
```

## 六、判据
| ID | 判据 |
|---|---|
| SC-9201 | ★★ **两种取法都试**（`get_` / `call_`）⇒ 排除「取法不对」|
| SC-9202 | ★★★ **查清归属**：4 个计数 + 2 个属性在 `I*FeatureData` 上，**不在** `IFeatureManager`/`IModelDoc2` |
| SC-9203 | ★★ 分辨「**空件没有**」与「**读错对象**」（两者表象相同）|
| SC-9204 | ★ 如实更正 docstring（**不假装能读**）|
| SC-9205 | ★ 补**能开火**的负例测试（成员缺席 ⇒ 必须 `None`，不许变 0）· 契约 **11 passed** |
| SC-9206 | 门禁 + 回归不退化 |

## ⚠ 明确记下的限度
* ⚠ **功能未修** —— `mold_evidence` **仍从旧位置读** ⇒ 真机上**仍只会全 None**；
* ⚠ 修法（从 `I*FeatureData` 取）需要**有分型线/分型面特征的零件** ⇒ 本轮**没有**那样的件，**未验证**；
* ⚠ 「成员不在 `IFeatureManager` 上」是**真机 + 两种取法**证实的；
  「它们在 `I*FeatureData` 上」来自 **swapi/反射**（**未经真机调用**）；
* ⚠ `mold_tools` **仍为 `stitched`**（本轮**没有**升它 —— 读取侧是空壳，写入侧在未准备件上会弹框）。
"""
plan = """# 092 · Plan

## 步骤
1. `mold_tools` 是 `stitched` 且 evidence 空 ⇒ 给它的 **COM 侧**取证
2. ★ 写真机冒烟跑 `mold_evidence` ⇒ ⚠ **判据先错**（我以为键是扁平的，实际是嵌套的 `counts`）
   ⇒ ★ **是判据错，不是函数坏** ⇒ 读实现改正判据
3. ★★ 真机全 `None`（连 `parting_type` 也是）⇒ ⚠ **可疑**：没有应当是 **0**，不是 `None`
4. ★★ 探针**两种取法都试** ⇒ **全 AttributeError** ⇒ 不是取法问题
5. ★★★ 查反射/swapi 得**归属**：在 `I*FeatureData` 上（事实 36 那一族）⇒ **根因**
6. ★ 更正 docstring（不假装能读）+ 补能开火的负例测试
7. 事实 112 → 门禁 + 回归 → 收工

## 风险与对策
| 风险 | 对策 |
|---|---|
| 判据与实现形状不符 | ★ **读实现再改判据**（本轮犯了又改）|
| 把「全 None」当成「空件没有」 | ★ **两种取法对照** ⇒ 才敢说"读错对象" |
| 假对象全绿就当能用 | ★ **负例测试**（成员缺席 ⇒ 必须 None）|
| 顺手升 `stitched` | ★ **不升** —— 读取侧是空壳、写入侧未验 |
"""
tasks = """# 092 · Tasks（全部完成，轮 172）

- [x] T-9201 真机冒烟 `mold_evidence` `→ 验收:` `python tools/verify_mold_evidence_smoke.py`
- [x] T-9202 两种取法对照 `→ 验收:` `python tools/probe_mold_evidence_readers.py`（**全 AttributeError**）
- [x] T-9203 查归属（`I*FeatureData`）⇒ 根因
- [x] T-9204 更正 docstring + 补负例测试 `→ 验收:` `python -m pytest tests/test_sw_mold_contract.py -q`（**11 passed**）
- [x] T-9205 事实 112
- [x] T-9206 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
"""
converge = """# 092 · Converge

**Converged**: 2026-10-01（轮 172）

## 一、结果
| 判据 | 结论 |
|---|---|
| SC-9201 两种取法 | ✅ 全 AttributeError |
| SC-9202 查清归属 | ✅ `I*FeatureData` |
| SC-9203 分辨「没有」与「读错」 | ✅ 读错对象 |
| SC-9204 更正 docstring | ✅ |
| SC-9205 负例测试 | ✅ 11 passed |
| SC-9206 门禁 + 回归 | ✅ |

## 二、★★★ 第 4 次「假对象测试看不见真契约」
```
99  干涉检查：三个**不存在的成员名**          ⇒ 一直绿而真机永远坏
101 sketch_relations：**无 sw_ 前缀**被整体漏扫
106 AddIndicator：TolType **取值不在官方清单**
112 mold_evidence：成员**在错的接口上**      ⇒ 假对象恰好**有**它们
⇒ ★★ 收敛成一句：**假对象能测「逻辑」，测不出「成员名 / 接口归属 / 取值 / 实参形态」。**
  这四样**只有真机（或对官方源做静态比对）能证**。
```

## 三、★ 一次「判据先错」的自我更正
```
我第一版判据以为 `mold_evidence` 的键是**扁平的**（4 个计数 + 2 个属性）⇒ 报 2/6
★ 读实现 ⇒ 实际是**嵌套的**（计数在 `counts` 子字典里）⇒ **是判据错，不是函数坏**
⇒ ★ 老教训（事实 51 那一族）：**判据要贴合实现的实际结构**，别凭印象写。
```

## 四、未查证
* ⚠ **功能未修**：`mold_evidence` 仍从旧位置读 ⇒ 真机仍全 None；
* ⚠ 从 `I*FeatureData` 取**需要有分型特征的零件** ⇒ 本轮没有那样的件，**未验证**；
* ⚠ 「成员不在 `IFeatureManager` 上」是**真机**证实的；「它们在 `I*FeatureData` 上」来自**官方源**（**未经真机调用**）；
* ⚠ `mold_tools` **仍 `stitched`**（本轮**没有**升它）。
"""
for name, text in (("spec.md", spec), ("plan.md", plan), ("tasks.md", tasks), ("converge.md", converge)):
    (S / name).write_text(text, encoding="utf-8")
    print("  written %s" % name)
