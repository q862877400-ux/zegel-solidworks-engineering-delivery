import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_gtol.py")
t = P.read_text(encoding="utf-8")

#: ① `GetFrame` 那条报错已过时（帧现在**拿得到**了）
OLD1 = ('            "IGtol.GetFrame(%d) 返回 None ⇒ 取不到这一帧"\n'
        '            "（官方 `FrameIndex` 是 **1 基**；**已尝试补帧仍取不到** "\n'
        '            "⇒ 该 Gtol 可能不是 2022 格式）" % frame')
NEW1 = ('            "IGtol.GetFrame(%d) 返回 None ⇒ 取不到这一帧"\n'
        '            "（官方 `FrameIndex` 是 **1 基**；**已尝试「先 ConvertFormat 再加帧」仍取不到**）"\n'
        '            "⚠ 轮 165 实测：**顺序对**时 `GetFrameCount()` 能到 **2** 且拿到对象 ⇒ "\n'
        '            "走到这里说明是别的原因（**未查明**）" % frame')
if OLD1 in t:
    t = t.replace(OLD1, NEW1, 1)
    print("  ok ① GetFrame 的报错已更新")

#: ② `AddIndicator` 那条报错里「不是 2022 格式」已不成立（我们**确实**转换过了）
i = t.find('"IGtolFram')
j = t.find(")\n", i)
seg = t[i:j + 1]
print("  ── AddIndicator 那条报错原文 ──")
print(seg)
NEW2 = ('            "IGtolFrame.AddIndicator 返回 False（失败）\\n"\n'
        '            "⚠ 轮 165 实测：**帧已经拿到了**（`GetFrameCount()` = 2、`GetFrame(1)/(2)` 有对象）"\n'
        '            "⇒ 所以**不再是「帧路径取不到」**，而是 **`AddIndicator` 的参数/前置未查明**。\\n"\n'
        '            "官方签名：`Boolean AddIndicator(Int32 BorderType, Int32 ToleranceType, String Datum)`。"\n'
        '            % ()')
if seg and "不是 2022" in seg or "不是 2022" in (seg or ""):
    pass
#: 整段替换（从 "IGtolFram 到该 raise 的参数结束）
k = t.rfind("raise RuntimeError(", 0, i)
m = t.find(")", t.find("% (", i)) if "% (" in t[i:i + 400] else t.find(")\n", i)
t = t[:k] + "raise RuntimeError(\n" + NEW2 + "\n        )" + t[t.find(")\n", i) + 1:]
P.write_text(t, encoding="utf-8")
ast.parse(t)
print("  ok ② AddIndicator 的报错已更新（去掉「不是 2022 格式」这个已不成立的说法）")
