import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW\docs\ROADMAP.md")
B = """           236 🎯 **Spec Kit `032`：台账剩下 20 条全部核完**（轮 113）——
               判法是把**官方文档所在接口**与**我方调用点的目标表达式**并排看
               （同一个成员常出现在**多个接口**下，只有**一部分**标废弃 ⇒ **光看名字判不出**）。
               结果：**真 8 · 假阳性 10 · 未定性 1** ⇒ 假阳性率 **50%**（比 `029` 的 26% 更高）。
               ★ **这门禁确实做不得** —— `029` 的判断再次被证实，且**这一轮的判法必须人工**。
            237 ★★ **查出一条「活的」—— 而且是**我们自己造的**债**：
               ```
               轮 98（Spec Kit 018）我把 sw_mold.mold_undercut_detect 暴露成 MCP 工具
                 `solidworks_mold_undercut_detect`
               而它调的 IFeatureManager.MoldUndercutDetect **官方早标了 Obsolete**
                 ⇒ 后继是 MoldUndercutDetect2
               ⇒ **发工具的时候，我没查它包着的入口是否已废弃。**
               ```
               ⚠ 那几轮挑的是"孤立能力"，标准是「**签名兼容**」+「**冒烟不报错**」——
                 **没有一条是「入口没废弃」**；而 `029` 的探针**一跑就抓出来了**。
            238 ⚑ **处置**：在该工具的 `doc` 里**加警示**（诚实、低风险），
               **不擅自改实现** —— 换 `MoldUndercutDetect2` 要先比形状（`030`/`031` 的教训）。
               台账补**总账**：真 8（6 换 · 2 不换 · 1 加警示）· 假阳性 18 · 未定性 1。
            239 ⚠ **未查证**：真候选里 `AutoDimension2` / `ExcludeFromBOM` / `GetDependencies2` /
               `GetErrorCode` / `ReferenceType` / `SystemValue` / `AdvancedGraphics`
               **仍未处置**，且**未查它们的后继形状**；`KFactor` **未定性**；
               台账**仍不做门禁**（假阳性约一半）。回归 **1085 passed**。
            240 ⚑ 下轮候选：① 查那 7 条的**后继形状**再决定换不换（照 `030`/`031` 的做法）；
               ② 继续补「真缺」；③ A5 的 2 条存疑。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None, "找不到『阻塞:』锚点"
before = "".join(lines)
if re.search(r"^\s+236 ", before, re.M):
    print("  游标 236 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+240 ", R.read_text(encoding="utf-8"), re.M), "复核失败"
    print("  复核: 240 行已存在 ✓")
