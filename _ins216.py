import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW\docs\ROADMAP.md")
B = """           216 🎯 **Spec Kit `028`：真缺档再补一条 —— 方程式**（轮 109）——
               两源取签名（`GetEquationMgr` / `Add2` / `GetCount` / `Delete` / `EvaluateAll`）
               ⇒ **5 条逐条一致**。能力条目 33 → **34**（`equations`，`stitched`）。
               ★ 两处要留神：① `Add` **已废弃** ⇒ 走 **`Add2`**；
               ② ⚠⚠ **`-1` 有两种语义**（入参 = 追加到末尾 · **返回 = 失败**）——
                 不区分的话，**失败会被当成"插到了末尾"**，而且**不会当场炸**，
                 只是**方程式悄悄没加进去**。⇒ 已单独一条测试钉住。
            217 ★★ **三批「真缺」补录的共同形状**（`023`/`024`/`028`）：
               | 轮 | 补的 | 最要留神的地方 |
               |---|---|---|
               | 023 | 螺旋线 | **枚举值凭记忆写反**（被查证拦下）|
               | 024 | 草图倒角/镜像 | **两源枚举冲突**（铁律 4 裁决）+ **走非废弃入口** |
               | 028 | 方程式 | **`-1` 的双重语义** + **走非废弃入口** |
               ★ 三条里**两条**都撞上「**官方的旧入口已废弃、必须走后继**」
                 （`SketchChamfer`→`CreateChamfer` · `Add`→`Add2`）。
               ⇒ **这是这个域的规律性坑：照抄第一个看到的方法名，可能抄到废弃的那个。**
            218 ⚠ **一个新的覆盖缺口（值得下轮做）**：`025` 的门禁只管**值**，
               **管不了「你用的是不是废弃入口」** —— 三批里撞上两次，**却没有机器判据**。
            219 ⚑ **未查证**：本机从未读写过方程式（`stitched`）；
               **不做方程式字符串格式校验**（官方没给可校验语法）；
               装配体零部件的「上下文中编辑」情形未处理；
               `IEquationMgr` 的 **11 属性 + 14 方法未逐一实现**。回归 **1084 passed**。
            220 ⚑ 下轮候选：① ★ **给「废弃入口」加一道门禁**（官方 md 里带
               `Obsolete`/`Superseded` 的成员，我们代码里不该直接调）；
               ② 继续补「真缺」；③ A5 的 2 条存疑。
"""
text = R.read_text(encoding="utf-8")
if re.search(r"^\s+216 ", text, re.M):
    print("  游标 216 已在")
else:
    lines = text.splitlines(keepends=True)
    i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
    assert i is not None, "找不到『阻塞:』锚点"
    before = "".join(lines)
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+220 ", R.read_text(encoding="utf-8"), re.M), "复核失败：找不到 220"
    print("  复核: 220 行已存在 ✓")
