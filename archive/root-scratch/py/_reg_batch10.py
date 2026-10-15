import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\mcp-server\register_capabilities.py")
t = P.read_text(encoding="utf-8")
OLD = '''    "tool_specs_batch9",   # 轮 98：模具域「已实现 + 有测试 + 未暴露」的 3 个
)'''
NEW = '''    "tool_specs_batch9",   # 轮 98：模具域「已实现 + 有测试 + 未暴露」的 3 个
    "tool_specs_batch10",  # 轮 128：把轮 123~127 **查证并真机跑过**的 4 个高层入口接出去
)'''
assert OLD in t, "锚点不符"
P.write_text(t.replace(OLD, NEW, 1), encoding="utf-8")
ast.parse(P.read_text(encoding="utf-8"))
print("  ok BATCH_MODULES 已加 batch10")

# 同时更新模块头部的批次说明（如果有）
t2 = P.read_text(encoding="utf-8")
print("  现在 BATCH_MODULES 有 %d 项" % t2.count('"tool_specs_batch'))
