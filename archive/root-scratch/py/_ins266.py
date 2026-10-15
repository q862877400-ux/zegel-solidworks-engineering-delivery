import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW\docs\ROADMAP.md")
B = """           266 🎯 **Spec Kit `038`：真缺档再补一条 —— 形位公差（**但换了入口**）**（轮 119）——
               ★★ **关键查证：官方推荐的那条路在新版上无效**：
               ```
               IModelDoc2.InsertGtol()          ⇒ 0 参，返回空 GTol                    ✓ 可用
               IGtol.SetFrameSymbols2(…9 参)    ⇒ ⚠ Remarks **原文**：
                 「valid only if this Gtol was created in a version of SOLIDWORKS
                   **earlier than 2022**」⇒ 本机是 **SW 2026** ⇒ **不可用**
                 ⚠ 且它的符号参数是 **字形串**（官方文档里显示为空）⇒ **文本协议传不了**
               ```
            267 ★★ **最要紧的一步是「查到旧路无效之后，**再查一层**」**：
               ```
               第一层：SetFrameSymbols2 不通 ⇒ **最容易的收场是记「不做 + 原因」**（A1 允许）
               第二层：**再查一层** ⇒ 2022 格式有两条路：
                       · SetSymbolXml（XML，有独立 Schema 文档）
                       · **AddIndicator（收枚举 + 字符串）** ← ★ 采用
               ```
               ★ **「官方推荐的那条路不通」≠「这件事做不了」**；
                 但**也不能反过来假设总有路** —— 再查一层仍不通，正确收场就是**记为不做 + 原因**。
            268 ★ **两条枚举逐值核对**（出厂反射）：`swGtolIndicatorBorderType_e` = 0..3 ·
               `swGtolGeomCharSymbol_e` = **19 项 / 12..30**。`GetFrame` 的 `FrameIndex` **1 基**。
               能力 **36 条**（新增 1：`geometric_tolerance`）· 回归 **1101 passed**。
            269 ★ **本轮测试自己踩了两次（都当场修，且都是判据糙、不是代码坏）**：
               ```
               ① 取"实现段"用 split("# ── 来源")[0] ⇒ 切在 **docstring 里那一段**上
                  （该标记在文件里出现两次）⇒ 取到的"实现"其实是文件头 ⇒ 改正为 rsplit
               ② 断言"实现里不许出现 SetFrameSymbols2" ⇒ **被自己的说明文字误伤**
                  （文档串里**必须**提到它才能解释为什么不走它）⇒ 改成查**调用形态**
               ```
               ★ **如果不修就去"改代码迎合判据"，那才是真的坏。**
            270 ⚑ **未查证**：本机**从未建过**形位公差（等级 `stitched`）；
               `AddIndicator` 的失败原因是**推断**的（官方只说 True/False）；
               `SetSymbolXml` 的 **XML Schema 未读**；`SetIndicator`/`AddFrame`/`DeleteFrame`/取回族**未实现**。
               「真缺」档补录进度：`023`/`024`/`028`/`034`/`038` ⇒ 共 **5 条**，该档约 **132 条**。
               下轮候选：① 继续补「真缺」；② 给剩下 6 条 `stitched` 做真机冒烟；③ A5 的 2 条存疑。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None, "找不到『阻塞:』锚点"
before = "".join(lines)
if re.search(r"^\s+266 ", before, re.M):
    print("  游标 266 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+270 ", R.read_text(encoding="utf-8"), re.M), "复核失败"
    print("  复核: 270 行已存在 ✓")
