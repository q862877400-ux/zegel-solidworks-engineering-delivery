"""★ vd50-H 索引脚本：抽仓内工具名 + 官方成员名 两份清单。"""
import re, glob, json, os

OUT = r'D:/AI/SW/specs/202-user-coverage-gaps/recon/verify50/__OUT__'

# ① 仓内工具名（只读 mcp-server/tool_specs_batch*.py）
tools = {}
for f in sorted(glob.glob(r'D:/AI/SW/mcp-server/tool_specs_batch*.py')):
    t = open(f, encoding='utf-8').read()
    for m in re.finditer(r'name\s*=\s*["\']([A-Za-z0-9_]+)["\']', t):
        tools.setdefault(m.group(1), []).append(os.path.basename(f))

# ② 官方成员名（只读 C:/swapi/types/*/*.md）
members = {}
for p in glob.glob(r'C:/swapi/types/*/*.md'):
    b = os.path.basename(p)[:-3]
    members.setdefault(b, []).append(os.path.basename(os.path.dirname(p)))

json.dump(tools, open(os.path.join(OUT, '_tools.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=0)
json.dump(members, open(os.path.join(OUT, '_official.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=0)

print('N_TOOLS', len(tools))
print('N_OFFICIAL_MEMBER_MD', len(members))
