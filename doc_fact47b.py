"""把 `_t011_section28.md` 追加进 T-011 文档；并把事实 47 插进 AGENTS.md。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（文档更新）
# 文件:   D:\\AI\\SW\\_t011_section28.md（内容，单独写成 .md 避免转义问题）
#         D:\\AI\\SW\\probe_setfixedface_forms.py / probe_setfixedface_overloads.py /
#         probe_access_selections.py（证据）
# 定位:   已知事实 47：`ISketchedBendFeatureData` 的 `AccessSelections` / `SetFixedFace`
#         在 pywin32 迟到绑定下不可调用（20+ 种形态穷尽）。
#  ⚠ **本次刻意不把长文本内联进 Python 字符串** —— 本会话已在「多行/长字符串」上踩 6 次
#    （文档串嵌引号、补丁脚本插真换行、`%` 格式串、转义等）。
#    **⇒ 长内容一律走**独立文件 + 最短的读写脚本**。**
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 一次性脚本：跑完即可删。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
WS = Path(r"D:\AI\SW")

SECTION = WS / "_t011_section28.md"
DOC = WS / "docs" / "T-011-expose-capabilities-assessment.md"
AGENTS = WS / "AGENTS.md"

# 事实 47 用**行列表**拼，每行都是独立终止的字符串 —— 不在 Python 里跨行续字符串
FACT47_LINES = [
    "| 47 | **`ISketchedBendFeatureData` 的 `AccessSelections` / `SetFixedFace` 在 pywin32 "
    "迟到绑定下**不可调用** —— 这是**架构性限制**，不是参数没找对**（2026-10-01，"
    "**两轮 20+ 种形态**实测）：`SetFixedFace(X,Y,Z,EdgeArray)` 的**七种数组包装 × 两个重载**"
    "全部报 `类型不匹配`（位置 1 或 4）；`AccessSelections(model, None)` 报 `类型不匹配`（位置 2）、"
    "改传 `VARIANT(VT_DISPATCH, None)` 则报 **`服务器出现意外情况`（`0x80010105`）**"
    "——**与已知事实 28 的 `CreateBsplineSurface` 同一个错误码**。"
    "**⇒ 这与 `capabilities.yaml` 里**早已记录**的后端限制吻合**："
    "「**不能调用官方标记为仅进程内非托管 C++ 的指针接口**」；反射里那对 "
    "**`IAccessSelections` / `IAccessSelections2`** 正是那种 `I` 前缀的**指针变体**。"
    "**⇒ 结论：`create_one_bend` / `create_edge_flange` / `create_gusset` 三条在 pywin32 "
    "这条后端上到不了「建成」**（除非换 `comtypes` 或进程内 C++ 后端）。"
    "⚠ **不要再用「换个参数试试」的方式继续试** —— 20+ 种已穷尽 | "
    "`D:\\AI\\SW\\probe_setfixedface_forms.py` / `probe_setfixedface_overloads.py` / "
    "`probe_access_selections.py`；`capabilities.yaml` 的 `backend_catalog` 限制段 |",
]


def main() -> int:
    # ① T-011（内容来自独立 .md 文件）
    if SECTION.is_file():
        with DOC.open("a", encoding="utf-8") as fh:
            fh.write(SECTION.read_text(encoding="utf-8"))
        print("  ✓ T-011 文档已追加「二十八」（内容取自 _t011_section28.md）")
    else:
        print("  ✗ 找不到 %s" % SECTION)
        return 1

    # ② AGENTS.md 事实 47
    t = AGENTS.read_text(encoding="utf-8")
    i = t.find("| 46 |")
    if i < 0:
        print("  ✗ AGENTS.md 里找不到 | 46 |")
        return 1
    if "| 47 |" in t:
        print("  ⚠ 事实 47 已存在，跳过")
        return 0
    e = t.find("\n", i) + 1
    AGENTS.write_text(t[:e] + FACT47_LINES[0] + "\n" + t[e:], encoding="utf-8")
    print("  ✓ AGENTS.md 已加已知事实 47")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
