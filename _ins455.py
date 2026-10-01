import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW\docs\ROADMAP.md")
B = """           455 🎯 **Spec Kit `077`：`export_to_pdf` ****此前从未能运行过**** —— 查出并修好****两处****缺陷**（轮 158）——
               顺着 `076` 矩阵唯一那个空格（`pdf`）：上轮我**猜**「不是功能不行，是**我用的对象不对**」
               （因为签名里有 `sheet_names`）⇒ ★★ 本轮**做一张工程图**去补那一格。
            456 ★★★ **工程图上**也**同样失败** ⇒ **推翻我上轮那个猜测** ⇒ **读源码（不猜）**：
               ```python
               def export_to_pdf(model, output_path, sheet_names=None):
                   sw = model.GetSldWorksObject()      # ← ★★★ 就是这里
               ```
               ```
               ★ 两套官方源都查不到 GetSldWorksObject（_raw 反射 / C:\\swapi\\types\\）⇒ **均无此名**
               ★ 仓库里**只有这一处**用它 ⇒ **铁律 5**：名字缺席 = 没有这个成员
               ⇒ **export_to_pdf 此前从未能运行过**（4 个调用点全都会炸）
               ```
            457 ★★★ **修第一处 ⇒ 立刻暴露第二处**：
               `TypeError: must be real number, not WindowsPath` ——
               `model.Extension.SaveAs(output_path, …)` 收 `Path` ⇒
               ★ 报错**完全看不出**是路径类型问题（与事实 59 同族：路径类型要在边界上 settle 一次）。
            458 ★★ **修法与真机验证**：
               ```
               修法：(a) 加可选入参 `sw=None`，缺省走 `sw_connect.connect_solidworks()` 取**同一实例**
                       （COM 单实例 ⇒ 符合事实 24 的单源约束）· (b) `str(output_path)`
               ⇒ ★★ 真机（工程图 1 张）：**39830 字节 · 头部 `%PDF-1.4` · 页数 = 1**（数 `/Type /Page`）
               ⇒ ★ 顺带：`dwg` 在**工程图**上也成功 ⇒ **279450 字节 · `AC1015`**（真 DWG）
                  ⇒ 轮 156「只测钣金件」那条限度**补上了**。
               ```
               ★★★ **影响面（用户可见）**：`server.py` 的 `solidworks_export_active` 的 **pdf 格式**、
                 `sw_session.py` 的 `.pdf` 路由 —— **此前都会炸**。
               ★ 为什么没被发现：**没有任何测试/冒烟跑过它** ⇒ 与事实 60（存在但没人用的守卫）**同族**：
                 **存在但没人跑的函数**也一样。
            459 ★★★ **本轮的形状：上一轮的「限度」里藏着这一轮的「真缺陷」** ——
               ```
               076：「pdf 在零件上失败 ⇒ ⚠ 本轮没做工程图 ⇒ 未查明」+ 准确措辞
               077：做工程图 ⇒ 也失败 ⇒ 猜测被推翻 ⇒ 读源码 ⇒ 真缺陷
               ⇒ ★★ **「限度」不是终点，它是一份待办清单**（与 065→066 同一形状）。
               ⇒ ★★ 「**诚实地写限度**」是有**复利**的：上轮那两行直接换来了本轮一个用户可见的修复。
               ```
               ⚑ **未查证**：⚠ 只在**工程图**那条路验过（零件上失败是**应然的**）；
                 ⚠ 只验**文件头与页数**，不证 PDF 内容正确；⚠ `GetSldWorksObject` 是**两套源都没查到**
                 （没有第三套源可交叉）；⚠ `sw` 缺省走 `connect_solidworks()` ⇒ **多连一次的代价未测**。
               已知事实 **98** 入库 · 回归 **1236 passed** · `release_check` exit 0。
               下轮候选：① 把「**存在但没人跑过**」的函数扫一遍（本轮查出 1 个，可能有更多）；
               ② 回到「真缺」继续补；③ 给剩下 3 条 `stitched` 冒烟。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None, "找不到『阻塞:』锚点"
before = "".join(lines)
if re.search(r"^\s+455 ", before, re.M):
    print("  游标 455 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+459 ", R.read_text(encoding="utf-8"), re.M), "复核失败"
    print("  复核: 459 行已存在 ✓")
