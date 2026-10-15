import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW\docs\ROADMAP.md")
B = """           547 🎯 **Spec Kit `096`：检查器收敛到「33 检查点 / 6 命中 / ****全真****」—— 四次「用猜填不知道」的收窄史**（轮 176）——
               ★ 关键改动：把**辅助函数的调用点常量代进形参** ⇒ 轮 175 那 47 处「查不了」里有一类**能查了**：
               ```
                   def _count(name):  return get_com_member(fm, name)     # 成员名是形参
                   counts = {..., _count("GetPartingLinesCount"), ...}     # 调用点传的是**常量**
               ⇒ ★ 把常量代进去 ⇒ 静态**就能查** ⇒ 检查点 214 → 228
               ```
            548 ★★★ **结果：自动抓出了轮 172 **必须靠真机 + swapi** 才发现的那 6 个成员**，
               且归属**完全一致**（`IPartingLineFeatureData` / `IPartingSurfaceFeatureData` / `IToolingSplitFeatureData`）。
               ⇒ ★★ **两条互相独立的证据链指向同一结论** —— 比任何一条单独都有力。
            549 ⚠⚠⚠ **但同一改动带出 8 处假阳性**（`sw_assembly_doc.py`）：
               ```
               它的 `call_assembly_doc(doc, member, *args)` 里 `doc` **就是** `IAssemblyDoc`
               （docstring 与它自己的报错文本都写着「**IAssemblyDoc** 上没有名为 {member} 的能力」），
               而我的 `ROOTS` 表把 `doc` **猜**成 `IModelDoc2` ⇒ 8 处假阳性
               ```
               ★★ **修法：把「变量名 → 接口」表**缩到只剩 `sw`****（本仓库处处是 `ISldWorks`，
               由 `connect_solidworks` 的返回契约保证）⇒ ★ **宁可少报，不假报**：
               ```
               缩表前：228 检查点 · **33 命中**（含 ~27 假）
               缩表后： 33 检查点 ·  **6 命中**（**全真**）
               ```
            550 ★★★ **四次「用猜填不知道」，四次都靠实测收窄** —— 这是本会话**最一致的一条主线**：
               ```
               113（轮 173）：兜底 **`IObject`**               ⇒ 必然不在谱系 ⇒ 必报
               114（轮 174）：用 **docstring 里的散文接口名**猜 ⇒ 实测两处推错 ⇒ **回退**
               115（轮 175）：`:param` 段里按**长度倒序**配接口名 ⇒ 配到更长的那个 ⇒ 改**位置判据**
               116（轮 176）：用**变量名**（`ROOTS` 表）猜接口       ⇒ 8 处假阳性 ⇒ **缩到只剩 1 个有契约保证的**
               ⇒ ★★ 共同形状：**用「猜」填「不知道」** ⇒ 四次都是**实测**发现的，四次都**收窄**
               ```
            551 ★ 收敛后的边界（可一句话说清）：**33 个检查点 · 6 处命中（全真）· 47 处未检查项**
               （成员名是变量且无常量调用点 ⇒ 留白）。
               门禁 + `release_check` exit 0 · 回归 **1248 passed**。
               ⚑ **未查证**：⚠ **`_count` 那条（`fm` 那一层）未进命中，原因未查明**（`_prop` 那条进了）；
                 ⚠ **缩表也有代价**：检查面 228 → 33（**大量地方现在留白不查**）；
                 ⚠ 那 6 处**未真机复核**（与轮 172 的真机结论一致，但那是**另一条**证据链）；
                 ⚠ 47 处未检查项**仍在**（本轮只解决了「有常量调用点」的那一类）。
               下轮候选：① 查 `_count`（`fm`）为何未命中（可能同族）；② 逐条真机核那 6 处；
               ③ 回到在上下文链（`SketchUseEdge3` 静默无效）。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None, "找不到『阻塞:』锚点"
before = "".join(lines)
if re.search(r"^\s+547 ", before, re.M):
    print("  游标 547 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+551 ", R.read_text(encoding="utf-8"), re.M), "复核失败"
    print("  复核: 551 行已存在 ✓")
