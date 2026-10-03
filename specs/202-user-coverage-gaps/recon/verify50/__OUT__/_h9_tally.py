"""★ vd50-H 终计：核对口径与计数。"""
import re, json, os

ENUM = r'C:/swapi/enums/swCommands_e.md'
rows = []
for l in open(ENUM, encoding='utf-8'):
    m = re.match(r'\|\s*(swCommand\w+)\s*\|\s*(.*?)\s*\|\s*$', l)
    if m and re.search(r'Sketch toolbar|Sketch Tools|Features toolbar', m.group(2)):
        rows.append(m.group(1))

rep = json.load(open(r'D:/AI/SW/specs/202-user-coverage-gaps/recon/verify50/__OUT__/_h1_report.json',
                     encoding='utf-8'))
print('ENUM_TOTAL_MEMBERS        :', 2204)
print('本片命令数(草图+特征工具条) :', len(rows))
print('其中 草图工具条            :', sum(1 for l in open(ENUM, encoding='utf-8')
      if re.search(r'Sketch toolbar|Sketch Tools', l) and re.match(r'\|\s*swCommand', l)))
print('其中 特征工具条            :', sum(1 for l in open(ENUM, encoding='utf-8')
      if re.search(r'Features toolbar', l) and re.match(r'\|\s*swCommand', l)))
print('逐条三向核过的命令数       :', len(rep))
print('  ├ 有官方参数化成员+有工具 :', sum(1 for r in rep if r['api_hit'] and r['tool_hit']))
print('  ├ 有官方参数化成员+无工具 :', sum(1 for r in rep if r['api_hit'] and not r['tool_hit']))
print('  └ 查不到官方参数化成员    :', sum(1 for r in rep if not r['api_hit']))
