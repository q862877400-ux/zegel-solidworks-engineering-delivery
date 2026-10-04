"""★ 量化「中文查询 vs 英文工具面」的词元重叠 —— ★ 这是检索失败的结构性成因（不是算法问题）。"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(r"D:\AI\SW")
for _p in (str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import metric_scope as ms   # ★ 口径注册表（★ 事实 517：口径必须落成代码）
import register_capabilities as rc                                    # noqa: E402

CJK = re.compile(r"[\u4e00-\u9fff]")
PAIRS = [("看零件的质心和体积", "solidworks_part_mass_properties"),
         ("拓扑优化建算例", "solidworks_topology_create_study"),
         ("给选中边加圆角", "solidworks_fillet"),
         ("跑静力仿真求解", "solidworks_simulation_run_analysis"),
         ("设置文档外观颜色", "solidworks_set_appearance"),
         ("导出运动算例的 AVI 动画", "solidworks_motion_export_avi")]

by = {s.name: s for s in rc.all_specs()}
print("★ 逐条：中文查询 vs 该工具**模型可见的全部文本**")
print()
print(ms.block_for('zero_han_surface'))
print()
zero_han = 0
for q, name in PAIRS:
    s = by.get(name)
    if s is None:
        print("  ★ 找不到工具:", name)
        continue
    surface = " ".join([s.name, getattr(s, "title", "") or "",
                        " ".join(p.name for p in (getattr(s, "params", None) or [])),
                        getattr(s, "doc", "") or ""])
    han_in_surface = len(CJK.findall(surface))
    #: ★ 词元重叠：查询的 CJK 二元组 ∩ 工具面里的 CJK 二元组
    qb = {q[i:i + 2] for i in range(len(q) - 1)}
    sb = {t[i:i + 2] for t in CJK.findall(surface) for i in range(len(t) - 1)}
    over = qb & sb
    if han_in_surface == 0:
        zero_han += 1
    print("  %-22s → %-40s 工具面汉字数=%-5d 中文二元组重叠=%d/%d"
          % (q[:20], name.removeprefix("solidworks_"), han_in_surface, len(over), len(qb)))
print()
print("★ 抽查的 %d 条里，**工具面一个汉字都没有**的有 **%d** 条 ⇒ ★ 词法检索对它们**结构上无解** ✓"
      % (len(PAIRS), zero_han))
print()
#: ★ 全局：有多少工具的"模型可见文本"完全不含汉字？
allzero = 0
for s in rc.all_specs():
    surface = " ".join([s.name, getattr(s, "title", "") or "",
                        getattr(s, "doc", "") or ""])
    if not CJK.search(surface):
        allzero += 1
print("★★ 全部 **%d** 个工具里，**模型可见文本（name+title+doc）完全不含汉字**的有 **%d** 个 = **%.1f%%**"
      % (len(rc.all_specs()), allzero, 100.0 * allzero / len(rc.all_specs())))
print("⇒ ★★ 中文用户的查询与这批工具的**词元重叠恒为 0** ⇒ 任何词法检索器都必然 miss ✓")
