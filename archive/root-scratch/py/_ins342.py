import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW\docs\ROADMAP.md")
B = """           342 🎯 **Spec Kit `053`：找出并接上一个****死守卫**** —— 规则 2 的长度那一半从未生效**（轮 134）——
               顺着 `052` 的线去看**工具层**那条守卫：
               ```
               mcp-server/tool_registry.py
                 L78:  _LEN_SUFFIX = "_mm"              ← 定义了
                 L251: if p.name in _BARE_COORD_NAMES:  ← 只有**裸坐标**那条在用
               ⇒ _LEN_SUFFIX **只在定义处出现一次** —— **死常量**
               ```
               ★★ 这正是**事实 40**：「一个**存在但没人用**的守卫与没有守卫等价，**且更糟**」。
               ⚠ 而更糟的是：规则 2 **一直被算进「五统一门禁通过」**（A3 的判据之一）。
            343 ★★ **先证明它死**（事实 62：负例是唯一的证明）：
               造一个故意违规的 `ToolSpec`（`thickness`、不以 `_mm` 结尾）
               ⇒ ✗ **不被拒**（断言"不生效"）· ✗ `_LEN_SUFFIX` 只在定义处 1 次 ·
                 ✓ **对照：同一段的裸坐标规则（规则 3）是活的**
                 ⇒ 不是"整段没实现"，而是**恰好少了长度那一半**。
            344 ★ **接上它**：`_LEN_WORDS`（**刻意不含** `size`/`w`/`h` —— 见事实 74）·
               ★ `bool` **不算长度**（`use_default_radius`/`reverse_thickness` 是**标志**）——
               那正是 `052` 那 4 个假阳性里的 2 个。
               ★ 3 个**真例外**（`sw_mold` 的 `thickness`/`offset`/`distance`，文档写明
                 「0.0 = 用文档默认」）走**显式豁免 + 每条理由**（照 `MANUAL_MAP` 先例），**不改成绿的**。
            345 ★★ **判据有效的证明：同一个负例，换个方向**：
               ```
               接上之前：assert not rejected            ⇒ 3 passed（证明"不生效"）
               接上之后：with pytest.raises(GateError)  ⇒ 5 passed（证明"生效"）
               ```
               ★★ **"把断言翻过来"这个动作本身就是判据被接上的证据** ——
                 而那个方向**是写那条测试时就预留好的**（docstring 里写着"一旦接上就该改成必须被拒"）。
               ★ 可复用做法：**要"先记现状、以后再修"时，把测试的"未来方向"写进它的 docstring** ——
                 那时改起来是**照做**，不是**重新想**。
            346 ★ **这次修的不是"一个 bug"**：接上后 `check_specs(all_specs())` = **0 问题**
               ⇒ **没有"正在违规"的工具** —— 修的是「**以后再犯会被拦**」。
               ★★ **与 `029`/`032`/`037`/`052` 方向相反，合起来才完整**：
                 ```
                 那几轮：**否决**一个判据（假阳性太高 / 原理不成立）
                 本轮  ：**救活**一个判据（它一直是死的）
                 ⇒ ★ 判据要么被负例证明有效，要么被证明不成立 ——
                   **不允许"存在但没人用"。**
                 ```
               ★ 另一处呼应：`052` 那份"**全是假阳性**"的清单**在本轮直接派上用场**
                 （`bool` 标志那 2 个）⇒ **一次否决并不浪费。**
               ⚑ **未查证**：词表是**有界选的**（`size`/`w`/`h` 故意不收）；3 个豁免是**人工判**的；
                 ⚠ **本轮没有去查其它规则是否也有"死守卫"** —— 那是另一轮的事。
               已知事实 **75** 入库 · 回归 **1171 passed**。
               下轮候选：① **系统扫一遍其余 5 条规则有没有"死守卫"**（本轮的方法可直接复用）；
               ② 继续补「真缺」；③ 给剩下 3 条 `stitched` 冒烟。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None, "找不到『阻塞:』锚点"
before = "".join(lines)
if re.search(r"^\s+342 ", before, re.M):
    print("  游标 342 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+346 ", R.read_text(encoding="utf-8"), re.M), "复核失败"
    print("  复核: 346 行已存在 ✓")
