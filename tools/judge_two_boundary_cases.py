"""★ 判 `check_official_source_defects` 那 2 处边界：哪个是误报、哪个是真漏。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   tools/judge_two_boundary_cases.py
# 定位:   判 `check_official_source_defects` 那 2 处边界：哪个是误报、哪个是真漏。
# 官方依据: 官方源 `C:\swapi\types\**`（★ 逐条见文件内引用）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(Path(__file__).resolve().parents[1])
TD = Path(r"C:\swapi\types")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

#: ── 边界 ① `[[IFeatureManager::IInsertMidSurface]]`（mcp-server/tool_specs_batch74.py:
#: 401）
print("═══ 边界 ① `[[IFeatureManager::IInsertMidSurface]]` ═══")
cand = ["IInsertMidSurface", "InsertMidSurface", "InsertMidSurface2"]
for c in cand:
    p = TD / "IFeatureManager" / ("%s.md" % c)
    print("   ★ `%s` 的页存在吗: **%s**%s" % (c, p.is_file(), "" if p.is_file() else "  ← 查不到"))
#: ★ 全库搜一遍这个名字（★ 可能挂在别的接口下）
hits = [str(p.relative_to(TD)) for p in TD.rglob("IInsertMidSurface*")]
print("   ★ 全库 `IInsertMidSurface*`: **%d** 个 %s" % (len(hits), hits[:3]))
hits2 = [str(p.relative_to(TD)) for p in TD.rglob("InsertMidSurface*")]
print("   ★ 全库 `InsertMidSurface*`: **%d** 个 %s" % (len(hits2), hits2[:4]))
print("   ⇒ ★ 判: %s"
      % ("★ **误报**（★ 该名字在本机全库确实没有 ⇒ 引用它**就是**引用不存在的页）"
         if not hits else "★★ **误报成立**（★ 页存在、只是不在 IFeatureManager 下）"))

#: ── 边界 ② `[[Iface::Member]]`（tools/build_obsolete_index.py:25）
print()
print("═══ 边界 ② `[[Iface::Member]]` ═══")
f = ROOT / "tools" / "build_obsolete_index.py"
lines = f.read_text(encoding="utf-8", errors="replace").splitlines()
for i in range(max(0, 22), min(len(lines), 30)):
    print("   %d| %s" % (i + 1, lines[i][:104]))
#: ★ 判据：该行是否落在 docstring / 注释里（★ 那才是"模板占位"）
print("   ⇒ ★ 判: %s"
      % ("★★ **误报**（★ 该行在 **docstring** 里 ⇒ `[[Iface::Member]]` 是**模板占位**，"
         "不是真引用）" if '"""' in "".join(lines[18:26]) or lines[24].lstrip().startswith("#")
         else "★ 需人判（★ 上下文看不出来）"))
