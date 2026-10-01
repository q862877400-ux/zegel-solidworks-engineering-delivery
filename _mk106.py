import json
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

# ── ① 写进 backend_catalog 的 pywin32 限制（A1 的「不做 + 原因」正主）────────────
Q = Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml")
d = json.loads(Q.read_text(encoding="utf-8"))
ADD = "".join([
    "**第二类具体化实例（2026-10-01 轮 186 实测）：`ISafeArrayUtility` 是**给 C++ 的**，pywin32 到不了** —— ",
    "一条外部评审把它列为「高杠杆缺口」（说官方给了数组工具集而我们到处手搓 `VARIANT(...)`），",
    "★ **实测否定**：`tools/probe_safearray_utility.py`（CommandInProgress 置位、不开文档、收尾轮询点掉）——",
    "① `ISldWorks.GetSafeArrayUtility()` **返回 `CDispatch`（对象拿得到）**；",
    "② 官方登记的**全部 21 个成员**逐个试 ⇒ **迟到绑定可达 0/21**（每个都 `AttributeError: <unknown>.X`）；",
    "③ 类型信息内省 ⇒ `com_error: (-2147352565, '无效索引。')` ⇒ **没有可用的 dispinterface**；",
    "④ 官方 `_overview.md` 的 Remarks 原话：「The ISafeArrayUtility interface replaces the SOLIDWORKS ",
    "**SafeArray template class**, which you might have used in earlier versions of SOLIDWORKS to instantiate ",
    "SafeArrays for methods requiring Variant arrays in **your C++ projects**。」",
    "⇒ ★★ 与本后端**第一类实例（事实 47 的 `IAccessSelections` / `SetFixedFace`）同一族**。",
    "★★★ **推论（重要）**：官方 md 明写它是**取代 C++ 的 SafeArray 模板类** —— 即在脚本语言里",
    "「本就有原生数组」⇒ 它**不是**本项目手搓 `VARIANT(VT_ARRAY|...)` 的替身。",
    "⚠ **不要再把它当「该补的缺口」**：它不到「编目录」以下任何一级。",
    "⚠ **另记一个被证伪的静态信号**：曾以为「`IX` 有成员而其无 `I` 孪生段为空 ⇒ 迟到绑定到不了」，",
    "实测**证伪** —— 1032 个接口段里 504 对有孪生、**502 对的孪生是空的**，而其中包含",
    "`ISldWorks` / `IModelDoc2` / `IFeatureManager` / `ISketchManager` / `ISelectionMgr` / `IFace2`",
    "**这些全都能用** ⇒ ☆ 该信号若做成门禁会**同时**给出 502 个假阳性。",
    "★ **判据只能用真机逐接口穷尽枚举**（与事实 47 的结论一致）。",
])
bc = d["backend_catalog"]["solidworks-com-pywin32"]
if not any("ISafeArrayUtility" in s for s in bc["limitations"]):
    bc["limitations"].append(ADD)
    print("  ok backend_catalog 已加 ISafeArrayUtility 实例")
else:
    print("  已有")
Q.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

# ── ② 事实 126 ───────────────────────────────────────────────────────
K = Path(r"D:\AI\SW\docs\known-facts.md")
tk = K.read_text(encoding="utf-8")
FACT = "| 126 | " + "".join([
    "**`ISafeArrayUtility` 是给 C++ 的，pywin32 到不了（21/21 不可达、无 dispinterface）—— ",
    "一条外部评审的「高杠杆」建议被实测否定** —— 2026-10-01（轮 186）。",
    "★ 评审的说法（§七）：官方给了 21 个成员的数组工具集，而本项目到处手搓 `VARIANT(...)`",
    "（事实 12 / 33 / 68 / 123 / 167）⇒ 「可能一次性替掉一批手搓代码」。",
    "★★★ **实测否定**（`tools/probe_safearray_utility.py`，真机、`CommandInProgress` 置位、不开文档）：",
    "```",
    "① ISldWorks.GetSafeArrayUtility()  ⇒ **返回 CDispatch（对象拿得到）**",
    "② 官方登记的全部 **21 个成员**逐个试 ⇒ **可达 0/21**（每个都 AttributeError: <unknown>.X）",
    "③ 类型信息内省 ⇒ com_error(-2147352565, '无效索引。') ⇒ **没有可用的 dispinterface**",
    "```",
    "★★ **官方自己写明了原因**（`C:/swapi/types/ISafeArrayUtility/_overview.md` 的 Remarks）：",
    "> \"The ISafeArrayUtility interface replaces the SOLIDWORKS **SafeArray template class**, which you might ",
    ">  have used in earlier versions of SOLIDWORKS to instantiate SafeArrays for methods requiring Variant ",
    ">  arrays in **your C++ projects**.\"",
    "⇒ ★★★ 即：它是**取代 C++ 的 SafeArray 模板类**的便利件 —— 在脚本语言里**本就有原生数组**",
    "⇒ **它不是我们手搓 `VARIANT(...)` 的替身**。★ 与**事实 47**（`IAccessSelections` / `SetFixedFace`",
    "「仅进程内非托管 C++」）**同一族**，已记进 `capabilities.yaml` 的 `backend_catalog` 限制段。",
    "⚠⚠⚠ **另记一个被证伪的静态信号（本轮差点做成门禁）**：",
    "```",
    "猜想：`IX` 有成员、而它的**无 I 孪生段**存在且为空 ⇒ 该接口只有 vtable ⇒ 迟到绑定到不了",
    "实测：1032 个接口段里 **504 对有孪生、502 对的孪生是空的**",
    "★★ 而其中包含 ISldWorks / IModelDoc2 / IFeatureManager / ISketchManager / ISelectionMgr / IFace2",
    "   —— **这些全都能用** ⇒ 该信号**完全不能预测可达性**",
    "⇒ ☆ 若做成门禁，会**同时**给出 502 个假阳性（★ 又一次「判据要锚在权威源、并做对照」）",
    "```",
    "★ **可复用判据**（本轮立）：判「一个官方接口在本后端可达吗」**只能真机逐接口穷尽枚举**",
    "（全部成员名 + 类型信息），**没有静态捷径** —— 与事实 47 的结论一致。",
    " | `tools/probe_safearray_utility.py`；`D:/AI/SW/output/safearray-utility-probe.json`；",
    "`capabilities.yaml` 的 `backend_catalog.solidworks-com-pywin32.limitations`；事实 47 / 62 |",
])
if "| 126 |" not in tk:
    K.write_text(tk.rstrip() + "\n\n" + FACT + "\n", encoding="utf-8")
    print("  ok known-facts 已加 126")
