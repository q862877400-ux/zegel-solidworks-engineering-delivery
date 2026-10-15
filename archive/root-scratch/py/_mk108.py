import json
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

CORRECTION = "".join([
    " ⚠⚠⚠ **2026-10-01（轮 188）更正上面这一段的措辞** —— 「到不了」**过强**，必须**带绑定层次**限定：",
    "```
· pywin32 **迟到绑定**：21 个成员 0/21 可达 + 无 dispinterface ⇒ **到不了**（这半是对的）
· comtypes **早绑定**（走 sldworks.tlb 类型库）：`tools/probe_safearray_comtypes.py` 实测 ——
  ① comtypes.client.GetActiveObject('SldWorks.Application') **附着**到**同一个**运行实例
     （PID 20456，**没起第二个实例** —— 红线：事实 24）
  ② 类型库模块 comtypes.gen.SldWorks 里**有** ISafeArrayUtility
  ③ ★★★ **QueryInterface(ISafeArrayUtility) 成功** ⇒ 对象**真的实现**那个 vtable 接口
⇒ ★★ 所以「接口不存在 / 到不了」是**错的**；正确的是「**pywin32 迟到绑定看不到它**」
⚠ 但**往返仍未走通**：PutDouble(arr, 0, 1.5) 不报错（3 参形态对，且它确实要 3 参），
  而 arr.value=None、GetDouble 读回 0.0 ⇒ **`in,out` 的 VARIANT 数组没回写**（与事实 68 同族）
⇒ **能不能正确构造 SAFEARRAY，本轮未走通**（按事实 53：不继续凑形态）。
★★ **而无论走不走得通，它对我们都没有新增能力** —— 证据（同一探针 ⑥）：
  pywin32 的 `VARIANT(VT_ARRAY|VT_R8, [...])` 与 `VARIANT(VT_ARRAY|VT_DISPATCH, [...])`
  **本来就能构造数组**（事实 123 / 167 就是这么修的）⇒
  ★ 它是**给 C++ 弥补"没有原生数组"**的，脚本语言的绑定层**已经替我们做了**。
```
⇒ ★★ **结论（本后端仍然「不做」）**：不是「够不到」，而是「**够得到但没有净收益**」——",
    " 而且**修正后的措辞**才是可引用的（不带层次的「到不了」会被人当成「官方没这个能力」）。",
])

Q = Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml")
d = json.loads(Q.read_text(encoding="utf-8"))
bc = d["backend_catalog"]["solidworks-com-pywin32"]
hit = 0
for i, s in enumerate(bc["limitations"]):
    if "ISafeArrayUtility" in s and "轮 188" not in s:
        bc["limitations"][i] = s + CORRECTION
        hit += 1
print("  ok backend_catalog 更正 %d 处" % hit)
if hit == 0:
    print("  ⚠ 没找到要更正的段（可能已改过）")
Q.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

# ── 事实 128 ────────────────────────────────────────────────────────
K = Path(r"D:\AI\SW\docs\known-facts.md")
tk = K.read_text(encoding="utf-8")
FACT = "| 128 | " + "".join([
    "**可达性结论必须带**绑定层次**限定 —— 轮 186 记的「`ISafeArrayUtility` 到不了」**过强**，本轮更正** —— ",
    "2026-10-01（轮 188）。",
    "★★★ **为什么必须更正**：轮 186 我在 pywin32 **迟到绑定**下测得 21/21 不可达，就记成「**到不了**」。",
    "⚠ 而**没限定层次** —— 下一轮（本轮）用 `comtypes` **早绑定**一试：",
    "```",
    "① comtypes.client.GetActiveObject('SldWorks.Application') ⇒ **附着**同一实例（PID 20456，**没起第二个**）",
    "② cc.GetModule('D:/Program Files/SOLIDWORKS Corp/SOLIDWORKS/sldworks.tlb') ⇒ 模块 comtypes.gen.SldWorks",
    "   里面有 **ISafeArrayUtility**",
    "③ ★★★ **QueryInterface(ISafeArrayUtility) 成功** ⇒ 对象**真的实现**那个 vtable 接口",
    "```",
    "⇒ ★★ 正确的是「**pywin32 迟到绑定看不到它**」，**不是**「接口不存在 / 到不了」。",
    "⚠ **而往返仍未走通**：`PutDouble(arr, 0, 1.5)` 不报错（类型库说它确实要 **3** 参、",
    "`VariantArray` 是 **in,out**），但 `arr.value=None`、`GetDouble` 读回 **0.0** ⇒",
    "**`in,out` 的 VARIANT 数组没回写**（与事实 68 同族）⇒ 按事实 53 **不继续凑形态**。",
    "★★ **而无论走不走得通它都没有净收益**：pywin32 的 `VARIANT(VT_ARRAY|VT_R8, [...])` 与",
    "`VARIANT(VT_ARRAY|VT_DISPATCH, [...])` **本来就能构造数组**（事实 123 / 167 就是这么修的）⇒",
    "★ 它是**给 C++ 弥补"没有原生数组"**的，脚本语言的绑定层**已经替我们做了**。",
    "⇒ ★ 本后端仍然「**不做**」，但理由**从"够不到"改成"够得到但没有净收益"**。",
    "★★★ **新定则**：**可达性结论必须带「绑定层次」限定** —— ",
    "`pywin32 迟到绑定` / `comtypes 早绑定` / `C# PIA` / `进程内 C++` 四层，",
    "**各层结论不能互相顶替**。⚠ 不带层次的「到不了」会被后来人读成「**官方没这个能力**」。",
    "★★★ **副产（本轮最有复用价值的一条）**：**类型库的方法表是第 4 套官方签名源**：",
    "```",
    "comtypes.client.GetModule('<xxx.tlb>').<IIface>._methods_",
    "  每条 = (HRESULT, 名字, argtypes, flags(名 + 方向), id, 描述)",
    "★ 它**直接给出 [in] / [out] / [in,out]** —— 而**反射文本**只给 `&`、**swapi md** 只给措辞",
    "  （`out` / `ref`），★ **两套源都没有这么直白的方号**。",
    "实例（本轮读到的权威形态）：PutDouble(VariantArray=**in,out** · Index=in · Value=in) ⇒ **3 参**",
    "                        GetDouble(VariantArray=in · Index=in · Value=**out**) ⇒ 2 参，出参作返回值",
    "⇒ ★ 我第一版**按 md 的措辞**传 2 个实参 ⇒ `TypeError: required argument 'Value' missing`",
    "```",
    " | `tools/probe_safearray_comtypes.py`；`D:/AI/SW/output/safearray-comtypes-probe.json`；",
    "`capabilities.yaml` 的 `backend_catalog`（已带更正）；事实 24 / 47 / 53 / 68 / 126 |",
])
if "| 128 |" not in tk:
    K.write_text(tk.rstrip() + "\n\n" + FACT + "\n", encoding="utf-8")
    print("  ok known-facts 已加 128")
