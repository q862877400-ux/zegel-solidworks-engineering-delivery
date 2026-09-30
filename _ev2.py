import re, sys, io
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
txt = Path(r"D:\AI\SW\_raw\enum_values_sldworks.txt").read_text(encoding="utf-8")
blocks = {}
cur = None
for l in txt.splitlines():
    if l.startswith("## "):
        cur = l[3:].strip(); blocks[cur] = []
    elif cur and l.strip():
        blocks[cur].append(l.strip())
print("总枚举数 =", len(blocks))
for name in ("swDocumentTypes_e", "swOpenDocOptions_e"):
    print("\n###", name)
    for l in blocks.get(name, [])[:9]: print("   ", l)
print("\n### swUserPreferenceStringValue_e —— 路径/模板相关")
pat = re.compile(r"swDocumentsDirectory|swExtDocumentsDir|swDefaultTemplate|swSaveAsDirectory|swExportDirectory|swBackupDirectory|swAutoSaveDirectory|swTempDirectory|swSaveAsFilename")
for l in blocks["swUserPreferenceStringValue_e"]:
    if pat.search(l): print("   ", l)
print("\n### swUserPreferenceToggle_e —— 与选择/网格相关")
pat2 = re.compile(r"swInputDimValOnCreate|swExtLoadModelFromWeb|swWarnOnSave|swSelRestrictToSelect")
for l in blocks["swUserPreferenceToggle_e"]:
    if pat2.search(l): print("   ", l)
print("\n### swUserPreferenceIntegerValue_e —— 与网格/单位相关")
pat3 = re.compile(r"swMeshQuality|swDefaultTemplatePart|swDefaultTemplateAssembly|swDefaultTemplateDrawing|swDefaultUnitSystem")
for l in blocks["swUserPreferenceIntegerValue_e"]:
    if pat3.search(l): print("   ", l)
