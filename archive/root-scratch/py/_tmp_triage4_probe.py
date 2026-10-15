"""临时只读脚本：找出反射转储里 design-table 成员归属哪个接口（用完即删）。"""
import re

P = r"D:\AI\SW\scripts\sw_api_sldworks.py"
src = open(P, encoding="utf-8").read().splitlines()
cur = None
pat = re.compile(
    r"'(GetDesignTable|IGetDesignTable|HasDesignTable|InsertFamilyTableOpen|"
    r"InsertFamilyTableNew|InsertFamilyTableEdit|CloseFamilyTable|DeleteDesignTable)'"
)
for i, l in enumerate(src, 1):
    m = re.match(r"^\s{0,8}'([A-Za-z_0-9]+)':\s*\{", l)
    if m:
        cur = m.group(1)
    if pat.search(l):
        print(i, "iface=", cur, "->", l.strip())
