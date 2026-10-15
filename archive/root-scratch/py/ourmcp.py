import re, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
s = Path(r"C:\swprojects\sw-skill-fork\mcp-server\server.py").read_text(encoding="utf-8")
print("=== 我们的 MCP 两个关键机制 ===")
print("① 单位：参数名里有没有 mm/deg 后缀？")
mm = len(re.findall(r'_\w*mm\b|_mm\b', s)); deg = len(re.findall(r'_deg\b', s))
print("     _mm 出现 %d 次   _deg 出现 %d 次" % (mm, deg))
units = re.findall(r'METERS?|metres?|meters?|毫米|米\b', s[:4000])
print("     docstring 里的单位说明: %s" % (sorted(set(units))[:6] or "无"))
print()
print("② 选择：有没有声明式 selection（按索引选中）？")
for k in ("selection", "face_index", "edge_indices", "SelectByID2", "marks", "list_faces", "list_edges"):
    n = len(re.findall(re.escape(k), s))
    print("     %-16s %d 次" % (k, n))
print()
print("③ 视觉反馈：截图？")
for k in ("screenshot", "capture", "image", "Image"):
    print("     %-14s %d 次" % (k, len(re.findall(re.escape(k), s))))