else:
    print("  已有 126")

# ── ③ Spec Kit 106 ───────────────────────────────────────────────────
S = Path(r"D:\AI\SW\specs\106-safearray-utility-is-cpp-only")
S.mkdir(parents=True, exist_ok=True)
spec = """# 106 · `ISafeArrayUtility` 是**给 C++ 的**，pywin32 到不了 —— 一条外部「高杠杆」建议被实测否定

**Status**: Implemented（轮 186）· ⚠ **负结果**（含一个**被证伪的静态信号**）

## 一、起因（外部评审 §七）
```
一条外部评审把 `ISafeArrayUtility`（台账 used=0、21 成员）列为本项目**唯一高杠杆**缺口：
「官方给了数组工具集，而本项目到处手搓 VARIANT(...)」——
  事实 12 / 33 / 68 / 123 / 167 都是这类坑
★ 但评审**没验证可达性**（它自己 §十三 写了「未连 SolidWorks」）。
```

## 二、★★★ 实测否定
```
tools/probe_safearray_utility.py（真机 · CommandInProgress 置位 · 不开文档 · 收尾轮询点掉）
① ISldWorks.GetSafeArrayUtility()  ⇒ **返回 CDispatch（对象拿得到）**
② 官方登记的全部 **21 个成员**逐个试 ⇒ **可达 0/21**（每个都 `AttributeError: <unknown>.X`）
③ 类型信息内省 ⇒ `com_error(-2147352565, '无效索引。')` ⇒ **没有可用的 dispinterface**
```

## 三、★★ 官方自己写明了原因
> "The ISafeArrayUtility interface replaces the SOLIDWORKS **SafeArray template class**, which you might
>  have used in earlier versions of SOLIDWORKS to instantiate SafeArrays for methods requiring Variant
>  arrays in **your C++ projects**." —— `C:/swapi/types/ISafeArrayUtility/_overview.md`

⇒ ★★★ 它是**取代 C++ 的 SafeArray 模板类**的便利件；在脚本语言里**本就有原生数组**
⇒ **它不是我们手搓 `VARIANT(...)` 的替身**。
★ 与**事实 47**（`IAccessSelections` / `SetFixedFace`「仅进程内非托管 C++」）**同一族**。

## 四、⚠⚠⚠ 一个被我**证伪**的静态信号（差点做成门禁）
```
猜想：`IX` 有成员、而它的无 I 孪生段存在且为空 ⇒ 只有 vtable ⇒ 迟到绑定到不了
实测：1032 个接口段里 **504 对有孪生、502 对的孪生是空的**
★★ 而其中包含 ISldWorks / IModelDoc2 / IFeatureManager / ISketchManager / ISelectionMgr / IFace2
   —— **这些全都能用** ⇒ 该信号**完全不能预测可达性**
⇒ ☆ 若做成门禁，会**同时**给出 **502 个假阳性**
```

## 五、★ 立下的可复用判据
> 判「一个官方接口在本后端可达吗」**只能真机逐接口穷尽枚举**（全部成员名 + 类型信息），
> **没有静态捷径** —— 与事实 47 的结论一致。

## 六、判据
| ID | 判据 |
|---|---|
| SC-10601 | ★★ 从反射拿到官方 21 个成员名单（**穷尽**，不只试几个）|
| SC-10602 | ★★★ 真机逐成员试 ⇒ **0/21** + 无 dispinterface |
| SC-10603 | ★★ 找到官方的**原因**（Remarks：取代 C++ 的 SafeArray 模板类）|
| SC-10604 | ★ 记进 `backend_catalog`（A1 的「不做 + 原因」正主）|
| SC-10605 | ★★★ **证伪**那个诱人的静态信号（并写出若做成门禁的后果：502 假阳性）|
| SC-10606 | 门禁 + 回归不退化 |

## ⚠ 明确记下的限度
* ⚠ 未试 `comtypes` / C# PIA 后端（它们**可能**能驱动 `out` 形参）—— 本轮只判 **pywin32**；
* ⚠ 「0/21 可达」是**迟到绑定**口径；若有现成 makepy 生成的早绑定模块，结论**未验**；
* ⚠ `PackVariant` 的 `ref Int32 Data` 形态**始终没查明**（因为压根够不到）；
* ⚠ 本轮**没有**因此改动任何生产代码（结论是「不做」，不是「实现」）。
"""
plan = """# 106 · Plan

## 步骤
1. 评审 §七 说 `ISafeArrayUtility` 是高杠杆缺口 ⇒ ★ 但它没验证可达性
2. ★ 读官方：反射 21 成员 + `_overview.md` 的 Remarks
3. ★★ 写探针：①拿对象 ②`Get*` 半边 ③`out` 形参（byref）④`Int32&` ⑤`PackVariant`
4. ⚠ 前 5 项全 `AttributeError` ⇒ ★ **不做结论**，先把**全部 21 个**穷尽扫一遍
5. ⚠ 仍 0/21 + `GetTypeInfo` 报「无效索引」⇒ **无 dispinterface** ⇒ 定论
6. ★ 官方 Remarks 给出原因 ⇒ 它是给 C++ 的
7. ★★ 顺手验证一个诱人的静态信号（空孪生）⇒ **被对照证伪**（502/504）
8. 落三处：`backend_catalog` / 事实 126 / 本 Spec Kit → 门禁 + 回归 → 收工

## 风险与对策
| 风险 | 对策 |
|---|---|
| 只试几个成员就下结论 | ★ **穷尽官方 21 个**（轮 185 的教训）|
| 把「够不到」写成"该做但难" | ★ 记成**不做 + 原因**（A1 的写法）|
| 把诱人的静态信号做成门禁 | ★ **先做对照** ⇒ 证伪（否则 502 假阳性）|
| 顺手去实现它 | ★ **不实现**（它够不到）|
"""
tasks = """# 106 · Tasks（全部完成，轮 186）

- [x] T-10601 读官方（反射 21 成员 + `_overview` Remarks）
- [x] T-10602 ★★★ 真机探针 `→ 验收:` `python tools/probe_safearray_utility.py`（**0/21 · 无 dispinterface**）
- [x] T-10603 ★★ 落进 `backend_catalog` 限制段（不做 + 原因）
- [x] T-10604 ★★★ 证伪「空孪生」静态信号
- [x] T-10605 事实 126
- [x] T-10606 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
"""
converge = """# 106 · Converge

**Converged**: 2026-10-01（轮 186）

## 一、结果
| 判据 | 结论 |
|---|---|
| SC-10601 穷尽成员名单 | ✅ 21 个 |
| SC-10602 真机 0/21 + 无 dispinterface | ✅ |
| SC-10603 官方原因 | ✅ 给 C++ 的 |
| SC-10604 落 backend_catalog | ✅ |
| SC-10605 证伪静态信号 | ✅ 502/504 |
| SC-10606 门禁 + 回归 | ✅ |

## 二、★★★ 本轮的价值：把一条「看起来该做」的缺口变成了**有证据的「不做」**
```
外部评审说它「高杠杆」⇒ ★ 若我照做，会花很多轮去包一个**根本够不到**的接口
实测 ⇒ **0/21 可达 + 无 dispinterface + 官方说它是给 C++ 的**
⇒ ★ 这正是 A1 要求的写法：「每一格都有来源，**或写明「不做 + 原因」**」——
   本轮补的是**那一半**：把「没做」变成"**有证据地不做**"。
```

## 三、★ 而那 502 个假阳性是本轮最该记住的
```
「空孪生 ⇒ 到不了」听起来极合理（ISafeArrayUtility 恰好符合），
★ 而对照一做就塌：ISldWorks / IModelDoc2 / IFeatureManager … **全都符合却全都能用**
⇒ ☆ 这就是事实 62 的价值：**负例/对照是唯一的证明** ——
   本轮若省了那一步，会往仓库里装一个 502 假阳性的门禁。
```

## 四、未查证
* ⚠ **只判 pywin32 迟到绑定**：`comtypes` / C# PIA **是否**能驱动这些 `out` 形参**未验**；
* ⚠ 若有 makepy 早绑定模块，结论未验；
* ⚠ `PackVariant` 的 `ref Int32 Data` 形态**没查明**（够不到，故无从查）；
* ⚠ 本轮**没改**任何生产代码（结论是「不做」）。
"""
for name, text in (("spec.md", spec), ("plan.md", plan), ("tasks.md", tasks), ("converge.md", converge)):
    (S / name).write_text(text, encoding="utf-8")
    print("  written %s" % name)