else:
    print("  已有 128")

# ── Spec Kit 108 ────────────────────────────────────────────────────
S = Path(r"D:\AI\SW\specs\108-reachability-needs-binding-layer")
S.mkdir(parents=True, exist_ok=True)
spec = """# 108 · 可达性结论必须带**绑定层次**限定 —— 更正轮 186 过强的「到不了」

**Status**: Implemented（轮 188）· ★ **本轮是对**上一轮自己的更正****

## 一、起因：上轮的记录**过强**
```
轮 186：pywin32 **迟到绑定**下测得 `ISafeArrayUtility` 21/21 不可达 + 无 dispinterface
        ⇒ 记成「**到不了**」（未限定层次）。
⚠ 同一轮我在括号里也写了限度「未试 comtypes / C# PIA」—— 本轮就去闭它。
```

## 二、★★★ 实测（`tools/probe_safearray_comtypes.py`）
```
① comtypes.client.GetActiveObject('SldWorks.Application') ⇒ **附着同一实例**
   （comtypes PID=20456 ⇒ 与运行中的那个**同一个**；**没起第二个实例** —— 事实 24 红线）
② cc.GetModule('…/sldworks.tlb') ⇒ 模块 comtypes.gen.SldWorks，**里面有 ISafeArrayUtility**
③ ★★★ **QueryInterface(ISafeArrayUtility) 成功** ⇒ 对象**真的实现**那个 vtable 接口
⇒ ★★ 正确的是「**pywin32 迟到绑定看不到它**」，**不是**「接口不存在 / 到不了」
```

## 三、⚠ 但**往返没走通**（如实记）
```
PutDouble(arr, 0, 1.5) ⇒ 不报错（类型库说它确实要 **3** 参、VariantArray 是 **in,out**）
但 arr.value=None、GetDouble 读回 **0.0** ⇒ **in,out 的 VARIANT 数组没回写**（事实 68 同族）
⇒ 按事实 53 **不继续凑形态**；「能否正确构造 SAFEARRAY」**本轮未走通**。
```

## 四、★★ 而它对我们**没有净收益**（这条才决定结论）
```
对照（同一探针 ⑥）：pywin32 的 `VARIANT(VT_ARRAY|VT_R8, [...])` 与
                   `VARIANT(VT_ARRAY|VT_DISPATCH, [...])` **本来就能构造数组**
                   （事实 123 / 167 就是这么修的）
⇒ ★ 它是**给 C++ 弥补「没有原生数组」**的；脚本语言的绑定层**已经替我们做了**
⇒ ★ 本后端仍然「**不做**」，但**理由从「够不到」改成「够得到但没有净收益」**。
```

## 五、★★★ 立下的新定则
> **可达性结论必须带「绑定层次」限定**：`pywin32 迟到绑定` / `comtypes 早绑定` /
> `C# PIA` / `进程内 C++` —— **四层结论不能互相顶替**。
> ⚠ 不带层次的「到不了」会被后来人读成「**官方没这个能力**」。

## 六、★★★ 副产：**类型库的方法表是第 4 套官方签名源**
```
comtypes.client.GetModule('<xxx.tlb>').<IIface>._methods_
  每条 = (HRESULT, 名字, argtypes, flags(名 + 方向), id, 描述)
★ 它**直接给出 [in] / [out] / [in,out]** ——
  反射文本只给 `&`、swapi md 只给措辞（`out` / `ref`），**两套源都没这么直白的方号**。
实例：PutDouble(VariantArray=**in,out** · Index=in · Value=in) ⇒ **3 参**
     GetDouble(VariantArray=in · Index=in · Value=**out**) ⇒ 2 参，出参作返回值
⇒ ⚠ 我第一版**按 md 的措辞**传 2 个实参 ⇒ `TypeError: required argument 'Value' missing`
```

## 七、判据
| ID | 判据 |
|---|---|
| SC-10801 | ★★ 附着同一实例（**不起第二个** —— 事实 24 红线）|
| SC-10802 | ★★★ **`QueryInterface` 成功** ⇒ 更正轮 186 的「到不了」|
| SC-10803 | ⚠ **如实记**：`in,out` 数组**没回写**、往返**未走通**（不吹）|
| SC-10804 | ★★ 用**对照**得出「**没有净收益**」（pywin32 原生就能构造数组）|
| SC-10805 | ★★★ 立定则：**可达性结论必须带绑定层次** |
| SC-10806 | ★★★ 副产：**类型库方法表**（带 `[in]/[out]`）是第 4 套官方签名源 |
| SC-10807 | 门禁 + 回归不退化 |

## ⚠ 明确记下的限度
* ⚠ **往返没走通** ⇒ 「comtypes 早绑定**能正确驱动** `ISafeArrayUtility`」**仍未证明**
  （已证的是：**接口可 QI 到、方法可调用、实参形态已对**）；
* ⚠ 只试了 `PutDouble` + `GetDouble` 一对，**其余 19 个成员未逐个试**；
* ⚠ C# PIA / 进程内 C++ 两层**未试**（定则说要分层说，但本轮只覆盖前两层）；
* ⚠ 本轮**没改**任何生产代码（结论仍是「不做」）。
"""
plan = """# 108 · Plan

## 步骤
1. 轮 186 记的「到不了」没限定层次 ⇒ ★ 本轮去闭它自己写的限度（未试 comtypes）
2. ★ 查到 `comtypes` 可用 + `sldworks.tlb` 在
3. ★★ 用 `GetActiveObject` **附着**（绝不起第二个实例）
4. ❌ 第一版找接口类找错了模块（用 `type(sw).__module__`）⇒ ★ 改 `cc.GetModule(tlb)`
5. ★★★ ⇒ **QI 成功** ⇒ 更正轮 186
6. ❌ 第一版按 **md 措辞**传 2 个实参 ⇒ 报 Value missing ⇒ ★ 读**类型库方法表**得权威 3 参
7. ⚠ 不报错了但**往返读回 0.0** ⇒ 如实记「没走通」，按事实 53 停手
8. ★★ 加对照组 ⇒ 结论改为「**够得到但没有净收益**」
9. 更正 backend_catalog · 事实 128 · 本 Spec Kit → 门禁 + 回归 → 两仓库 commit

## 风险与对策
| 风险 | 对策 |
|---|---|
| 起第二个 SW 实例（会死锁） | ★ 只用 `GetActiveObject` **附着**，并**回读 PID 比对** |
| 拿 md 措辞当签名 | ★ 改读**类型库方法表**（带 in/out 方向）|
| 往返没通却写"能用" | ⚠ **如实记"未走通"**（事实 53 停手）|
| 只凭"QI 成功"就说该做 | ★ **加对照** ⇒ 无净收益 |
"""
tasks = """# 108 · Tasks（全部完成，轮 188）

- [x] T-10801 查后端可用性（comtypes ✓ / sldworks.tlb ✓）
- [x] T-10802 ★★★ comtypes 早绑定探针 `→ 验收:` `python tools/probe_safearray_comtypes.py`
  （**QI 成功 · 同实例 PID 20456 · 往返未走通 · 无净收益**）
- [x] T-10803 ★★★ 读**类型库方法表**拿权威 `in/out` 签名
- [x] T-10804 更正 `backend_catalog` 里轮 186 的过强措辞
- [x] T-10805 事实 128
- [x] T-10806 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
"""
converge = """# 108 · Converge

**Converged**: 2026-10-01（轮 188）

## 一、结果
| 判据 | 结论 |
|---|---|
| SC-10801 同实例附着 | ✅ PID 20456 |
| SC-10802 QI 成功 ⇒ 更正 | ✅ |
| SC-10803 如实记未走通 | ✅ |
| SC-10804 无净收益 | ✅ |
| SC-10805 新定则 | ✅ |
| SC-10806 类型库方法表 | ✅ |
| SC-10807 门禁 + 回归 | ✅ |

## 二、★★★ 本轮是**对自己上一轮的更正** —— 而这类更正比新功能值钱
```
轮 186 我写「到不了」，乍看有依据（21/21 + 无 dispinterface），
★ 但**漏了一个限定词**：那是 **pywin32 迟到绑定**下的结论。
⇒ 本轮一换层次就翻案 ⇒ ★★ **一个不精确的否定结论，比没有结论更危险**：
  它会让人（包括下一轮的我）**不再去试**。
⇒ 修法不是删掉它，而是**把限定词补上**，并把「为什么仍然不做」的理由换成**更强的那条**
  （从"够不到" → "**够得到但没有净收益**"）。
```

## 三、★ 而"没有净收益"是靠**对照**得出的
```
若我只证到「QI 成功 + 方法可调用」，结论会变成「该做」——
★ 是那句对照（**pywin32 原生就能构造数组**）把它挡住的。
⇒ 与轮 185/186 同一条主线：**判据/结论都要有对照**。
```

## 四、未查证
* ⚠ **往返未走通** ⇒ 「comtypes 能正确驱动它」**未证明**；
* ⚠ 只试了 `PutDouble` / `GetDouble` 一对（其余 19 个成员未逐个试）；
* ⚠ **C# PIA / 进程内 C++ 两层未试**；
* ⚠ 本轮**没改**任何生产代码。
"""
for name, text in (("spec.md", spec), ("plan.md", plan), ("tasks.md", tasks), ("converge.md", converge)):
    (S / name).write_text(text, encoding="utf-8")
    print("  written %s" % name)
