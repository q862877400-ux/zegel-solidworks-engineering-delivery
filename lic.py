import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
for name, p in [("Eduardof0nt",r"C:\swprojects\Eduardof0nt"),
                ("andrewbartels1",r"C:\swprojects\andrewbartels1"),
                ("vespo92",r"C:\swprojects\SolidworksMCP-TS"),
                ("Slacker-LLC",r"C:\swprojects\Slacker-LLC")]:
    d = Path(p)
    print("=== %s ===" % name)
    # LICENSE 文件实际内容
    lic = None
    for f in list(d.glob("LICENSE*")) + list(d.glob("NOTICE*")) + list(d.glob("COPYING*")):
        head = f.read_text(encoding="utf-8", errors="ignore")[:400]
        kind = ("MIT" if "MIT License" in head or "Permission is hereby granted, free of charge" in head
                else "Apache-2.0" if "Apache License" in head
                else "GPL" if "GNU General" in head else "?")
        print("   %-14s -> %s" % (f.name, kind))
        if f.name.upper().startswith("LICENSE"): lic = kind
    if not lic: print("   ⚠ 无 LICENSE 文件")
    # 测试规模
    tests = [f for f in d.rglob("*") if f.is_file() and ("test" in f.name.lower() or "test" in str(f.parent).lower())
             and f.suffix in (".py",".ts") and ".venv" not in str(f) and "node_modules" not in str(f)]
    live = [f for f in tests if "live" in f.name.lower() or "real" in f.name.lower()]
    print("   测试文件 %d 个（其中 live/real %d 个）" % (len(tests), len(live)))
    print()