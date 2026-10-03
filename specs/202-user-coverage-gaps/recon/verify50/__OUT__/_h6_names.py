"""★ vd50-H 第六轮：列出仓内全部 ToolSpec 名（人工过目，防"换个名字其实有"）。"""
import re, glob

n = []
for f in sorted(glob.glob(r'D:/AI/SW/mcp-server/tool_specs_batch*.py')):
    t = open(f, encoding='utf-8').read()
    n += re.findall(r'name\s*=\s*["\']([A-Za-z0-9_]+)["\']', t)
n = sorted(set(n))
print('TOTAL_UNIQUE_TOOLNAMES', len(n))
for i in range(0, len(n), 3):
    print('  '.join(f'{x:40s}' for x in n[i:i + 3]))
