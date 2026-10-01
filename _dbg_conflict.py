import importlib.util, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
spec = importlib.util.spec_from_file_location(
    "_g", r"C:\swprojects\sw-skill-fork\scripts\check_enum_values_vs_reflection.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

ref, owner = m.parse_dump(m.DUMP)
mem = "swSketchChamfer_DistanceDistance"
print("  在转储里: %s  值=%s  所属枚举=%s" % (mem in ref, ref.get(mem), owner.get(mem)))
rows = m.parse_code()
mine = [r for r in rows if r[4] == mem]
print("  代码里的行: %s" % mine)
en = owner.get(mem, "")
print("  准备查的枚举: %r" % en)
sw = m.parse_swapi(en) if en else {}
print("  swapi 表里: %s 值=%s" % (mem in sw, sw.get(mem)))
print("  swapi 表条目数: %d" % len(sw))
if sw:
    print("  前 3 个键: %s" % list(sw.items())[:3])
