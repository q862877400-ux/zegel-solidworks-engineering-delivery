"""摘掉 `sw_selection_spec.py` 的「未实测」标注（它已端到端实测）+ 记录证据。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（一次性补丁，非第三方移植）
# 文件:   D:\\AI\\SW\\patch_selection_verified.py
# 定位:   2026-10-01 用 `D:\\AI\\SW\\probe_selection_spec_e2e.py` 端到端实测
#         `scripts/sw_selection_spec.py`：**12 项通过 / 0 失败**，含
#         `entities_on_body`（12 边 / 6 面）、`index:` 解析、`__current_selection__` 解析、
#         直接传对象、以及 4 个「该报错就报错」的判定。
#         **⇒ 按铁律 2，把「未在本机实测」改成实测结论 + 证据出处。**
# 官方签名依据: 不适用（纯 Python 文本补丁）
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 一次性脚本：跑完即可删。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

SEL = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_selection_spec.py")

OLD_MODULE = """# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ⚠ **未在本机实测本模块整体**（被它包装的 `Select4` 与 `GetSelectedObject6`
#   各自已实测，见上表）；接入前应跑一次端到端。"""
NEW_MODULE = """# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ⚠ **已在本机实测**（2026-10-01，SW 2026 SP4.1，100×60×20 mm 板）：
#   证据脚本 `D:\\AI\\SW\\probe_selection_spec_e2e.py` ⇒ **12 项通过 / 0 失败**：
#     · `entities_on_body` → 12 边 / 6 面（与几何相符）
#     · `index:0` / `index:11` / `index:0`(FACE) 解析 → 计数均为 1
#     · `__current_selection__`：空选区**正确报错**、有选中时**正确取到**
#     · 直接传 COM 对象 → 计数 1
#     · 4 个「该报错就报错」的判定全部正确报错（非法类型 / 越界 / 非法选择器 / 空选区）
#     · **复现了「`SelectByID2` 对边/面的名字选不中」**（两者计数均为 0）"""

OLD_CURRENT = "# 覆盖:   本函数整体（自本行至函数结束）\n# ⚠ **未在本机实测**（`GetSelectedObject6` 本身在本项目其它模块已用，但本包装没跑过）。"
NEW_CURRENT = "# 覆盖:   本函数整体（自本行至函数结束）\n# ⚠ **已在本机实测**（同上证据脚本）：空选区返回空列表、有选中时正确取到。"

OLD_ENTITIES = "# 覆盖:   本函数整体（自本行至函数结束）\n# ⚠ **未在本机实测**（`GetBodies2` / `GetEdges` 本项目已用，本包装没跑过）。"
NEW_ENTITIES = "# 覆盖:   本函数整体（自本行至函数结束）\n# ⚠ **已在本机实测**（同上证据脚本）：12 边 / 6 面，与 100×60×20 mm 板的几何相符。"

OLD_RESOLVE = "# 覆盖:   本函数整体（自本行至函数结束）\n# ⚠ **未在本机实测**"
NEW_RESOLVE = "# 覆盖:   本函数整体（自本行至函数结束）\n# ⚠ **已在本机实测**（同上证据脚本，12/12 通过）"


def main() -> int:
    t = SEL.read_text(encoding="utf-8")
    missed = []
    for old, new in ((OLD_MODULE, NEW_MODULE), (OLD_CURRENT, NEW_CURRENT),
                     (OLD_ENTITIES, NEW_ENTITIES), (OLD_RESOLVE, NEW_RESOLVE)):
        if old not in t:
            missed.append(old.splitlines()[3][:44] if len(old.splitlines()) > 3 else old[:44])
            continue
        t = t.replace(old, new, 1)
    SEL.write_text(t, encoding="utf-8")
    if missed:
        print("  ✗ 未匹配：%r" % missed)
        return 1
    print("  ✓ 四处「未实测」标注已改为实测结论 + 证据出处")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
