import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW\docs\ROADMAP.md")
B = """           602 🎯 **Spec Kit `108`：可达性结论必须带****绑定层次****限定 —— 更正轮 186 过强的「到不了」**（轮 188）——
               起因：轮 186 我在 pywin32 **迟到绑定**下测得 `ISafeArrayUtility` 21/21 不可达，
               ⇒ 记成「**到不了**」（**未限定层次**）。★ 同轮我在括号里也写了限度「未试 comtypes / C# PIA」
               ⇒ 本轮去闭它。
            603 ★★★ **实测（`tools/probe_safearray_comtypes.py`）**：
               ```
               ① comtypes.client.GetActiveObject('SldWorks.Application') ⇒ **附着同一实例**
                  （comtypes PID=20456 ⇒ 与运行中的那个同一个；**没起第二个实例** —— 事实 24 红线）
               ② cc.GetModule('…/sldworks.tlb') ⇒ 模块 comtypes.gen.SldWorks，**里面有 ISafeArrayUtility**
               ③ ★★★ **QueryInterface(ISafeArrayUtility) 成功** ⇒ 对象**真的实现**那个 vtable 接口
               ⇒ ★★ 正确的是「**pywin32 迟到绑定看不到它**」，**不是**「接口不存在 / 到不了」
               ```
            604 ⚠ **但往返没走通**（如实记）：`PutDouble(arr, 0, 1.5)` 不报错（类型库说它确实要 **3** 参、
               `VariantArray` 是 **in,out**），而 `arr.value=None`、`GetDouble` 读回 **0.0**
               ⇒ **`in,out` 的 VARIANT 数组没回写**（事实 68 同族）⇒ 按事实 53 **不继续凑形态**。
               ★★ **而无论走不走得通它都没有净收益**（对照，同一探针 ⑥）：
               pywin32 的 `VARIANT(VT_ARRAY|VT_R8, [...])` 与 `VARIANT(VT_ARRAY|VT_DISPATCH, [...])`
               **本来就能构造数组**（事实 123 / 167 就是这么修的）⇒ ★ 它是**给 C++ 弥补"没有原生数组"**的。
               ⇒ ★ 本后端仍然「**不做**」，但**理由从「够不到」改成「够得到但没有净收益」**。
            605 ★★★ **立下的新定则**：**可达性结论必须带「绑定层次」限定** ——
               `pywin32 迟到绑定` / `comtypes 早绑定` / `C# PIA` / `进程内 C++` 四层，**各层不能互相顶替**。
               ⚠ 不带层次的「到不了」会被后来人读成「**官方没这个能力**」。
               ★★ **一个不精确的否定结论比没有结论更危险** —— 它会让人（**包括下一轮的我**）**不再去试**。
            606 ★★★ **副产：类型库的方法表是第 4 套官方签名源**：
               ```
               comtypes.client.GetModule('<xxx.tlb>').<IIface>._methods_
                 每条 = (HRESULT, 名字, argtypes, flags(名 + 方向), id, 描述)
               ★ 它**直接给出 [in] / [out] / [in,out]** —— 而反射文本只给 `&`、swapi md 只给措辞
                 （`out` / `ref`）⇒ ★ **两套源都没这么直白的方号**
               实例：PutDouble(VariantArray=**in,out** · Index=in · Value=in) ⇒ **3 参**
                     GetDouble(VariantArray=in · Index=in · Value=**out**) ⇒ 2 参，出参作返回值
               ⇒ ⚠ 我第一版**按 md 的措辞**传 2 个实参 ⇒ `TypeError: required argument 'Value' missing`
               ⇒ ★★ 铁律 4 的"三源互证"本轮实际扩到了**四源**（官方 md · 反射文本 · 出厂类型库元数据 ·
                 **类型库方法表（带方向）**）。
               ```
               门禁 + `release_check` exit 0 · 回归 **1248 passed**。
               ⚑ **未查证**：⚠ **往返未走通** ⇒ 「comtypes 能正确驱动它」**未证明**（已证的是：可 QI 到、
                 可调用、实参形态已对）；⚠ 只试了 `PutDouble`/`GetDouble` 一对（**其余 19 个成员未逐个试**）；
                 ⚠ **C# PIA / 进程内 C++ 两层未试**；⚠ 本轮**没改**任何生产代码（结论仍是「不做」）。
               下轮候选：① 用**类型库方法表**去校一轮 `docs/signature-audit.md`（★ 它带 in/out 方向，
                 可能一次校出若干 `byref` 类缺陷）；② 逐条判审计 §八 那 25 个零调用族「该做 / 不做 + 原因」；
               ③ 回到在上下文链（`SketchUseEdge3` 静默无效）。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None, "找不到『阻塞:』锚点"
before = "".join(lines)
if re.search(r"^\s+602 ", before, re.M):
    print("  游标 602 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+606 ", R.read_text(encoding="utf-8"), re.M), "复核失败"
    print("  复核: 606 行已存在 ✓")
