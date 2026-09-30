import re, sys, io
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
txt = Path(r"D:\AI\SW\_raw\enum_values_sldworks.txt").read_text(encoding="utf-8")
blocks, cur = {}, None
for l in txt.splitlines():
    if l.startswith("## "):
        cur = l[3:].strip(); blocks[cur] = []
    elif cur and l.strip():
        m = re.match(r"(\w+)\s*=\s*(-?\d+)", l.strip())
        if m: blocks[cur].append((m.group(1), int(m.group(2))))
# 只要与本模块相关的枚举
WANT = ["swDocumentTypes_e", "swUserPreferenceStringValue_e", "swUserPreferenceIntegerValue_e",
        "swUserPreferenceToggle_e", "swUserPreferenceDoubleValue_e", "swOpenDocOptions_e",
        "swSaveAsOptions_e", "swSaveAsVersion_e", "swFrameState_e", "swSelectType_e"]
out = []
for name in WANT:
    items = blocks.get(name)
    if not items:
        out.append((name, None)); continue
    out.append((name, items))
for name, items in out:
    print("%-36s %s" % (name, ("%d 项" % len(items)) if items else "** 缺 **"))
Path(r"D:\AI\SW\_enum_pick.json").write_text(
    __import__("json").dumps({k: v for k, v in out if v}, ensure_ascii=False),
    encoding="utf-8")
print("已存 D:\\AI\\SW\\_enum_pick.json")
