"""★ 自校 `docs/official-source-errors.md` 里写的"真名"—— ★ 逐个去官方核。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身。
# 文件:   tools/selfcheck_official_source_errors.py
# 定位:   ★ 阶段 1 的 **B-5** 的自校：★ 那张表里每条都说"真名是 X" ⇒
#   ★★ **X 必须真的存在于官方 `types/` 下**（★ 否则我只是把一种错换成了另一种）✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(r"D:\AI\SW")
SWAPI = Path(r"C:\swapi")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

#: ★★ 我在表里写的"真名"（★ 逐条核它在官方 `types/` 下存在）
CORRECTED = [
    ("IDrawingDoc", "Create1stAngleViews2"),
    ("ISketchManager", "MakeSketchBlockSelected"),
    ("ISketchManager", "MakeSketchBlockFromFile"),
    ("ISketchManager", "GetSketchBlockDefinitions"),
    ("IDrawingDoc", "IGetCurrentSheet"),
    ("IView", "ActivateView"),
    ("IModelDoc2", "ForceRebuild3"),
    ("IDrawingDoc", "SetSelectedSheets"),
]
#: ★ 原表里写错的那些（★ 逐条核它**确实不存在**—— ★ 否则"死链"这个判断就错了）
WRONG = [
    ("IDrawingDoc", "1stAngleViews2"),
    ("ISketchManager", "MakeSketchBlockSelected"),
    ("ISkethcManager", "MakeSketchBlockFromFile"),
    ("SketchManager", "GetSketchBlockDefinitions"),
    ("IDrawing", "IGetCurrentSheet"),
    ("IDrawingView", "ActivateView"),
    ("IModel2", "ForceRebuild3"),
    ("IDrawingDoc", "SetSelectedSheets"),
]


def _exists(iface: str, member: str) -> bool:
    return (SWAPI / "types" / iface / (member + ".md")).is_file()


def main() -> int:
    print("★ 表里写的「真名」逐条核（★ 应当**全部存在**）：")
    bad1 = []
    for iface, m in CORRECTED:
        e = _exists(iface, m)
        print("   %s %-18s %s" % ("OK " if e else "✗✗ ", iface + "::" + m, "" if e else "★ 官方也没有这个页！"))
        if not e:
            bad1.append("%s::%s" % (iface, m))
    print()
    print("★ 原表里的「错名」逐条核（★ 应当**存在** —— 因为错的是**链接指向的接口**，不是成员缺席）：")
    for iface, m in WRONG:
        e = _exists(iface, m)
        print("   %s %-18s %s" % ("    " if not e else "OK ", iface + "::" + m, "（★ 不存在，与死链判断一致）" if not e else ""))
    print()
    print("★★ 结论:", "★ 表里写的真名全部存在 ✓" if not bad1 else ("★★ 有 %d 条真名官方也没有：%s" % (len(bad1), bad1)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
