import sys, io, importlib.util
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
spec = importlib.util.spec_from_file_location("tbi", r"C:\swprojects\sw-skill-fork\scripts\sw_toolbox_index.py")
m = importlib.util.module_from_spec(spec); sys.modules["tbi"]=m; spec.loader.exec_module(m)
print("  19 套标准，前 6:", list(m.list_standards().items())[:6])
print()
print("  搜 'ball bearing' (GB):", len(m.search("ball bearing", standard="GB")), "条")
for h in m.search("ball bearing", standard="GB")[:2]:
    print("     %-52s %s" % (h["part"], h["path"][-58:]))
print()
print("  搜 'hex head' (Ansi Inch):", len(m.search("hex head", standard="Ansi Inch")), "条")
p = m.part_path("GB", m.search("ball", standard="GB")[0]["part"])
print()
print("  part_path 示例:", p[-70:])
print()
for kw in ("ball screw", "linear guide", "profile 4040", "Φ20"):
    print("  搜 %-14s -> %d 条" % (kw, len(m.search(kw))))
try:
    m.part_path("GB", "不存在的零件")
    print("  [FAIL] 查不到未抛错")
except KeyError as e:
    print("  查不到已抛错，提示:", str(e).splitlines()[0][:56])