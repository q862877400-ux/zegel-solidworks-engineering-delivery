import re, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"C:\swprojects\sw-skill-fork")
srv = (R / "mcp-server" / "server.py").read_text(encoding="utf-8", errors="ignore")
disp = {f for _, f in re.findall(r'"(\w+)":\s*[A-Za-z_]\w*\.(\w+)\s*,', srv)}
spec = set()
for p in (R / "mcp-server").glob("tool_specs_*.py"):
    spec |= set(re.findall(r'function="([\w]+)"', p.read_text(encoding="utf-8", errors="ignore")))
exposed = disp | spec
for n in ("insert_core_cavity_solids", "insert_parting_line", "insert_parting_surface",
          "insert_shut_off_surface", "mold_evidence", "mold_draft_analysis", "mold_undercut_detect"):
    tests = sum(1 for p in (R / "tests").glob("*.py")
                if re.search(r"\b%s\b" % re.escape(n), p.read_text(encoding="utf-8", errors="ignore")))
    print("  %-30s 已暴露=%-5s 测试文件 %d" % (n, "是" if n in exposed else "**否**", tests))
print()
print("  外部缺口操作 tooling_split 对应的官方成员: InsertMoldCoreCavitySolids / CoreCavitySplit")
