import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

# ① 已知事实 72
K = Path(r"D:\AI\SW\docs\known-facts.md")
tk = K.read_text(encoding="utf-8")
ADD = """

| # | 事实 | 依据 |
|---|---|---|
| 72 | **MCP 协议层里，工具的入参 schema 是「**嵌在 `params` 对象里**」的，不是展平的；且框架会统一补一个 `response_format`** —— 2026-10-01（轮 129）起 server 发 `tools/list` 实测：`inputSchema.properties` **只有 `params`**（一个 `$ref`），真正的参数在 `inputSchema.$defs.<ModelName>.properties` 里，模型名由工具名驼峰化得到（`solidworks_hole_standards` ⇒ `SolidworksHoleStandardsInput`）。★ 而且**框架自动补**了一个 `response_format`（枚举 `json`/`markdown`，**也是 `$ref`** ⇒ 枚举在 `$defs.ResponseFormat`）—— 声明里**没有**它。⚠⚠ **我第一版判据爬错了两层**：先在**顶层**找展平参数名（报「协议里只有一个 `params`」），再在 `inner["response_format"]` 找 `enum`（它是个 `$ref`）⇒ ★ **不是缺陷，是查错了地方**。★ 同轮实测：协议层 **86 个工具**（这补上了 `047` 说的「总暴露数没有重新统计」） | `tools/verify_mcp_protocol_layer.py`（7/7）；`tests/test_mcp_protocol_layer.py`（4 条，**起 server 但一次工具都不调** ⇒ 不碰 COM，符合已知事实 24）；`_dump_tool_schema.py`（原样打印 schema）|
"""
if "嵌在 `params` 对象里" not in tk:
    K.write_text(tk.rstrip() + ADD, encoding="utf-8")
    print("  ok known-facts 已加 72")
else:
    print("  已有 72")

# ② 更新 harvest-report 里的总暴露数（若写着 83）
H = Path(r"C:\swprojects\sw-skill-fork\docs\harvest-report.md")
th = H.read_text(encoding="utf-8")
import re
hits = re.findall(r"(暴露|工具)[^\n]{0,40}?\b(\d{2,3})\s*(?:个|条)", th)
print("  harvest-report 里疑似暴露数的行:")
for m in re.finditer(r"(?m)^.*(暴露|工具数|工具)[^\n]*\d{2,3}[^\n]*$", th):
    print("    %s" % m.group(0).strip()[:100])
