import re, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
s = Path(r"C:\swprojects\sw-skill-fork\mcp-server\server.py").read_text(encoding="utf-8")
print("=== ① 工具声明质量 ===")
blocks = re.findall(r'@mcp\.tool\((.*?)\)\s*\ndef\s+(\w+)', s, re.S)
print("  @mcp.tool 块 %d 个" % len(blocks))
ann = sum(1 for b,_ in blocks if "annotations" in b)
ttl = sum(1 for b,_ in blocks if "title=" in b)
print("  带 annotations: %d/%d   带 title: %d/%d" % (ann, len(blocks), ttl, len(blocks)))
print()
print("=== ② 护栏（安全设计）===")
guards = ["_run_locked", "input_path_must_exist", "formats_must_be_whitelisted",
          "process_must_be_whitelisted", "solver_must_be_whitelisted",
          "output_path_must_be_json", "_active_part_required", "_coinitialize"]
for g in guards:
    n = len(re.findall(r'\b%s\b' % g, s))
    print("  %-32s 出现 %d 次" % (g, n))
print()
print("=== ③ 类型化入参（Pydantic）===")
models = re.findall(r'class\s+(\w+Input)\b', s)
print("  输入模型 %d 个: %s" % (len(models), models[:6]))
print()
print("=== ④ 错误处理 ===")
for k in ("_tool_error", "try:", "except ", "raise "):
    print("  %-14s %d 次" % (k, len(re.findall(re.escape(k), s))))
print()
print("=== ⑤ HTTP 传输（本地 stdio 之外的能力）===")
for k in ("stdio", "sse", "streamable", "FastMCP", "run("):
    print("  %-12s %s" % (k, "有" if k in s else "—"))