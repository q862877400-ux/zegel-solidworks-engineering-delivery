import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\docs\acceptance-status.md")
t = P.read_text(encoding="utf-8")
OLD = "| `tools/verify_composite_curve_smoke.py` | 6/7 |"
NEW = "| `tools/verify_composite_curve_smoke.py` | **8/8**（轮 182 起） |"
i = t.find(OLD)
if i > 0:
    j = t.find("\n", i)
    row = ("| `tools/verify_composite_curve_smoke.py` | **8/8** | "
           "⚠ **轮 182 定性更正**：官方样例（VBA/C#/VB.NET 三份一致）要求前置 = "
           "「**两条**样条**草图**」，而 ★ **样条在本机建不出来**（`CreateSpline2` 返回 None，"
           "事实 40 族）⇒ **前置不可达** ⇒ `InsertCompositeCurve` 必然 False。"
           "★ 判据已改成**三档**（可达 ⇒ 要求 True / 不可达 ⇒ **不计入** / 真失败）"
           "⇒ 本条**不再计入红**。⚠ 但卡住的**样条**本身是**未解问题**。 |")
    t = t[:i] + row + t[j:]
    print("  ok 表格行已更新")
else:
    print("  ⚠ 没找到那一行")
MARK = "> ⚠ 本表是 **2026-10-01（轮 180）** 的快照"
i = t.find(MARK)
if i > 0:
    NOTE = ("> ⚠⚠ **轮 182 再更正**：`verify_composite_curve_smoke` 的**真正前置**是"
            "「**两条样条草图**」（官方三份样例一致），而 **样条在本机建不出来** ⇒ **前置不可达**\n"
            "> （**不是**它自己功能不行）。判据已改成三档 ⇒ 本条**不计入红**；"
            "★ 卡住的**样条**（`CreateSpline2` 返回 None）才是**未解问题**。\n")
    if "轮 182" not in t[:i]:
        t = t[:i] + NOTE + t[i:]
        print("  ok 顶部提示已加")
P.write_text(t, encoding="utf-8")
print("  最终 %d 字节" % len(t))
