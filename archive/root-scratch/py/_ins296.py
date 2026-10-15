import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW\docs\ROADMAP.md")
B = """           296 🎯 **Spec Kit `044`：把剩下 3 个孤儿也接上 —— 顺带查出一条****官方没写**的行为约束****（轮 125）——
               链路：**标准（15）→ 紧固件类型（14）→ 表类型（`[0,1,2]`）**。
            297 ★★ **查出的约束：`IHoleStandardsData` 必须先「热身」** ——
               ```
               第一版拿到 data 后**直接**调 GetFastenerTypes ⇒ 返回 False
               （而同一探针早先明明拿到过 True ⇒ 说明有隐藏状态）
               ⇒ **不猜，量四组对照**：
                 A 直接调                                  ⇒ False
                 B **先调 GetHoleStandards** 再调           ⇒ **True** ✓
                 C 未热身对象上**再调一次**                 ⇒ 仍 False（⇒ 不是"调一次就好"）
                 D 换标准名 'ISO'                          ⇒ 仍 False（⇒ 不是名字问题）
               ```
               ⇒ 官方文档**只写各方法自己的前置**，**没有**这条跨方法顺序约束。
                 已在 `_hole_standards_data()` 里默认热身（`initialize=False` 可跳过）。
            298 ★★★ **「反向验证」—— 本项目第一次**：
               ```
               以往证据都是「做了 X 之后 Y 成立」
               本轮的是「**不做 X 就不成立**」（不热身 ⇒ GetFastenerTypes 返回 False）
               ⇒ ★ 这才证明 X **必要**，而不只是"无害"
               ```
               ★ 与事实 62（「门禁『写了』≠『有效』，负例是唯一的证明」）**同一思路**，
                 只是对象从**门禁**换成了**运行期约束**。真机冒烟 **11/11**。
            299 ❌ **`get_fastener_table` 到不了** —— 官方第 4 参是 `out IHoleDataTable`，
               用**同族另外三个已验过**的容器形态传，三个 `TableID` 全报
               `com_error -2147352571`「类型不匹配」**位置 4**。
               ★ **同族里只有这一个到不了** ⇒ 按**事实 53** 停手，保留函数作**可复算的证据**。
               ★ **"接上"不等于"都能用"** —— 本轮把「**能用的**」与「**到不了的**」分开报。
            300 ⚠ **同一个来源块问题第三次出现**：`# 覆盖: 后续同级定义` **会被下一个来源块截断** ——
               而新函数被插进了**两段已有来源块之间** ⇒ 改用 `# 覆盖: 全文件`。
               ⚠ 三次了（119 判据被文档串误伤；124/125 覆盖范围）⇒ **该写进纪律**，不是每次当场发现。
               ⚑ **未查证**：只证了 `ANSI Inch` + `hole_type_id=0` 一条组合；**不证 15/14/`[0,1,2]` 是全集**；
                 `id` 语义未核；`get_fastener_table` 换后端未试；**没有**注册成 MCP 工具。
               已知事实 **69** 入库 · 回归 **1124 passed**。
               下轮候选：① 把"来源块覆盖范围"这条写进纪律（**已经三次**）；
               ② 给剩下 3 条 `stitched` 冒烟；③ 把查到的 API 注册成 MCP 工具（要比清 `sw` 从哪来）。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None, "找不到『阻塞:』锚点"
before = "".join(lines)
if re.search(r"^\s+296 ", before, re.M):
    print("  游标 296 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+300 ", R.read_text(encoding="utf-8"), re.M), "复核失败"
    print("  复核: 300 行已存在 ✓")
