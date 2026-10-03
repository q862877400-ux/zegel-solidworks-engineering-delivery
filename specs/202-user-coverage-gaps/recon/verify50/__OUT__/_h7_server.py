"""★ vd50-H 第七轮：server.py 侧的非 ToolSpec 导出（防"其实挂在 server 上"的假阳性）。"""
import re

t = open(r'D:/AI/SW/mcp-server/server.py', encoding='utf-8').read()
m = re.search(r'exports\s*=\s*\{(.*?)\n\s*\}', t, re.S)
print('FOUND_EXPORTS_DICT', bool(m))
if m:
    keys = re.findall(r'["\']([A-Za-z0-9_]+)["\']\s*:', m.group(1))
    print('N_EXPORTS', len(keys))
    for k in sorted(keys):
        print('  ', k)

print()
print('=== server.py 里是否出现下列能力名 ===')
for name in ['linear_pattern', 'curve_driven', 'table_driven', 'fill_pattern',
             'sketch_driven', 'intersect_curves', 'sketch_text', 'sketch_picture',
             'revolve_cut', 'split_open_segment', 'equation_spline',
             'projected_sketch', 'FeatureRevolveCut', 'InsertSketchText']:
    hit = [l.strip()[:120] for l in t.splitlines() if name.lower() in l.lower()]
    print(f'  {name:22s} -> {hit if hit else "0 命中"}')
