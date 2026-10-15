import re, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"C:\swprojects\sw-skill-fork")
names = set()
srv = (R / "mcp-server" / "server.py").read_text(encoding="utf-8", errors="ignore")
names |= set(re.findall(r'@mcp\.tool\(\s*\n?\s*name\s*=\s*"([^"]+)"', srv))
for p in (R / "mcp-server").glob("tool_specs_*.py"):
    names |= set(re.findall(r'name="((?:solidworks|cadstudio)_[\w]+)"',
                            p.read_text(encoding="utf-8", errors="ignore")))
asm = sorted(n for n in names if any(k in n for k in
             ("mate", "component", "assembly", "explode", "interference", "joint")))
print("现有装配相关 MCP 工具 %d 个:" % len(asm))
for n in asm:
    print("   %s" % n)
print("全部工具 %d 个" % len(names))

print()
print("装配函数在 tool_specs 里被 function= 引用的:")
t = "".join(p.read_text(encoding="utf-8", errors="ignore")
            for p in (R / "mcp-server").glob("tool_specs_*.py"))
for f in ("add_component", "add_mate_coincident", "add_mate_concentric", "add_mate_distance",
          "add_mate_parallel", "add_concentric_mate_by_cylinders", "add_gear_mate_by_cylinders",
          "add_revolute_joint_by_cylinders", "suppress_component", "unsuppress_component",
          "replace_component", "get_interference_detection", "add_mate", "suppress_mate",
          "fix_component", "get_components", "apply_component_transform_x"):
    hit = ('function="%s"' % f) in t
    tests = sum(1 for p in (R / "tests").glob("*.py")
                if re.search(r"\b%s\b" % re.escape(f), p.read_text(encoding="utf-8", errors="ignore")))
    print("   %-34s 已暴露=%-5s 测试文件 %d 个" % (f, "是" if hit else "**否**", tests))
