import re
import shutil
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

WS = Path(r"D:\AI\SW\tools")
REPO = Path(r"C:\swprojects\sw-skill-fork")
DEST = REPO / "tools"

SRC_BLOCK = """
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（本工具为原创；{moved} 从工作区仓库搬入本仓库）
# 文件:   tools/{name} —— 本文件自身
# 定位:   {role}
# 官方依据: {basis}
# 许可:   本仓库 MIT
# ⚠ 只做静态读取与生成，不连 SolidWorks。输入源依赖本机布局（`C:\\swapi` / `D:\\AI\\SW\\_raw`），
#   未在第二台机器上实测。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""

META = {
    "gen_api_map.py": dict(
        role="docs/api-map.md 的生成器（官方 API 成员 → 本仓库函数的反向索引）",
        basis="C:\\swapi 的成员目录 + 本仓库源码（静态扫描）",
    ),
    "gen_iview_registry.py": dict(
        role="scripts/sw_drawing_view.py 的机械生成器（从反射清单生成登记表 + 通用访问器）",
        basis="D:\\AI\\SW\\_raw 的 sldworks 反射清单",
    ),
}

moved = []
for name, meta in META.items():
    src = WS / name
    dst = DEST / name
    t = src.read_text(encoding="utf-8")
    if "# ── 来源 ─" not in t:
        #: 插到模块 docstring 里（紧跟在开头 """ 之后那一段之后最简单：插在 docstring 结束前）
        m = re.search(r'(?s)^(.*?""")(.*)$', t)
        block = SRC_BLOCK.format(moved="2026-10-01 轮 219（地基④）", name=name, **meta)
        t = t[:m.end(1)] + block + t[m.end(1):] if m else block + t
    dst.write_text(t, encoding="utf-8")
    shutil.copy2(src, str(dst) + ".orig")          #: 临时留一份对照，随后删
    moved.append(name)
    print("  ✓ 已写入 %s（%d 字节）" % (dst, dst.stat().st_size))

print("")
print("  产物对照（确认与工作区版一致，除了新加的来源块）:")
for name in moved:
    a = (WS / name).read_text(encoding="utf-8")
    b = (DEST / name).read_text(encoding="utf-8")
    print("    %-28s 工作区 %d 字节 · 仓库 %d 字节 · 多出 %d" % (name, len(a), len(b), len(b) - len(a)))
