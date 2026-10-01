import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

led = Path(r"C:\swprojects\sw-skill-fork\docs\obsolete-member-candidates.md").read_text(encoding="utf-8")
print("══ 台账里「官方标了废弃」的实例（证明 API 面**确实**在版本间移动）══")
seg = led[led.index("### ⚠ 已核实**为真**"):]
for m in re.finditer(r"(?m)^\|\s*`?(\w+)`?\s*\|([^|]*)\|([^|]*)\|([^|]*)\|", seg):
    a, b, c, dd = (x.strip() for x in m.groups())
    if a.startswith("-") or a == "成员":
        continue
    print("  %-24s 废弃接口:%-26s 后继: %s" % (a, b[:26], dd[:44]))
print()
print("══ 官方 Remarks 里**明写版本**的约束（最硬的版本依赖证据）══")
import subprocess
for f in (r"C:\swapi\types\IGtol\SetFrameSymbols2.md",
          r"C:\swapi\types\IGtolFrame\SetSymbolXml.md",
          r"C:\swapi\types\IGtol\ConvertFormat.md",
          r"C:\swapi\types\IGtol\AddFrame.md"):
    p = Path(f)
    if p.is_file():
        t = p.read_text(encoding="utf-8", errors="replace")
        for m in re.finditer(r"(?m)^.*(earlier than 2022|2022 or later|2022 format|SOLIDWORKS 2022).*$", t):
            print("  %-38s %s" % (p.stem, m.group(0).strip()[:96]))
