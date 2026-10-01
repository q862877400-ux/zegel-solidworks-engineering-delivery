"""验证 `Path("D:")` 是不是「带盘符的相对路径」（缺反斜杠）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（诊断）+ Python 标准库 `pathlib` 文档
# 文件:   scripts/cad_installation.py 的 `_common_candidates`（L211-212 / L225）
# 定位:   轮 45 查明 `test_discover_installation_supports_injected_filesystem` 的失败真因。
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 长内容走**短的单行字符串**（事实 48 定则）。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")


def main() -> int:
    bad = Path("D:") / "AutoCAD 2024" / "acad.exe"
    good = Path("D:/") / "AutoCAD 2024" / "acad.exe"
    want = r"d:\autocad 2024\acad.exe"
    print("  Path('D:')                            = %r" % str(Path("D:")))
    print("  Path('D:') / 'AutoCAD 2024' / exe     = %r" % str(bad))
    print("      ^^^ **缺反斜杠 —— 这不是 D 盘的根**")
    print()
    print("  Path('D:/') / 'AutoCAD 2024' / exe    = %r" % str(good))
    print("      ^^^ **正确**")
    print()
    print("  ★ 测试注入的 exists 只认: %r" % want)
    print("    旧写法能匹配? **%s**" % (str(bad).lower() == want))
    print("    新写法能匹配? **%s**" % (str(good).lower() == want))
    print()
    print("  ⇒ 结论：旧写法在 **D:/E: 盘上永远找不到** AutoCAD/SolidWorks ——")
    print("    这是**真实功能 bug**（不只是测试问题），被那个测试尽职抓到。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
