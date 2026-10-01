import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW\docs\ROADMAP.md")
B = """           594 🎯 **Spec Kit `106`：`ISafeArrayUtility` 是****给 C++ 的****，pywin32 到不了 —— 一条外部「高杠杆」建议被**实测否定****（轮 186）——
               起因：一份外部评审（`D:/AI/SW-transfer/capability-gap-audit.md`）把
               `ISafeArrayUtility`（台账 `used=0`、21 成员）列为本项目**唯一高杠杆**缺口 ——
               「官方给了数组工具集，而我们到处手搓 `VARIANT(...)`」（事实 12 / 33 / 68 / 123 / 167）。
               ★ 但那份评审**没验证可达性**（它自己 §十三 写了「未连 SolidWorks」）。
            595 ★★★ **实测否定**（`tools/probe_safearray_utility.py`：真机 · `CommandInProgress` 置位 · 不开文档 · 收尾轮询点掉）：
               ```
               ① ISldWorks.GetSafeArrayUtility()  ⇒ **返回 CDispatch（对象拿得到）**
               ② 官方登记的全部 **21 个成员**逐个试 ⇒ **可达 0/21**（每个都 AttributeError: <unknown>.X）
               ③ 类型信息内省 ⇒ com_error(-2147352565, '无效索引。') ⇒ **没有可用的 dispinterface**
               ```
               ★★ **官方自己写明了原因**（`ISafeArrayUtility/_overview.md` 的 Remarks）：
               > "replaces the SOLIDWORKS **SafeArray template class** … for methods requiring Variant
               >  arrays in **your C++ projects**."
               ⇒ ★★★ 它是**取代 C++ 的 SafeArray 模板类**的便利件；脚本语言里**本就有原生数组**
                 ⇒ **它不是我们手搓 `VARIANT(...)` 的替身**。★ 与**事实 47** 同一族。
            596 ★★★ **本轮的价值：把一条「看起来该做」的缺口变成了**有证据的「不做」**** ——
               ```
               评审说它高杠杆 ⇒ ★ 若照做，会花很多轮去包一个**根本够不到**的接口
               ⇒ ★ 这是 A1 要求的写法：「每一格都有来源，**或写明不做 + 原因**」——
                 本轮补的是**那一半**：把「没做」变成「**有证据地不做**」。
               ⇒ 已记进 `capabilities.yaml` 的 `backend_catalog.solidworks-com-pywin32.limitations`。
               ```
            597 ⚠⚠⚠ **而 502 个假阳性是本轮最该记住的**：
               ```
               猜想：「`IX` 有成员、其无 I 孪生段存在且为空 ⇒ 只有 vtable ⇒ 迟到绑定到不了」
               实测：1032 个接口段里 **504 对有孪生、502 对的孪生是空的**
               ★★ 而其中包含 ISldWorks / IModelDoc2 / IFeatureManager / ISketchManager /
                  ISelectionMgr / IFace2 —— **这些全都能用** ⇒ 该信号**完全不能预测可达性**
               ⇒ ☆ 若做成门禁，会**同时**给出 **502 个假阳性**
               ```
               ★ **立下的可复用判据**：判「一个官方接口在本后端可达吗」**只能真机逐接口穷尽枚举**
                 （全部成员名 + 类型信息），**没有静态捷径** —— 与事实 47 的结论一致。
               门禁 + `release_check` exit 0 · 回归 **1248 passed**。
               ⚑ **未查证**：⚠ **只判 pywin32 迟到绑定** —— `comtypes` / C# PIA **是否**能驱动那些 `out` 形参**未验**；
                 ⚠ 若有 makepy 早绑定模块，结论**未验**；⚠ `PackVariant` 的 `ref Int32 Data` 形态**没查明**（够不到）；
                 ⚠ 本轮**没改**任何生产代码（结论是「不做」，不是「实现」）。
               下轮候选：① 试 `comtypes` 后端驱动 `out` 形参（若成，则「不做」要改写成「换后端可做」）；
               ② 把审计 §八 那 25 个零调用族逐条判「该做 / 不做 + 原因」（★ 本轮立了判据）；
               ③ 回到在上下文链（`SketchUseEdge3` 静默无效）。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None, "找不到『阻塞:』锚点"
before = "".join(lines)
if re.search(r"^\s+594 ", before, re.M):
    print("  游标 594 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+597 ", R.read_text(encoding="utf-8"), re.M), "复核失败"
    print("  复核: 597 行已存在 ✓")
